const JETSTREAM_URL =
  "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post";
const SCORED_LANGUAGES = new Set(["en", "es"]);
const SESSION_LIMIT_MS = 10 * 60 * 1000;
const MAX_SCORED_POSTS = 5000;
const BIN_COUNT = 10;

let scoreText = null;
let timer = null;
const radar = {
  socket: null,
  status: "idle",
  startedAt: null,
  observed: 0,
  scored: 0,
  skippedLanguage: 0,
  queued: 0,
  recent: [],
  histogram: Array(BIN_COUNT).fill(0),
  tiers: {},
  rules: {},
};

function reset() {
  Object.assign(radar, {
    startedAt: Date.now(), observed: 0, scored: 0, skippedLanguage: 0, queued: 0,
    recent: [], histogram: Array(BIN_COUNT).fill(0), tiers: {}, rules: {},
  });
}

function disconnect(reason = "idle") {
  radar.status = reason;
  if (radar.socket) radar.socket.close();
  radar.socket = null;
  sync();
}

function connect() {
  if (radar.socket || typeof scoreText !== "function") return;
  reset();
  radar.status = "connecting";
  sync();
  try {
    radar.socket = new WebSocket(JETSTREAM_URL);
  } catch {
    radar.status = "error";
    sync();
    return;
  }
  radar.socket.onopen = () => { radar.status = "live"; sync(); };
  radar.socket.onerror = () => { radar.status = "error"; sync(); };
  radar.socket.onclose = () => {
    radar.socket = null;
    if (radar.status === "live" || radar.status === "connecting") radar.status = "idle";
    sync();
  };
  radar.socket.onmessage = ({ data }) => {
    if (Date.now() - radar.startedAt >= SESSION_LIMIT_MS || radar.scored >= MAX_SCORED_POSTS) {
      disconnect("capped");
      return;
    }
    let event;
    try { event = JSON.parse(data); } catch { return; }
    const commit = event?.commit;
    if (event?.kind !== "commit" || commit?.operation !== "create") return;
    const record = commit.record || {};
    const text = typeof record.text === "string" ? record.text.trim() : "";
    if (!text) return;
    radar.observed += 1;
    radar.recent.push(Date.now());
    const primaryLanguage = String(record.langs?.[0] || "und").split("-")[0].toLowerCase();
    if (!SCORED_LANGUAGES.has(primaryLanguage)) { radar.skippedLanguage += 1; return; }

    // `text` is only used for this synchronous local score, then discarded.
    const result = scoreText(text);
    radar.scored += 1;
    const bin = Math.min(BIN_COUNT - 1, Math.floor(result.score * BIN_COUNT));
    radar.histogram[bin] += 1;
    radar.tiers[result.action] = (radar.tiers[result.action] || 0) + 1;
    if (result.action !== "No label") radar.queued += 1;
    for (const rule of result.ruleResults || []) {
      if (rule.matched) radar.rules[rule.label] = (radar.rules[rule.label] || 0) + 1;
    }
  };
}

function count(value) { return Number(value).toLocaleString("en-US"); }
function percent(value) { return `${(value * 100).toFixed(2)}%`; }

function rate() {
  const floor = Date.now() - 10000;
  radar.recent = radar.recent.filter((time) => time >= floor);
  return radar.recent.length / 10;
}

