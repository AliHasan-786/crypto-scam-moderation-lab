/*
 * Live Radar — the visitor's browser connects to the public Bluesky
 * Jetstream firehose and scores real posts with the same deterministic
 * policy scorer used in Test Post (scoreText in app.js).
 *
 * Privacy design (Decision Log 011): every post is scored in memory and
 * immediately discarded. No text, handle, DID, or URI is stored, displayed,
 * or transmitted anywhere — the socket is a read-only public feed, scoring
 * happens client-side, and only aggregate counters ever reach the DOM.
 * The radar never labels, reports, or takes any action on any account.
 */

let deps = { scoreText: null, calibration: null };

const JETSTREAM_URL =
  "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post";
const SCORED_LANGS = new Set(["en", "es"]);
const HISTOGRAM_BINS = 10;

const radar = {
  socket: null,
  status: "idle", // idle | connecting | live | error
  startedAt: null,
  observed: 0,
  scored: 0,
  otherLanguage: 0,
  peakPerSecond: 0,
  recentTimestamps: [],
  histogram: new Array(HISTOGRAM_BINS).fill(0),
  tierCounts: {},
  ruleCounts: {},
  timer: null,
};

function reset() {
  radar.startedAt = Date.now();
  radar.observed = 0;
  radar.scored = 0;
  radar.otherLanguage = 0;
  radar.peakPerSecond = 0;
  radar.recentTimestamps = [];
  radar.histogram = new Array(HISTOGRAM_BINS).fill(0);
  radar.tierCounts = {};
  radar.ruleCounts = {};
}

function connect() {
  if (radar.socket) return;
  reset();
  radar.status = "connecting";
  syncDom();
  let socket;
  try {
    socket = new WebSocket(JETSTREAM_URL);
  } catch (error) {
    radar.status = "error";
    syncDom();
    return;
  }
  radar.socket = socket;
  socket.onopen = () => {
    radar.status = "live";
    syncDom();
  };
  socket.onmessage = (message) => {
    let event;
    try {
      event = JSON.parse(message.data);
    } catch (error) {
      return;
    }
    const commit = event && event.commit;
    if (!commit || event.kind !== "commit" || commit.operation !== "create") return;
    const record = commit.record || {};
    const text = typeof record.text === "string" ? record.text.trim() : "";
    if (!text) return;

    radar.observed += 1;
    const now = Date.now();
    radar.recentTimestamps.push(now);

    const langs = Array.isArray(record.langs) && record.langs.length ? record.langs : ["und"];
    const primary = String(langs[0] || "und").split("-")[0].toLowerCase();
    if (!SCORED_LANGS.has(primary)) {
      radar.otherLanguage += 1;
      return;
    }

    // Score in memory; the text goes out of scope right after.
    const result = typeof deps.scoreText === "function" ? deps.scoreText(text) : null;
    if (!result) return;
    radar.scored += 1;
    const bin = Math.min(HISTOGRAM_BINS - 1, Math.floor(result.score * HISTOGRAM_BINS));
    radar.histogram[bin] += 1;
    radar.tierCounts[result.action] = (radar.tierCounts[result.action] || 0) + 1;
    (result.ruleResults || []).forEach((rule) => {
      if (rule.matched) {
        radar.ruleCounts[rule.label || rule.name] =
          (radar.ruleCounts[rule.label || rule.name] || 0) + 1;
      }
    });
  };
  socket.onerror = () => {
    radar.status = "error";
    syncDom();
  };
  socket.onclose = () => {
    radar.socket = null;
    if (radar.status !== "error") radar.status = "idle";
    syncDom();
  };
}

function disconnect() {
  if (radar.socket) {
    radar.status = "idle";
    radar.socket.close();
    radar.socket = null;
  }
  syncDom();
}

function postsPerSecond() {
  const cutoff = Date.now() - 10000;
  radar.recentTimestamps = radar.recentTimestamps.filter((t) => t >= cutoff);
  const rate = radar.recentTimestamps.length / 10;
  if (rate > radar.peakPerSecond) radar.peakPerSecond = rate;
  return rate;
}

function elapsedLabel() {
  if (!radar.startedAt || radar.status === "idle") return "0:00";
  const seconds = Math.floor((Date.now() - radar.startedAt) / 1000);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

function formatCount(value) {
  return value.toLocaleString("en-US");
}

function calibration() {
  return deps.calibration || null;
}

function renderShell() {
  const cal = calibration();
  const statusLabel = {
    idle: "Not connected",
    connecting: "Connecting to firehose...",
    live: "LIVE — scoring real posts in your browser",
    error: "Connection failed (network or firewall). Nothing was sent anywhere.",
  }[radar.status];

  return `
    <div class="module-grid single-column">
      <section class="panel radar-panel" aria-label="Live firehose radar">
        <div class="radar-topline">
          <span class="radar-status ${radar.status}">
            <i></i>${statusLabel}
          </span>
          <div class="radar-actions">
            <button type="button" class="radar-connect" data-radar-action="connect" ${
              radar.status === "live" || radar.status === "connecting" ? "disabled" : ""
            }>Connect to live firehose</button>
            <button type="button" class="radar-disconnect" data-radar-action="disconnect" ${
              radar.status === "live" || radar.status === "connecting" ? "" : "disabled"
            }>Disconnect</button>
          </div>
        </div>

        <div class="caveat-banner">
          <strong>What this is:</strong> your browser connects directly to Bluesky's public
          Jetstream firehose and runs the same deterministic policy scorer as Test Post over
          real posts, live. Aggregates only — no post text, handle, or identifier is stored,
          displayed, or sent anywhere, and the radar can take no action on any account
          (Decision Log 008 and 011). The full ML baseline and human-review pipeline run in
          the repo, not in this preview.
        </div>

        <div class="radar-counters">
          <div><strong id="radar-observed">0</strong><span>posts observed</span></div>
          <div><strong id="radar-scored">0</strong><span>scored (EN/ES)</span></div>
          <div><strong id="radar-rate">0.0</strong><span>posts/sec (10s window)</span></div>
          <div><strong id="radar-peak">0.0</strong><span>peak posts/sec</span></div>
          <div><strong id="radar-elapsed">0:00</strong><span>session time</span></div>
          <div><strong id="radar-review">0</strong><span>review-band hits</span></div>
        </div>

        <div class="radar-columns">
          <div>
            <h3>Score distribution (this session)</h3>
            <div class="radar-histogram" id="radar-histogram" role="img"
              aria-label="Histogram of policy scores for posts scored this session"></div>
            <p class="radar-note">
              Real traffic is overwhelmingly low-score — that asymmetry is the whole
              moderation problem: the interesting band is tiny, and every threshold
              shift moves a payroll number (see Scale &amp; Capacity).
            </p>
          </div>
          <div>
            <h3>Decision tiers (this session)</h3>
            <div class="radar-tiers" id="radar-tiers"></div>
            <h3>Top matched rules</h3>
            <div class="radar-rules" id="radar-rules"></div>
          </div>
        </div>
      </section>

      ${
        cal
          ? `
      <section class="panel radar-panel" aria-label="Offline stream calibration">
        <h3>Pipeline calibration on real traffic (full ML model, offline)</h3>
        <p class="radar-note">
          The repo pipeline ran the complete model — TF-IDF + policy features + decision
          layer — over <strong>${formatCount(cal.window.postsScored)}</strong> real posts
          sampled from <strong>${formatCount(cal.window.postsObserved)}</strong> observed in
          ${Math.round(cal.window.seconds)}s of firehose on ${cal.generatedAt}. Aggregates
          only, same privacy rule as this radar.
        </p>
        <div class="radar-counters">
          <div><strong>${(
            (cal.decisionTierShares.send_to_human_review || { share: 0 }).share * 100
          ).toFixed(2)}%</strong><span>review-tier share of live traffic</span></div>
          <div><strong>${cal.modelScore.p99.toFixed(2)}</strong><span>p99 model score</span></div>
          <div><strong>${cal.modelScore.p50.toFixed(2)}</strong><span>median model score</span></div>
          <div><strong>${formatCount(
            (cal.decisionTierShares.no_label || { count: 0 }).count
          )}</strong><span>no-action posts</span></div>
        </div>
        <p class="radar-note">${cal.interpretation}</p>
      </section>`
          : ""
      }
    </div>
  `;
}

function syncDom() {
  const activeRadar = document.querySelector('[data-active-module="radar"]');
  if (!activeRadar) return;

  const statusHost = activeRadar.querySelector(".radar-status");
  if (statusHost) {
    // Re-render the whole shell only on status transitions.
    const moduleContent = document.querySelector('[data-active-module="radar"]');
    const currentStatus = statusHost.classList.contains(radar.status);
    if (!currentStatus) {
      moduleContent.innerHTML = renderShell();
      attach();
    }
  }

  const set = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  };
  set("radar-observed", formatCount(radar.observed));
  set("radar-scored", formatCount(radar.scored));
  set("radar-rate", postsPerSecond().toFixed(1));
  set("radar-peak", radar.peakPerSecond.toFixed(1));
  set("radar-elapsed", elapsedLabel());
  const reviewBand =
    (radar.tierCounts["Human review queue"] || 0) +
    (radar.tierCounts["Potential Crypto Fraud label"] || 0) +
    (radar.tierCounts["Interstitial plus downrank"] || 0) +
    (radar.tierCounts["Block pending reviewer confirmation"] || 0);
  set("radar-review", formatCount(reviewBand));

  const histogramHost = document.getElementById("radar-histogram");
  if (histogramHost) {
    const max = Math.max(1, ...radar.histogram);
    histogramHost.innerHTML = radar.histogram
      .map((count, index) => {
        const height = Math.max(2, Math.round((count / max) * 100));
        const low = (index / HISTOGRAM_BINS).toFixed(1);
        return `<div class="radar-bar" title="${low}s: ${formatCount(count)} posts">
            <i style="height:${height}%"></i><span>${low}</span>
          </div>`;
      })
      .join("");
  }

  const tiersHost = document.getElementById("radar-tiers");
  if (tiersHost) {
    const entries = Object.entries(radar.tierCounts).sort((a, b) => b[1] - a[1]);
    tiersHost.innerHTML = entries.length
      ? entries
          .map(
            ([tier, count]) =>
              `<div class="radar-tier-row"><span>${tier}</span><b>${formatCount(count)}</b></div>`,
          )
          .join("")
      : '<p class="radar-note">Connect to start counting.</p>';
  }

  const rulesHost = document.getElementById("radar-rules");
  if (rulesHost) {
    const entries = Object.entries(radar.ruleCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
    rulesHost.innerHTML = entries.length
      ? entries
          .map(
            ([rule, count]) =>
              `<div class="radar-tier-row"><span>${rule}</span><b>${formatCount(count)}</b></div>`,
          )
          .join("")
      : '<p class="radar-note">No policy rules matched yet.</p>';
  }
}

function attach() {
  document.querySelectorAll("[data-radar-action]").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.radarAction === "connect") connect();
      else disconnect();
    });
  });
  if (!radar.timer) {
    radar.timer = setInterval(() => {
      if (radar.status === "live") syncDom();
    }, 1000);
  }
}

export const LiveRadar = {
configure(next) {
  deps = { ...deps, ...next };
},
renderShell,
attach,
connect,
disconnect,
state: radar,
};