function elapsed() {
  if (!radar.startedAt) return "0:00";
  const seconds = Math.floor((Date.now() - radar.startedAt) / 1000);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

function statusCopy() {
  return {
    idle: "Not connected",
    connecting: "Connecting directly to the public relay…",
    live: "Live in this browser",
    capped: "Session cap reached; disconnected",
    error: "Connection failed; no data was retained",
  }[radar.status];
}

function rows(items, empty) {
  const entries = Object.entries(items).sort((a, b) => b[1] - a[1]).slice(0, 5);
  return entries.length
    ? entries.map(([label, value]) => `<div><span>${label}</span><b>${count(value)}</b></div>`).join("")
    : `<p>${empty}</p>`;
}

export function configureLiveRadar(nextScoreText) { scoreText = nextScoreText; }

export function renderLiveRadar(calibration) {
  return `
    <section class="live-radar" data-live-radar aria-labelledby="radar-title">
      <div class="live-radar-heading">
        <div>
          <span class="section-label">Optional live view</span>
          <h3 id="radar-title">Watch the boundary meet a public stream.</h3>
        </div>
        <span class="radar-status ${radar.status}" data-radar-status>${statusCopy()}</span>
      </div>
      <p class="live-radar-intro">
        This browser can read public Bluesky post events and count how the local rubric routes them.
        It never displays, saves, or sends post text, accounts, identifiers, or decisions anywhere.
      </p>
      <div class="radar-actions">
        <button type="button" data-radar-action="connect" ${radar.status === "live" || radar.status === "connecting" ? "disabled" : ""}>Connect</button>
        <button type="button" data-radar-action="disconnect" ${radar.socket ? "" : "disabled"}>Disconnect</button>
      </div>
      <div class="radar-stats" aria-live="polite">
        <div><strong data-radar-observed>${count(radar.observed)}</strong><span>non-empty posts observed</span></div>
        <div><strong data-radar-scored>${count(radar.scored)}</strong><span>scored locally (EN/ES)</span></div>
        <div><strong data-radar-queue>${count(radar.queued)}</strong><span>human-operated routes</span></div>
        <div><strong data-radar-rate>${rate().toFixed(1)}</strong><span>posts/sec, 10s window</span></div>
        <div><strong data-radar-time>${elapsed()}</strong><span>session time</span></div>
      </div>
      <div class="radar-detail-grid">
        <div>
          <h4>Local score distribution</h4>
          <div class="radar-histogram" data-radar-histogram></div>
        </div>
        <div class="radar-list"><h4>Routing counts</h4><div data-radar-tiers>${rows(radar.tiers, "Connect to start counting.")}</div></div>
        <div class="radar-list"><h4>Matched evidence</h4><div data-radar-rules>${rows(radar.rules, "No rule matches yet.")}</div></div>
      </div>
      <p class="radar-limit">Hard cap: ${MAX_SCORED_POSTS.toLocaleString()} scored posts or 10 minutes. This browser stores no stream records; counters reset on the next connection or page load.</p>
      <aside class="calibration-note">
        <span>Historic calibration</span>
        <p>${calibration.scope} On ${calibration.generatedAt}, ${count(calibration.window.postsScored)} posts were scored from ${count(calibration.window.nonEmptyPostsObserved)} non-empty posts observed. The intermediate-review share was <b>${percent(calibration.routing.intermediateReview.share)}</b>; the human-operated queue share was <b>${percent(calibration.routing.humanOperatedQueue.share)}</b>.</p>
      </aside>
    </section>
  `;
}

export function attachLiveRadar() {
  document.querySelectorAll("[data-radar-action]").forEach((button) => {
    button.addEventListener("click", () => button.dataset.radarAction === "connect" ? connect() : disconnect());
  });
  if (!timer) timer = window.setInterval(() => { if (radar.status === "live") sync(); }, 1000);
  sync();
}

function sync() {
  const root = document.querySelector("[data-live-radar]");
  if (!root) return;
  const set = (selector, value) => { const el = root.querySelector(selector); if (el) el.textContent = value; };
  const status = root.querySelector("[data-radar-status]");
  if (status) {
    status.textContent = statusCopy();
    status.className = `radar-status ${radar.status}`;
  }
  const connectButton = root.querySelector('[data-radar-action="connect"]');
  const disconnectButton = root.querySelector('[data-radar-action="disconnect"]');
  if (connectButton) connectButton.disabled = radar.status === "live" || radar.status === "connecting";
  if (disconnectButton) disconnectButton.disabled = !radar.socket;
  set("[data-radar-observed]", count(radar.observed));
  set("[data-radar-scored]", count(radar.scored));
  set("[data-radar-queue]", count(radar.queued));
  set("[data-radar-rate]", rate().toFixed(1));
  set("[data-radar-time]", elapsed());
  const max = Math.max(...radar.histogram, 1);
  const histogram = root.querySelector("[data-radar-histogram]");
  if (histogram) histogram.innerHTML = radar.histogram.map((value, index) => `<i title="${index / BIN_COUNT}-${(index + 1) / BIN_COUNT}: ${count(value)}" style="height:${Math.max(3, Math.round((value / max) * 100))}%"></i>`).join("");
  const tiers = root.querySelector("[data-radar-tiers]");
  if (tiers) tiers.innerHTML = rows(radar.tiers, "Connect to start counting.");
  const rules = root.querySelector("[data-radar-rules]");
  if (rules) rules.innerHTML = rows(radar.rules, "No rule matches yet.");
}

export function stopLiveRadar() { if (radar.socket) disconnect(); }
