import { posts } from "./data/posts.js";
import { evalSummary } from "./data/evalSummary.js";
import { liveReviewQueue } from "./data/liveReviewQueue.js";
import { campaignGraph } from "./data/campaignGraph.js";
import { adversarialLab } from "./data/adversarialLab.js";
import { evidenceSummary } from "./data/evidenceSummary.js";
import { governanceReport } from "./data/governanceReport.js";
import { hardeningSummary } from "./data/hardeningSummary.js";
import { opsAnalytics } from "./data/opsAnalytics.js";
import { qualityCalibration } from "./data/qualityCalibration.js";
import { incidentResponse } from "./data/incidentResponse.js";
import { evalGate } from "./data/evalGate.js";
import { agenticAbuseLab } from "./data/agenticAbuseLab.js";
import { campaignGallery } from "./data/campaignGallery.js";

const app = document.querySelector("#app");

const state = {
  threshold: 0.48,
  queue: "flagged",
  selectedId: null,
  selectedMode: "dataset",
  activeLens: "content",
  activeModule: "overview",
  agentStrategy: "airdrop-funnel",
  incidentId: "ir_wallet_drainer_campaign",
  incidentChoice: "route_review",
  calibrationIndex: 0,
  calibrationAnswers: {},
  customText:
    "Limited airdrop for verified holders. Connect your wallet now to claim 5 ETH before the window closes.",
};

const incidentChoices = [
  {
    id: "monitor",
    label: "Monitor",
    description: "Keep watching while evidence is weak.",
    exposureReduction: 8,
    backlogDelta: 0,
    falsePositiveRisk: 8,
    appealRisk: 4,
    confidence: 35,
  },
  {
    id: "route_review",
    label: "Route to review",
    description: "Send representative samples to human review before public action.",
    exposureReduction: 30,
    backlogDelta: 18,
    falsePositiveRisk: -18,
    appealRisk: -10,
    confidence: 62,
  },
  {
    id: "public_label",
    label: "Public label",
    description: "Apply user-facing warning where evidence is concrete.",
    exposureReduction: 55,
    backlogDelta: -5,
    falsePositiveRisk: 22,
    appealRisk: 18,
    confidence: 58,
  },
  {
    id: "warning_friction",
    label: "Warning friction",
    description: "Add click-through or sharing friction while preserving review.",
    exposureReduction: 44,
    backlogDelta: 8,
    falsePositiveRisk: 6,
    appealRisk: 6,
    confidence: 68,
  },
  {
    id: "rate_limit_cluster",
    label: "Rate-limit cluster",
    description: "Reduce repeated entity spread after campaign evidence is confirmed.",
    exposureReduction: 64,
    backlogDelta: 10,
    falsePositiveRisk: 12,
    appealRisk: 14,
    confidence: 72,
  },
  {
    id: "escalate",
    label: "Escalate",
    description: "Bring policy, product, legal, or engineering into the decision loop.",
    exposureReduction: 36,
    backlogDelta: 22,
    falsePositiveRisk: -4,
    appealRisk: 0,
    confidence: 78,
  },
];

const calibrationActions = [
  { id: "public_label", label: "Public label" },
  { id: "human_review", label: "Human review" },
  { id: "no_label", label: "No label" },
  { id: "escalate", label: "Escalate" },
];

const consoleModules = [
  {
    id: "overview",
    label: "Overview",
    group: "Start",
    title: "Crypto Scam Moderation Lab",
    description:
      "A browser-based safety product for deciding when crypto-related posts should be labeled, reviewed, escalated, or left alone.",
  },
  {
    id: "queue",
    label: "Review Queue",
    group: "Review",
    title: "Review queue",
    description:
      "Inspect ranked cases, evidence, ground truth, prediction errors, and the decision boundary used by the labeler.",
  },
  {
    id: "tester",
    label: "Test Post",
    group: "Review",
    title: "Test a post",
    description:
      "Try clean examples, borderline cases, and obfuscated variants against the same policy rubric and risk scorer.",
  },
  {
    id: "evals",
    label: "Evals",
    group: "Assurance",
    title: "Evaluation suite",
    description:
      "Check whether the system preserves legitimate speech, catches scam patterns, and blocks regressions before launch.",
  },
  {
    id: "agentic",
    label: "GenAI Abuse Lab",
    group: "Assurance",
    title: "GenAI and agentic abuse lab",
    description:
      "Generate bounded synthetic scam variants, test reviewer-assistant guardrails, and inspect where automation must stop.",
  },
  {
    id: "campaigns",
    label: "Campaign Graph",
    group: "Intelligence",
    title: "Campaign graph",
    description:
      "Follow shared domains, wallet-like strings, repeated handles, and high-risk phrases across local review candidates.",
  },
  {
    id: "ops",
    label: "Ops Analytics",
    group: "Operations",
    title: "Operations analytics",
    description:
      "Tune thresholds while watching review coverage, backlog, precision, recall, and repeated-entity leads.",
  },
  {
    id: "qa",
    label: "QA Calibration",
    group: "Operations",
    title: "QA calibration",
    description:
      "Translate policy into reviewer consistency checks, evidence quality standards, and protected-context safeguards.",
  },
  {
    id: "incidents",
    label: "Incident Response",
    group: "Operations",
    title: "Incident response",
    description:
      "Review tabletop scenarios for fast-moving scam waves, false-positive spikes, and ambiguous visual evidence.",
  },
  {
    id: "governance",
    label: "Appeals / Transparency",
    group: "Governance",
    title: "Appeals and transparency",
    description:
      "See notice templates, appeal paths, reversal scenarios, and public-safe transparency controls.",
  },
  {
    id: "model",
    label: "Model Audit",
    group: "Governance",
    title: "Model audit",
    description:
      "Compare the browser scoring simulator with the reproducible baseline and inspect the operating threshold.",
  },
];

const moduleHashAliases = {
  "case-review": "queue",
  metrics: "ops",
  "hardening-evals": "evals",
  "evidence-extractor": "evals",
  "adversarial-lab": "evals",
  "agentic-abuse-lab": "agentic",
  "eval-gate": "evals",
  "campaign-graph": "campaigns",
  "live-store": "campaigns",
  "ops-analytics": "ops",
  "quality-calibration": "qa",
  "incident-response": "incidents",
  policy: "overview",
};

const scenarioTexts = [
  {
    id: "giveaway",
    label: "Giveaway",
    text:
      "Elon Musk is giving away 1000 ETH to celebrate. Send 0.1 ETH to our verified wallet and get 0.5 ETH back instantly.",
  },
  {
    id: "legit-news",
    label: "Legit news",
    text:
      "Coinbase earnings are out. Revenue was up this quarter, but analysts still disagree about long-term exchange volume.",
  },
  {
    id: "ambiguous",
    label: "Ambiguous",
    text:
      "Lost access to an old wallet from 2016. Does anyone know a recovery service with a transparent fee structure?",
  },
  {
    id: "satire",
    label: "Satire",
    text:
      "I am obviously not the CEO of Bitcoin, but if you send me one imaginary coin I will send back two imaginary coins.",
  },
];

const policyRules = [
  {
    id: "returns",
    label: "Unrealistic returns",
    weight: 0.25,
    detail: "Guaranteed, risk-free, doubled, or extreme short-term gains.",
    patterns: [
      /guaranteed/i,
      /risk[-\s]?free/i,
      /double your/i,
      /[0-9]{2,}\s?%/i,
      /[0-9]+x/i,
      /instant(?:ly)?/i,
      /profit/i,
      /returns?/i,
    ],
  },
  {
    id: "transfer",
    label: "Transfer request",
    weight: 0.24,
    detail: "Requests to send assets, pay a fee, deposit funds, or connect a wallet.",
    patterns: [
      /send\s+(?:me\s+)?(?:[0-9.]+\s*)?(btc|bitcoin|eth|ethereum|sol|usdt|crypto)/i,
      /send .* wallet/i,
      /connect your wallet/i,
      /conecta(?:r)?\s+(?:tu\s+)?billetera/i,
      /verifica.*billetera/i,
      /wallet address/i,
      /processing fee/i,
      /upfront/i,
      /deposit/i,
      /wire transfer/i,
    ],
  },
  {
    id: "giveaway",
    label: "Suspicious giveaway",
    weight: 0.22,
    detail: "Airdrops, promo codes, free tokens, and claim language.",
    patterns: [
      /airdrop/i,
      /bono/i,
      /giveaway/i,
      /claim/i,
      /reclama/i,
      /won/i,
      /prize/i,
      /congratulations/i,
      /absolutely free/i,
      /gratis/i,
      /free\s+(btc|bitcoin|eth|ethereum|usdt|crypto|token)/i,
      /promo code/i,
      /bonus/i,
      /selected/i,
      /winner/i,
    ],
  },
  {
    id: "authority",
    label: "Authority misuse",
    weight: 0.13,
    detail: "Claims of official status, celebrity sponsorship, or major-brand affiliation.",
    patterns: [
      /official/i,
      /verified/i,
      /elon|musk|bill gates|microsoft|cr7|ronaldo/i,
      /coinbase|binance|meta|tesla/i,
      /founder/i,
      /ceo/i,
    ],
  },
  {
    id: "urgency",
    label: "Urgent call to action",
    weight: 0.12,
    detail: "Time pressure, scarcity, or direct action phrasing.",
    patterns: [
      /limited/i,
      /limitado/i,
      /expires?/i,
      /urgent/i,
      /act now/i,
      /hurry/i,
      /spots? available/i,
      /before it closes/i,
      /antes de que cierre/i,
      /now/i,
    ],
  },
  {
    id: "link",
    label: "Risky link surface",
    weight: 0.1,
    detail: "Shorteners, wallet-drainer phrasing, or domains that mimic campaign pages.",
    patterns: [
      /https?:\/\//i,
      /\b[a-z0-9-]+\.(cash|io|net|xyz|top|click)\b/i,
      /\b[a-z0-9-]*(winner|airdrop|giveaway|secure|crypto)[a-z0-9-]*\.[a-z]{2,}\b/i,
      /bit\.ly|tinyurl|t\.co/i,
      /secure/i,
      /winner/i,
    ],
  },
];

const financialTerms = [
  "bitcoin",
  "btc",
  "ethereum",
  "eth",
  "crypto",
  "token",
  "wallet",
  "airdrop",
  "staking",
  "trading",
  "investment",
  "profit",
  "return",
  "usdt",
  "defi",
  "exchange",
];

const reportedMetrics = {
  trainRows: posts.filter((post) => post.split === "train").length,
  testRows: posts.filter((post) => post.split === "test").length,
  fraudPrecision: 0.882,
  fraudRecall: 1,
  thresholdF1: 0.938,
  operationalPrecision: 0.882,
  operationalRecall: 1,
  operationalF1: 0.938,
  weightedF1: 0.953,
};

const lenses = {
  content: {
    label: "Content",
    title: "Label and friction",
    items: [
      "Potential Crypto Fraud label",
      "Click-through warning for risky links",
      "No blanket ban on ordinary crypto discussion",
    ],
  },
  behavior: {
    label: "Behavior",
    title: "Rate and reach controls",
    items: ["DM throttles for scam spikes", "New-account posting limits", "Warnings before reposting"],
  },
  actor: {
    label: "Actor",
    title: "Account-level escalation",
    items: ["Repeated-domain clustering", "Verification for financial promoters", "Appeals before high-impact sanctions"],
  },
};

const testerMutations = [
  {
    id: "space",
    label: "Space",
    apply: (text) =>
      text
        .replace(/\bwallet\b/gi, "w a l l e t")
        .replace(/\bconnect\b/gi, "c o n n e c t")
        .replace(/\bclaim\b/gi, "c l a i m")
        .replace(/\bairdrop\b/gi, "a i r d r o p"),
  },
  {
    id: "leet",
    label: "Leet",
    apply: (text) =>
      text
        .replace(/\bofficial\b/gi, "0fficial")
        .replace(/\bwallet\b/gi, "w4llet")
        .replace(/\bcrypto\b/gi, "crypt0")
        .replace(/\bclaim\b/gi, "cl4im")
        .replace(/\bconnect\b/gi, "c0nnect"),
  },
  {
    id: "defang",
    label: "Defang",
    apply: (text) => {
      const defanged = text
        .replace(/https?:\/\//gi, "hxxps://")
        .replace(/\b([a-z0-9-]+)\.(xyz|top|click|cash|net|io|com)\b/gi, "$1[.]$2");
      return defanged === text ? `${text} hxxps://secure-claim[.]xyz` : defanged;
    },
  },
  {
    id: "ocr",
    label: "OCR",
    apply: (text) =>
      `[Image OCR]\nScreenshot text: ${cleanText(text)}\nQR code visible. Link is cropped. Source account not visible.`,
  },
];

const assignmentPolicyBrief = [
  {
    label: "Harm definition",
    title: "Investment scams, not crypto discussion",
    text:
      "Fraudulent schemes persuade people to send money to illegitimate opportunities by promising easy, fast, or low-risk returns. Wallet drainers, fake airdrops, advance-fee recovery, and impersonated support are in scope.",
  },
  {
    label: "ABC spread model",
    title: "Who acts, what they do, what users see",
    text:
      "Actors include fake coaches, bots, impersonators, and compromised accounts. Behaviors include unsolicited DMs, fabricated testimonials, mass tagging, and repeated links. Content includes wallet asks, referral posts, airdrop graphics, and guaranteed-return claims.",
  },
  {
    label: "Why intervene",
    title: "High severity and high platform responsibility",
    text:
      "The proposal used the Severity x Responsibility framework: financial and identity losses can be life-changing, while reposts, feeds, DMs, and decentralized labelers shape reach. Acting protects user trust and brand safety, even though false positives and review costs must be controlled.",
  },
  {
    label: "AIM + ABC response",
    title: "Use proportionate friction before blanket removal",
    text:
      "Verify financial promoters, cluster reused domains and wallets, rate-limit suspicious bursts, warn before risky links, and combine automated detection with human review. Anticipate new patterns, incentivize verification, and mitigate confirmed campaigns.",
  },
  {
    label: "Boundaries",
    title: "Keep legitimate speech visible and appealable",
    text:
      "The proposal rejected blanket crypto bans, manual pre-approval, and reports-only enforcement. Warnings, news, satire, technical discussion, and help-seeking stay protected; interventions use minimal data, multi-source evidence, transparent notices, and appeals.",
  },
];

const primerSteps = [
  {
    label: "Policy proposal",
    title: "Define the boundary",
    text:
      "Assignment 2 established what counts as investment-scam harm, how it spreads on Bluesky, why the platform should act, and where intervention would overreach.",
  },
  {
    label: "Coursework prototype",
    title: "Test the first labeler",
    text:
      "The final project translated that policy into labeled examples and a Bluesky-style Potential Crypto Fraud classifier, then measured where the first implementation failed.",
  },
  {
    label: "Portfolio system",
    title: "Build the operating loop",
    text:
      "The rebuild connects scoring to review queues, evals, evidence, campaigns, appeals, QA, incidents, and launch gates so decisions can be challenged and improved.",
  },
];

const glossaryTerms = [
  {
    term: "Potential Crypto Fraud",
    definition: "A warning label for posts that combine scam-like claims with concrete evidence, not a blanket crypto ban.",
  },
  {
    term: "Human review",
    definition: "The safer middle path when a post is suspicious but context is missing or a public label could overreach.",
  },
  {
    term: "Eval",
    definition: "A deliberately written test case with an expected outcome, used to catch regressions and policy mistakes.",
  },
  {
    term: "Evidence",
    definition: "The specific words, links, domains, or entities that justify a label or explain why the system should hold back.",
  },
];

function cleanText(text) {
  return String(text || "")
    .replace(/^"+|"+$/g, "")
    .replace(/""/g, '"')
    .trim();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function percentage(value) {
  if (!Number.isFinite(value)) return "0%";
  return `${Math.round(value * 100)}%`;
}

function decimal(value) {
  if (!Number.isFinite(value)) return "0.00";
  return value.toFixed(2);
}

function signedDecimal(value) {
  if (!Number.isFinite(value)) return "0.000";
  return `${value >= 0 ? "+" : ""}${value.toFixed(3)}`;
}

function humanize(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function compactEntity(value) {
  const text = String(value || "");
  if (text.length <= 32) return text;
  return `${text.slice(0, 14)}...${text.slice(-10)}`;
}

function moduleFromHash(hash = window.location.hash) {
  const key = String(hash || "#overview").replace(/^#/, "") || "overview";
  const moduleId = moduleHashAliases[key] || key;
  return consoleModules.some((module) => module.id === moduleId) ? moduleId : "overview";
}

function activeModule() {
  return consoleModules.find((module) => module.id === state.activeModule) || consoleModules[0];
}

function scrollToConsoleTop() {
  window.requestAnimationFrame(() => window.scrollTo(0, 0));
  window.setTimeout(() => window.scrollTo(0, 0), 0);
  window.setTimeout(() => window.scrollTo(0, 0), 80);
}

function activateModule(moduleId, updateHash = true) {
  if (!consoleModules.some((module) => module.id === moduleId)) return;
  state.activeModule = moduleId;
  if (updateHash && window.location.hash !== `#${moduleId}`) {
    window.history.pushState(null, "", `#${moduleId}`);
  }
  render();
  scrollToConsoleTop();
}

function entityDisplayValue(entity) {
  if (entity.type === "risk_phrase") return humanize(entity.value).toLowerCase();
  return compactEntity(entity.value);
}

function countMatches(text, patterns) {
  return patterns.reduce((count, pattern) => count + (pattern.test(text) ? 1 : 0), 0);
}

function scoreText(text) {
  const normalized = cleanText(text);
  const lower = normalized.toLowerCase();
  const ruleResults = policyRules.map((rule) => {
    const hits = countMatches(normalized, rule.patterns);
    const matched = hits > 0;
    const contribution = matched ? rule.weight : 0;
    return { ...rule, hits, matched, contribution };
  });

  const financeHits = financialTerms.reduce(
    (count, term) => count + (lower.includes(term) ? 1 : 0),
    0,
  );
  const walletPattern =
    /(0x[a-f0-9]{20,}|bc1[a-z0-9]{20,}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|[A-Za-z0-9]{24,})/i;
  const hasWalletishString = walletPattern.test(normalized);
  const uppercaseRatio =
    normalized.length === 0
      ? 0
      : normalized.split("").filter((char) => char >= "A" && char <= "Z").length / normalized.length;
  const financeBoost = Math.min(0.1, financeHits * 0.018);
  const walletBoost = hasWalletishString ? 0.08 : 0;
  const emphasisBoost = uppercaseRatio > 0.12 ? 0.025 : 0;
  const base = normalized.length > 0 ? 0.07 : 0;
  const score = Math.min(
    0.98,
    base +
      ruleResults.reduce((sum, rule) => sum + rule.contribution, 0) +
      financeBoost +
      walletBoost +
      emphasisBoost,
  );

  const action = decideAction(score);
  return {
    text: normalized,
    score,
    action,
    financeHits,
    hasWalletishString,
    uppercaseRatio,
    ruleResults,
  };
}

function decideAction(score) {
  const threshold = state.threshold;
  if (score >= Math.min(0.92, threshold + 0.28)) return "Block pending reviewer confirmation";
  if (score >= threshold + 0.14) return "Interstitial plus downrank";
  if (score >= threshold) return "Potential Crypto Fraud label";
  if (score >= Math.max(0, threshold - 0.12)) return "Human review queue";
  return "No label";
}

function scorePost(post) {
  const result = scoreText(post.text);
  return {
    ...post,
    ...result,
    prediction: result.score >= state.threshold ? 1 : 0,
    review: result.score >= state.threshold - 0.12 && result.score < state.threshold,
  };
}

function scoredDataset() {
  return posts.map((post) => scorePost({ ...post, text: cleanText(post.text) }));
}

function liveItemToCase(item, index) {
  const policy = item.policyEvidence || {};
  const rules = Array.isArray(policy.rules) ? policy.rules : [];
  return {
    id: item.uri || `live-${index}`,
    mode: "live",
    split: `live / ${item.status || "new"}`,
    groundTruth: null,
    prediction: ["apply_potential_crypto_fraud_label", "high_confidence_escalation"].includes(item.action) ? 1 : 0,
    review: item.action === "send_to_human_review",
    text: cleanText(item.text),
    score: Number(item.probability) || 0,
    action: humanize(item.action),
    financeHits: policy.finance_term_count || 0,
    hasWalletishString: Boolean(policy.walletish_string),
    uppercaseRatio: policy.uppercase_ratio || 0,
    ruleResults: rules.map((rule) => ({
      id: rule.name,
      label: humanize(rule.name),
      weight: rule.contribution || 0.02,
      detail: rule.description || "",
      hits: rule.hits || 0,
      matched: Boolean(rule.matched),
      contribution: rule.contribution || 0,
    })),
    source: item.source,
    sourceQuery: item.sourceQuery,
    sourceUri: item.uri,
    status: item.status,
    reviewerDecision: item.reviewerDecision,
    reviewerNotes: item.reviewerNotes,
    author: item.author || {},
    entities: item.entities || [],
    duplicateCount: item.duplicateCount || 1,
    ingestedAt: item.ingestedAt,
  };
}

function liveQueueItems() {
  return (liveReviewQueue.items || [])
    .map((item, index) => liveItemToCase(item, index))
    .sort((a, b) => b.score - a.score);
}

function computeMetrics(items) {
  const cm = items.reduce(
    (acc, item) => {
      if (item.groundTruth === 1 && item.prediction === 1) acc.tp += 1;
      if (item.groundTruth === 0 && item.prediction === 1) acc.fp += 1;
      if (item.groundTruth === 0 && item.prediction === 0) acc.tn += 1;
      if (item.groundTruth === 1 && item.prediction === 0) acc.fn += 1;
      return acc;
    },
    { tp: 0, fp: 0, tn: 0, fn: 0 },
  );
  const precision = cm.tp / Math.max(1, cm.tp + cm.fp);
  const recall = cm.tp / Math.max(1, cm.tp + cm.fn);
  const specificity = cm.tn / Math.max(1, cm.tn + cm.fp);
  const f1 = (2 * precision * recall) / Math.max(0.001, precision + recall);
  const accuracy = (cm.tp + cm.tn) / Math.max(1, items.length);
  return { ...cm, precision, recall, specificity, f1, accuracy };
}

function thresholdCurve(items) {
  const points = [];
  for (let threshold = 0.2; threshold <= 0.9; threshold += 0.05) {
    const evaluated = items.map((item) => ({
      ...item,
      prediction: item.score >= threshold ? 1 : 0,
    }));
    const metrics = computeMetrics(evaluated);
    points.push({
      threshold,
      precision: metrics.precision,
      recall: metrics.recall,
    });
  }
  return points;
}

function queueItems(items) {
  if (state.queue === "live") {
    return liveQueueItems().slice(0, 80);
  }
  const filters = {
    flagged: (item) => item.prediction === 1,
    review: (item) => item.review,
    falsePositive: (item) => item.prediction === 1 && item.groundTruth === 0,
    falseNegative: (item) => item.prediction === 0 && item.groundTruth === 1,
    all: () => true,
  };
  const filter = filters[state.queue] || filters.flagged;
  return items
    .filter(filter)
    .sort((a, b) => {
      if (state.queue === "review") {
        return Math.abs(a.score - state.threshold) - Math.abs(b.score - state.threshold);
      }
      return b.score - a.score;
    })
    .slice(0, 80);
}

function selectedItem(items, queue) {
  if (state.selectedMode === "custom") {
    const result = scoreText(state.customText);
    return {
      id: "custom",
      split: "live",
      groundTruth: null,
      prediction: result.score >= state.threshold ? 1 : 0,
      review: result.score >= state.threshold - 0.12 && result.score < state.threshold,
      ...result,
    };
  }
  if (state.selectedMode === "live" || state.queue === "live") {
    const liveItems = liveQueueItems();
    return liveItems.find((item) => item.id === state.selectedId) || queue[0] || liveItems[0] || items[0];
  }
  return (
    items.find((item) => item.id === state.selectedId) ||
    queue[0] ||
    items.find((item) => item.split === "test") ||
    items[0]
  );
}

function labelForGroundTruth(value) {
  if (value === 1) return "Fraud";
  if (value === 0) return "Legit";
  return "Unlabeled";
}

function labelForPrediction(value) {
  return value === 1 ? "Flagged" : "Not flagged";
}

function renderQueueItem(item, selected) {
  const mode = item.mode || "dataset";
  const active = selected && selected.id === item.id && state.selectedMode === mode;
  const errorClass =
    item.prediction === 1 && item.groundTruth === 0
      ? "false-positive"
      : item.prediction === 0 && item.groundTruth === 1
        ? "false-negative"
        : "";
  return `
    <button class="queue-item ${active ? "active" : ""} ${errorClass}" data-select="${escapeHtml(item.id)}" data-select-mode="${mode}">
      <span class="queue-meta">
        <strong>${escapeHtml(item.id)}</strong>
        <span>${escapeHtml(item.split)} / ${labelForGroundTruth(item.groundTruth)}</span>
      </span>
      <span class="queue-score">${percentage(item.score)}</span>
      <span class="queue-text">${escapeHtml(item.text.slice(0, 138))}${item.text.length > 138 ? "..." : ""}</span>
    </button>
  `;
}

function renderLiveMetadata(item) {
  if (item.mode !== "live") return "";
  return `
    <div class="live-meta">
      <span>${escapeHtml(humanize(item.status))}</span>
      <span>${escapeHtml(item.source || "local")}</span>
      <span>${escapeHtml(item.author?.handle || item.author?.did || "unknown actor")}</span>
      <span>${item.duplicateCount} observations</span>
    </div>
  `;
}

function renderEntityChips(item) {
  if (!Array.isArray(item.entities) || item.entities.length === 0) return "";
  const entities = [...item.entities]
    .sort((a, b) => (b.riskWeight || 0) - (a.riskWeight || 0))
    .slice(0, 10);
  return `
    <div class="entity-chip-row" aria-label="Extracted entities">
      ${entities
        .map(
          (entity) => `
            <span class="entity-chip ${escapeHtml(entity.type)}">
              <b>${escapeHtml(humanize(entity.type))}</b>
              ${escapeHtml(entityDisplayValue(entity))}
            </span>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderEvidence(item) {
  return `
    <div class="evidence-list">
      ${item.ruleResults
        .map(
          (rule) => `
            <div class="evidence-row ${rule.matched ? "matched" : ""}">
              <div>
                <strong>${escapeHtml(rule.label)}</strong>
                <span>${escapeHtml(rule.detail)}</span>
              </div>
              <div class="bar" aria-label="${escapeHtml(rule.label)} contribution">
                <i style="width: ${rule.matched ? Math.round(rule.weight * 100) : 4}%"></i>
              </div>
              <b>${rule.matched ? `+${Math.round(rule.weight * 100)}` : "0"}</b>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderConfusionMatrix(metrics) {
  return `
    <div class="matrix" role="img" aria-label="Confusion matrix">
      <span></span><strong>Pred legit</strong><strong>Pred fraud</strong>
      <strong>True legit</strong><b>${metrics.tn}</b><b class="warn">${metrics.fp}</b>
      <strong>True fraud</strong><b class="warn">${metrics.fn}</b><b>${metrics.tp}</b>
    </div>
  `;
}

function renderCurve(points) {
  const width = 330;
  const height = 160;
  const x = (index) => 28 + (index * 280) / Math.max(1, points.length - 1);
  const y = (value) => 132 - value * 104;
  const precision = points.map((point, index) => `${x(index)},${y(point.precision)}`).join(" ");
  const recall = points.map((point, index) => `${x(index)},${y(point.recall)}`).join(" ");
  const thresholdX = 28 + ((state.threshold - 0.2) / 0.7) * 280;
  return `
    <svg class="curve" viewBox="0 0 ${width} ${height}" role="img" aria-label="Precision recall threshold curve">
      <line x1="28" y1="132" x2="310" y2="132" class="axis"></line>
      <line x1="28" y1="24" x2="28" y2="132" class="axis"></line>
      <polyline points="${precision}" class="precision-line"></polyline>
      <polyline points="${recall}" class="recall-line"></polyline>
      <line x1="${thresholdX}" y1="24" x2="${thresholdX}" y2="132" class="threshold-line"></line>
      <text x="34" y="18">precision</text>
      <text x="128" y="18">recall</text>
      <text x="220" y="150">threshold</text>
    </svg>
  `;
}

function renderLens() {
  const lens = lenses[state.activeLens];
  return `
    <div class="lens-card">
      <div class="segmented">
        ${Object.entries(lenses)
          .map(
            ([key, value]) => `
              <button type="button" class="${state.activeLens === key ? "active" : ""}" data-lens="${key}">
                ${escapeHtml(value.label)}
              </button>
            `,
          )
          .join("")}
      </div>
      <h3>${escapeHtml(lens.title)}</h3>
      <ul>
        ${lens.items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    </div>
  `;
}

function renderSelected(item) {
  const scoreClass =
    item.score >= state.threshold + 0.14 ? "high" : item.score >= state.threshold ? "medium" : "low";
  return `
    <section class="panel detail-panel" id="case-review">
      <div class="section-label">Case review</div>
      <div class="detail-head">
        <div>
          <h2>${state.selectedMode === "custom" ? "Live post tester" : escapeHtml(item.id)}</h2>
          <span>${escapeHtml(item.split)} / ground truth: ${labelForGroundTruth(item.groundTruth)}</span>
        </div>
        <div class="score-ring ${scoreClass}">
          <strong>${percentage(item.score)}</strong>
          <span>risk</span>
        </div>
      </div>
      <blockquote>${escapeHtml(item.text)}</blockquote>
      ${renderLiveMetadata(item)}
      <div class="decision-strip">
        <span class="${item.prediction ? "bad" : "good"}">${labelForPrediction(item.prediction)}</span>
        <strong>${escapeHtml(item.action)}</strong>
      </div>
      ${renderEvidence(item)}
      <div class="feature-chips">
        <span>${item.financeHits} finance terms</span>
        <span>${item.hasWalletishString ? "wallet-like string" : "no wallet pattern"}</span>
        <span>${Math.round(item.uppercaseRatio * 100)}% uppercase</span>
      </div>
      ${renderEntityChips(item)}
    </section>
  `;
}

function renderTester() {
  return `
    <section class="panel tester-panel" id="tester">
      <div class="section-label">Try a post</div>
      <textarea id="custom-text" rows="6">${escapeHtml(state.customText)}</textarea>
      <div class="scenario-row">
        ${scenarioTexts
          .map(
            (scenario) => `
              <button type="button" data-scenario="${escapeHtml(scenario.id)}">${escapeHtml(scenario.label)}</button>
            `,
          )
          .join("")}
      </div>
      <div class="mutation-row">
        ${testerMutations
          .map(
            (mutation) => `
              <button type="button" data-mutation="${escapeHtml(mutation.id)}">${escapeHtml(mutation.label)}</button>
            `,
          )
          .join("")}
      </div>
      <button type="button" class="primary-action" id="evaluate-custom">Evaluate draft</button>
    </section>
  `;
}

function renderMetrics(metrics, curvePoints) {
  return `
    <section class="panel metrics-panel" id="metrics">
      <div class="section-label">Threshold tuning</div>
      <label class="threshold-control">
        <span>Risk threshold ${percentage(state.threshold)}</span>
        <input id="threshold" type="range" min="0.2" max="0.9" step="0.01" value="${state.threshold}" />
      </label>
      <div class="metric-grid">
        <div><strong>${percentage(metrics.precision)}</strong><span>precision</span></div>
        <div><strong>${percentage(metrics.recall)}</strong><span>recall</span></div>
        <div><strong>${percentage(metrics.f1)}</strong><span>F1</span></div>
        <div><strong>${percentage(metrics.specificity)}</strong><span>legit recall</span></div>
      </div>
      ${renderCurve(curvePoints)}
      ${renderConfusionMatrix(metrics)}
    </section>
  `;
}

function renderReportedModel() {
  return `
    <section class="panel model-panel" id="model">
      <div class="section-label">Model baselines</div>
      <div class="reported-grid">
        <div><strong>${reportedMetrics.trainRows}</strong><span>train posts</span></div>
        <div><strong>${reportedMetrics.testRows}</strong><span>test posts</span></div>
        <div><strong>${percentage(reportedMetrics.operationalRecall)}</strong><span>public-label recall</span></div>
        <div><strong>${reportedMetrics.operationalF1.toFixed(3)}</strong><span>operational F1</span></div>
      </div>
      ${renderBaselineBars()}
      <p>
        Browser scoring is an explainable rubric simulator. The reproducible v2 baseline uses
        TF-IDF, policy features, review/label/escalation thresholds, and public-label evidence guardrails.
      </p>
    </section>
  `;
}

function renderBaselineBars() {
  const rows = [
    ["Precision", reportedMetrics.operationalPrecision, "#0f766e"],
    ["Recall", reportedMetrics.operationalRecall, "#b45309"],
    ["F1", reportedMetrics.operationalF1, "#1d4ed8"],
    ["Weighted F1", reportedMetrics.weightedF1, "#be123c"],
  ];
  return `
    <svg class="model-chart" viewBox="0 0 360 172" role="img" aria-label="Reported v2 baseline metrics">
      <rect x="0" y="0" width="360" height="172" rx="8" fill="#ffffff" />
      <line x1="104" y1="18" x2="104" y2="150" class="axis" />
      ${rows
        .map(([label, value, color], index) => {
          const y = 28 + index * 34;
          const width = Math.max(3, value * 220);
          return `
            <text x="12" y="${y + 14}">${label}</text>
            <rect x="104" y="${y}" width="220" height="18" rx="5" fill="#e7edf5" />
            <rect x="104" y="${y}" width="${width}" height="18" rx="5" fill="${color}" />
            <text x="332" y="${y + 14}" text-anchor="end">${percentage(value)}</text>
          `;
        })
        .join("")}
    </svg>
  `;
}

function renderEvalSuite() {
  return `
    <section class="panel eval-panel" id="evals">
      <div class="section-label">Eval suite</div>
      <div class="reported-grid">
        <div><strong>${evalSummary.caseCount}</strong><span>scenario cases</span></div>
        <div><strong>${percentage(evalSummary.expectationPassRate)}</strong><span>expectation pass</span></div>
        <div><strong>${percentage(evalSummary.publicLabelPrecision)}</strong><span>public-label precision</span></div>
        <div><strong>${percentage(evalSummary.adversarialPassRate)}</strong><span>adversarial pass</span></div>
      </div>
      <p>
        Evals separate public labels from review routing across fraud, legitimate speech, ambiguous cases, and obfuscated scam variants.
      </p>
      <ul class="eval-notes">
        <li>Educational, research, satire, and developer contexts suppress public labels.</li>
        <li>High-risk recovery and unverified airdrop contexts can route to review without public enforcement.</li>
      </ul>
    </section>
  `;
}

function renderHardeningEvals() {
  const dimensions = (hardeningSummary.dimensionSummary || []).slice(0, 5);
  const urlEvidence = (hardeningSummary.topUrlEvidence || []).slice(0, 4);
  const failures = hardeningSummary.topFailureIds || [];
  return `
    <section class="panel hardening-panel" id="hardening-evals">
      <div class="section-label">Hardening evals</div>
      <div class="reported-grid">
        <div><strong>${hardeningSummary.caseCount || 0}</strong><span>hardening cases</span></div>
        <div><strong>${percentage(hardeningSummary.expectationPassRate)}</strong><span>expectation pass</span></div>
        <div><strong>${percentage(hardeningSummary.reviewOrLabelRecall)}</strong><span>review recall</span></div>
        <div><strong>${percentage(hardeningSummary.legitimateNoPublicLabelRate)}</strong><span>legit protected</span></div>
      </div>
      <div class="hardening-dimension-list">
        ${dimensions
          .map(
            (dimension) => `
              <div>
                <span>${escapeHtml(humanize(dimension.name))}</span>
                <strong>${dimension.passed}/${dimension.count}</strong>
                <b>${percentage(dimension.passRate)}</b>
              </div>
            `,
          )
          .join("")}
      </div>
      <div class="hardening-url-list">
        ${urlEvidence
          .map(
            (item) => `
              <div>
                <strong>${escapeHtml(item.domain)}</strong>
                <span>${escapeHtml((item.riskFactors || []).map(humanize).join(", "))}</span>
                <b>${Math.round((item.riskWeight || 0) * 100)}</b>
              </div>
            `,
          )
          .join("")}
      </div>
      <p>
        This suite probes canonicalization, defanged URLs, shorteners, OCR/source ambiguity,
        Spanish-language scam phrasing, and protected-context false positives. ${
          failures.length
            ? `${failures.length} current failure${failures.length === 1 ? "" : "s"} need review.`
            : "No current expectation failures."
        }
      </p>
    </section>
  `;
}

function renderAdversarialLab() {
  const mutations = (adversarialLab.mutationSummary || []).slice(0, 5);
  const weakness = (adversarialLab.topWeaknesses || [])[0];
  return `
    <section class="panel adversarial-panel" id="adversarial-lab">
      <div class="section-label">Adversarial lab</div>
      <div class="reported-grid">
        <div><strong>${adversarialLab.variantCount || 0}</strong><span>mutated variants</span></div>
        <div><strong>${percentage(adversarialLab.reviewOrLabelRetentionRate)}</strong><span>review recall</span></div>
        <div><strong>${percentage(adversarialLab.publicLabelRetentionRate)}</strong><span>public-label retained</span></div>
        <div><strong>${percentage(adversarialLab.downgradeRate)}</strong><span>downgraded</span></div>
      </div>
      <div class="mutation-list">
        ${mutations
          .map(
            (mutation) => `
              <div class="mutation-row-result">
                <div>
                  <strong>${escapeHtml(mutation.label)}</strong>
                  <span>${escapeHtml(humanize(mutation.category))}</span>
                </div>
                <b>${percentage(mutation.publicLabelRetentionRate)}</b>
                <span>${mutation.downgradeCount} downgraded</span>
              </div>
            `,
          )
          .join("")}
      </div>
      ${
        weakness
          ? `
            <div class="weakness-card">
              <span>Top weakness</span>
              <strong>${escapeHtml(weakness.mutationLabel)} / ${escapeHtml(weakness.seedId)}</strong>
              <p>${escapeHtml(humanize(weakness.baselineAction))} to ${escapeHtml(humanize(weakness.mutatedAction))}; probability ${signedDecimal(weakness.probabilityDelta)}.</p>
            </div>
          `
          : ""
      }
    </section>
  `;
}

function activeAgentStrategy() {
  return (
    (agenticAbuseLab.strategies || []).find((strategy) => strategy.id === state.agentStrategy) ||
    (agenticAbuseLab.strategies || [])[0]
  );
}

function agenticDecision(variant, scored) {
  if (variant.protectedContext && scored.score >= state.threshold - 0.12) return "Human review only";
  if (scored.score >= state.threshold) return "Public label candidate";
  if (scored.score >= state.threshold - 0.12) return "Human review";
  return "No label";
}

function agenticVariantResults() {
  const strategy = activeAgentStrategy();
  return (strategy?.variants || []).map((variant) => {
    const scored = scoreText(variant.text);
    const decision = agenticDecision(variant, scored);
    return {
      ...variant,
      ...scored,
      decision,
      reviewOrLabel: decision !== "No label",
      publicLabelCandidate: decision === "Public label candidate",
      downgradedFromPublic:
        scored.score >= state.threshold &&
        decision !== "Public label candidate" &&
        variant.expectedBoundary !== "public_label_candidate",
    };
  });
}

function agenticMetrics(results) {
  const risky = results.filter((variant) => variant.risk);
  const protectedVariants = results.filter((variant) => variant.protectedContext);
  const publicEligibleButBounded = results.filter(
    (variant) => variant.score >= state.threshold && variant.expectedBoundary !== "public_label_candidate",
  );
  const overreachFailures = (agenticAbuseLab.agentRiskTests || []).filter((test) => !test.passed);
  return {
    generatedVariantCount: results.length,
    reviewOrLabelRetentionRate:
      risky.length > 0 ? risky.filter((variant) => variant.reviewOrLabel).length / risky.length : 0,
    publicLabelDowngradeRate:
      publicEligibleButBounded.length > 0
        ? publicEligibleButBounded.filter((variant) => variant.downgradedFromPublic).length /
          publicEligibleButBounded.length
        : 0,
    protectedContextFalsePositiveRate:
      protectedVariants.length > 0
        ? protectedVariants.filter((variant) => variant.publicLabelCandidate).length / protectedVariants.length
        : 0,
    assistantOverreachRate:
      (agenticAbuseLab.agentRiskTests || []).length > 0
        ? overreachFailures.length / (agenticAbuseLab.agentRiskTests || []).length
        : 0,
  };
}

function renderAgenticAbuseLab() {
  const strategy = activeAgentStrategy();
  const results = agenticVariantResults();
  const metrics = agenticMetrics(results);
  return `
    <section class="panel agentic-panel" id="agentic-abuse-lab">
      <div class="section-label">GenAI abuse lab</div>
      <div class="agentic-control-row">
        <div>
          <h3>${escapeHtml(strategy.label)}</h3>
          <p>${escapeHtml(strategy.summary)}</p>
        </div>
        <div class="segmented agentic-tabs" aria-label="Synthetic abuse strategy">
          ${(agenticAbuseLab.strategies || [])
            .map(
              (item) => `
                <button type="button" class="${state.agentStrategy === item.id ? "active" : ""}" data-agent-strategy="${escapeHtml(item.id)}">
                  ${escapeHtml(item.label)}
                </button>
              `,
            )
            .join("")}
        </div>
      </div>
      <div class="reported-grid">
        <div><strong>${metrics.generatedVariantCount}</strong><span>synthetic variants</span></div>
        <div><strong>${percentage(metrics.reviewOrLabelRetentionRate)}</strong><span>review-or-label retained</span></div>
        <div><strong>${percentage(metrics.publicLabelDowngradeRate)}</strong><span>bounded downgrade</span></div>
        <div><strong>${percentage(metrics.assistantOverreachRate)}</strong><span>assistant overreach</span></div>
      </div>
      <div class="agent-variant-list">
        ${results
          .map(
            (variant) => `
              <article class="agent-variant-card ${variant.publicLabelCandidate ? "public" : variant.reviewOrLabel ? "review" : "safe"}">
                <div class="agent-variant-head">
                  <span>${escapeHtml(variant.step)}</span>
                  <strong>${escapeHtml(variant.decision)}</strong>
                  <b>${percentage(variant.score)}</b>
                </div>
                <p>${escapeHtml(variant.text)}</p>
                <div class="agent-chip-row">
                  <span>${variant.risk ? "risk-bearing" : "context-bearing"}</span>
                  <span>${variant.protectedContext ? "protected context" : "direct claim"}</span>
                  <span>${escapeHtml(humanize(variant.expectedBoundary))}</span>
                </div>
              </article>
            `,
          )
          .join("")}
      </div>
      <div class="agent-risk-list">
        ${(agenticAbuseLab.agentRiskTests || [])
          .map(
            (test) => `
              <div class="${test.passed ? "passed" : "failed"}">
                <span>${test.passed ? "Pass" : "Fail"}</span>
                <strong>${escapeHtml(test.label)}</strong>
                <p>${escapeHtml(test.challenge)}</p>
                <b>${escapeHtml(test.expectedBoundary)}</b>
              </div>
            `,
          )
          .join("")}
      </div>
      <p>${escapeHtml(agenticAbuseLab.safetyBoundary)}</p>
    </section>
  `;
}

function renderEvidenceExtractor() {
  const examples = (evidenceSummary.examples || []).slice(0, 3);
  const actions = evidenceSummary.actionCounts || {};
  const failureCount = Object.values(evidenceSummary.failureCounts || {}).reduce((sum, count) => sum + count, 0);
  return `
    <section class="panel evidence-extractor-panel" id="evidence-extractor">
      <div class="section-label">Evidence extractor</div>
      <div class="reported-grid">
        <div><strong>${evidenceSummary.caseCount || 0}</strong><span>cases checked</span></div>
        <div><strong>${percentage(evidenceSummary.passRate)}</strong><span>expectation pass</span></div>
        <div><strong>${percentage(evidenceSummary.spanFaithfulnessRate)}</strong><span>span faithfulness</span></div>
        <div><strong>${failureCount}</strong><span>eval failures</span></div>
      </div>
      <div class="action-breakdown" aria-label="Evidence extractor action distribution">
        ${Object.entries(actions)
          .map(
            ([action, count]) => `
              <div>
                <span>${escapeHtml(humanize(action))}</span>
                <strong>${count}</strong>
              </div>
            `,
          )
          .join("")}
      </div>
      <div class="evidence-example-list">
        ${examples
          .map(
            (example) => `
              <div class="evidence-example-card">
                <div class="evidence-example-head">
                  <strong>${escapeHtml(example.caseId)}</strong>
                  <span>${escapeHtml(humanize(example.recommendedReviewerAction))} / ${percentage(example.confidence)}</span>
                </div>
                <p>${escapeHtml(example.reviewerSummary)}</p>
                <div class="evidence-factor-row">
                  ${(example.riskFactors || [])
                    .map((factor) => `<span class="risk">${escapeHtml(humanize(factor))}</span>`)
                    .join("")}
                  ${(example.benignFactors || [])
                    .map((factor) => `<span class="benign">${escapeHtml(humanize(factor))}</span>`)
                    .join("")}
                  ${(example.missingContext || [])
                    .map((factor) => `<span class="missing">${escapeHtml(humanize(factor))}</span>`)
                    .join("")}
                </div>
              </div>
            `,
          )
          .join("")}
      </div>
      <p>
        This layer extracts cited reviewer evidence only. Public labels remain gated by policy thresholds, evals, and human review.
      </p>
    </section>
  `;
}

function renderLiveStore() {
  const counts = liveReviewQueue.statusCounts || {};
  return `
    <section class="panel live-store-panel" id="live-store">
      <div class="section-label">Live review store</div>
      <div class="reported-grid">
        <div><strong>${liveReviewQueue.count || 0}</strong><span>stored candidates</span></div>
        <div><strong>${counts.new || 0}</strong><span>new</span></div>
        <div><strong>${counts.review || 0}</strong><span>in review</span></div>
        <div><strong>${(counts.labeled || 0) + (counts.escalated || 0) + (counts.dismissed || 0)}</strong><span>decided</span></div>
      </div>
      <p>
        Exported from the local SQLite queue. Search and Jetstream ingestion dedupe by URI/CID before this browser view imports candidates.
      </p>
    </section>
  `;
}

function renderOpsAnalytics() {
  const summary = opsAnalytics.summary || {};
  const entities = opsAnalytics.topEntities || [];
  const backlog = opsAnalytics.backlogItems || [];
  return `
    <section class="panel ops-panel" id="ops-analytics">
      <div class="section-label">Ops Analytics</div>
      <div class="reported-grid">
        <div><strong>${summary.totalItems || 0}</strong><span>queue items</span></div>
        <div><strong>${percentage(summary.reviewCoverage || 0)}</strong><span>review coverage</span></div>
        <div><strong>${summary.unreviewedItems || 0}</strong><span>backlog</span></div>
        <div><strong>${summary.totalObservations || 0}</strong><span>observations</span></div>
      </div>
      <div class="action-breakdown" aria-label="Operations action distribution">
        ${(opsAnalytics.actionCounts || [])
          .map(
            (item) => `
              <div>
                <span>${escapeHtml(humanize(item.action))}</span>
                <strong>${item.count}</strong>
              </div>
            `,
          )
          .join("")}
      </div>
      <div class="ops-entity-list">
        ${entities
          .slice(0, 4)
          .map(
            (entity) => `
              <div>
                <span>${escapeHtml(humanize(entity.entity_type))}</span>
                <strong>${escapeHtml(entity.value)}</strong>
                <b>${entity.linked_items} linked</b>
              </div>
            `,
          )
          .join("")}
      </div>
      <p>
        Operations view: review load, unresolved backlog, action mix, and repeated entity leads. ${
          backlog.length ? `${backlog.length} unresolved demo candidate${backlog.length === 1 ? "" : "s"} remain.` : "No unresolved demo backlog."
        }
      </p>
    </section>
  `;
}

function calibrationCases() {
  return qualityCalibration.cases || qualityCalibration.sampleCases || [];
}

function activeCalibrationCase() {
  const cases = calibrationCases();
  return cases[state.calibrationIndex] || cases[0];
}

function isProtectedCalibrationCase(item) {
  return [
    "consumer_warning",
    "market_news",
    "multilingual_help_seeking",
    "developer_context",
    "ocr_source_ambiguity",
    "satire",
    "redirect_mismatch",
  ].includes(item.policy_focus);
}

function calibrationSummary() {
  const cases = calibrationCases();
  const answered = cases.filter((item) => state.calibrationAnswers[item.id]);
  const correct = answered.filter((item) => state.calibrationAnswers[item.id] === item.expected_action);
  const protectedCases = answered.filter(isProtectedCalibrationCase);
  const protectedMisses = protectedCases.filter((item) => state.calibrationAnswers[item.id] === "public_label");
  const overEnforcement = answered.filter(
    (item) => item.expected_action !== "public_label" && state.calibrationAnswers[item.id] === "public_label",
  );
  const underEnforcement = answered.filter(
    (item) => item.expected_action === "public_label" && state.calibrationAnswers[item.id] !== "public_label",
  );
  return {
    answered: answered.length,
    total: cases.length,
    accuracy: answered.length ? correct.length / answered.length : 0,
    protectedMisses: protectedMisses.length,
    overEnforcement: overEnforcement.length,
    underEnforcement: underEnforcement.length,
  };
}

function renderCalibrationSimulator() {
  const cases = calibrationCases();
  const item = activeCalibrationCase();
  const answer = state.calibrationAnswers[item.id];
  const summary = calibrationSummary();
  const expected = calibrationActions.find((action) => action.id === item.expected_action)?.label || humanize(item.expected_action);
  return `
    <section class="panel calibration-simulator-panel" id="calibration-simulator">
      <div class="section-label">Calibration simulator</div>
      <div class="calibration-head">
        <div>
          <h3>${escapeHtml(item.id)}</h3>
          <p>${escapeHtml(item.text)}</p>
        </div>
        <div class="calibration-progress">
          <strong>${state.calibrationIndex + 1}/${cases.length}</strong>
          <span>${summary.answered} answered</span>
        </div>
      </div>
      <div class="agent-chip-row">
        <span>${escapeHtml(humanize(item.policy_focus))}</span>
        <span>${escapeHtml(humanize(item.severity))}</span>
        <span>${isProtectedCalibrationCase(item) ? "context-sensitive" : "direct evidence"}</span>
      </div>
      <div class="calibration-action-row" aria-label="Calibration actions">
        ${calibrationActions
          .map(
            (action) => `
              <button type="button" class="${answer === action.id ? "active" : ""}" data-calibration-choice="${escapeHtml(action.id)}">
                ${escapeHtml(action.label)}
              </button>
            `,
          )
          .join("")}
      </div>
      ${
        answer
          ? `
            <div class="calibration-feedback ${answer === item.expected_action ? "correct" : "miss"}">
              <span>${answer === item.expected_action ? "Match" : "Review miss"}</span>
              <strong>Expected: ${escapeHtml(expected)}</strong>
              <p>${escapeHtml(item.rationale)}</p>
            </div>
          `
          : ""
      }
      <div class="calibration-score-grid">
        <div><strong>${percentage(summary.accuracy)}</strong><span>action accuracy</span></div>
        <div><strong>${summary.protectedMisses}</strong><span>protected-context misses</span></div>
        <div><strong>${summary.overEnforcement}</strong><span>over-enforcement risk</span></div>
        <div><strong>${summary.underEnforcement}</strong><span>under-enforcement risk</span></div>
      </div>
      <div class="calibration-nav-row">
        <button type="button" data-calibration-nav="-1">Previous</button>
        <button type="button" data-calibration-nav="1">Next</button>
      </div>
    </section>
  `;
}

function renderQualityCalibration() {
  const coverage = qualityCalibration.coverage || {};
  const standards = qualityCalibration.calibrationStandards || [];
  const cases = qualityCalibration.sampleCases || [];
  return `
    <section class="panel quality-panel" id="quality-calibration">
      <div class="section-label">QA Calibration</div>
      <div class="reported-grid">
        <div><strong>${qualityCalibration.caseCount || 0}</strong><span>calibration cases</span></div>
        <div><strong>${coverage.publicLabelCases || 0}</strong><span>label cases</span></div>
        <div><strong>${coverage.humanReviewCases || 0}</strong><span>review cases</span></div>
        <div><strong>${coverage.protectedContextCases || 0}</strong><span>protected contexts</span></div>
      </div>
      <div class="qa-standard-list">
        ${standards
          .slice(0, 4)
          .map((standard) => `<div><span>QA</span><strong>${escapeHtml(standard)}</strong></div>`)
          .join("")}
      </div>
      <div class="calibration-case-list">
        ${cases
          .slice(0, 3)
          .map(
            (item) => `
              <div>
                <span>${escapeHtml(humanize(item.expected_action))}</span>
                <strong>${escapeHtml(item.id)}</strong>
                <p>${escapeHtml(item.rationale)}</p>
              </div>
            `,
          )
          .join("")}
      </div>
      <p>
        Calibration turns policy into reviewer consistency checks: action accuracy, evidence quality, context sensitivity, and appeal-ready notes.
      </p>
    </section>
  `;
}

function activeIncidentScenario() {
  return (
    (incidentResponse.scenarios || []).find((scenario) => scenario.id === state.incidentId) ||
    (incidentResponse.scenarios || [])[0]
  );
}

function activeIncidentChoice() {
  return incidentChoices.find((choice) => choice.id === state.incidentChoice) || incidentChoices[1];
}

function clampImpact(value) {
  return Math.max(0, Math.min(100, value));
}

function incidentOutcome(scenario, choice) {
  const outcome = { ...choice };
  if (scenario.id === "ir_wallet_drainer_campaign" && choice.id === "rate_limit_cluster") {
    outcome.exposureReduction += 12;
    outcome.confidence += 8;
  }
  if (scenario.id === "ir_false_positive_spike" && choice.id === "public_label") {
    outcome.exposureReduction -= 30;
    outcome.falsePositiveRisk += 26;
    outcome.appealRisk += 22;
    outcome.confidence -= 18;
  }
  if (scenario.id === "ir_false_positive_spike" && choice.id === "route_review") {
    outcome.falsePositiveRisk -= 12;
    outcome.confidence += 8;
  }
  if (scenario.id === "ir_ocr_qr_ambiguity" && choice.id === "public_label") {
    outcome.exposureReduction -= 22;
    outcome.falsePositiveRisk += 24;
    outcome.appealRisk += 18;
    outcome.confidence -= 20;
  }
  if (scenario.id === "ir_ocr_qr_ambiguity" && choice.id === "route_review") {
    outcome.falsePositiveRisk -= 10;
    outcome.confidence += 10;
  }
  return {
    ...outcome,
    exposureReduction: clampImpact(outcome.exposureReduction),
    falsePositiveRisk: Math.max(-40, Math.min(60, outcome.falsePositiveRisk)),
    appealRisk: Math.max(-30, Math.min(60, outcome.appealRisk)),
    confidence: clampImpact(outcome.confidence),
  };
}

function signedImpact(value) {
  return `${value > 0 ? "+" : ""}${value}`;
}

function renderImpactMeter(label, value, display, tone = "neutral") {
  return `
    <div class="impact-meter ${tone}">
      <div>
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(display)}</strong>
      </div>
      <i style="width: ${clampImpact(value)}%"></i>
    </div>
  `;
}

function renderIncidentReplay() {
  const scenario = activeIncidentScenario();
  const choice = activeIncidentChoice();
  const outcome = incidentOutcome(scenario, choice);
  const signals = scenario.signals || [];
  const firstActions = scenario.first_actions || [];
  const mitigations = scenario.mitigations || [];
  const postmortemQuestions = scenario.postmortem_questions || [];
  return `
    <section class="panel incident-replay-panel" id="incident-replay">
      <div class="section-label">Incident replay</div>
      <div class="incident-replay-head">
        <div>
          <h3>${escapeHtml(scenario.title)}</h3>
          <p>${escapeHtml(scenario.trigger)}</p>
        </div>
        <div class="segmented incident-tabs" aria-label="Incident scenario">
          ${(incidentResponse.scenarios || [])
            .map(
              (item) => `
                <button type="button" class="${state.incidentId === item.id ? "active" : ""}" data-incident="${escapeHtml(item.id)}">
                  ${escapeHtml(item.severity.toUpperCase())}
                </button>
              `,
            )
            .join("")}
        </div>
      </div>
      <div class="incident-choice-grid" aria-label="Response choices">
        ${incidentChoices
          .map(
            (item) => `
              <button type="button" class="${state.incidentChoice === item.id ? "active" : ""}" data-incident-choice="${escapeHtml(item.id)}">
                <strong>${escapeHtml(item.label)}</strong>
                <span>${escapeHtml(item.description)}</span>
              </button>
            `,
          )
          .join("")}
      </div>
      <div class="incident-outcome-grid">
        ${renderImpactMeter("Exposure reduced", outcome.exposureReduction, `${outcome.exposureReduction}%`, "good")}
        ${renderImpactMeter("Review backlog", clampImpact(50 + outcome.backlogDelta), signedImpact(outcome.backlogDelta), outcome.backlogDelta > 12 ? "warn" : "neutral")}
        ${renderImpactMeter("False-positive risk", clampImpact(50 + outcome.falsePositiveRisk), signedImpact(outcome.falsePositiveRisk), outcome.falsePositiveRisk > 0 ? "bad" : "good")}
        ${renderImpactMeter("Appeal risk", clampImpact(50 + outcome.appealRisk), signedImpact(outcome.appealRisk), outcome.appealRisk > 0 ? "warn" : "good")}
        ${renderImpactMeter("Confidence", outcome.confidence, `${outcome.confidence}%`, "neutral")}
      </div>
      <div class="incident-timeline">
        <div><span>1</span><strong>${escapeHtml(signals[0] || "Signal detected")}</strong></div>
        <div><span>2</span><strong>${escapeHtml(firstActions[0] || "Initial action selected")}</strong></div>
        <div><span>3</span><strong>${escapeHtml(choice.label)}: ${escapeHtml(choice.description)}</strong></div>
        <div><span>4</span><strong>${escapeHtml(mitigations[0] || "Create follow-up control")}</strong></div>
      </div>
      <div class="postmortem-card">
        <span>Generated follow-up</span>
        <strong>${escapeHtml(postmortemQuestions[0] || "Which signal fired first?")}</strong>
        <p>${escapeHtml(mitigations[mitigations.length - 1] || "Add a follow-up eval, policy note, or QA case.")}</p>
      </div>
    </section>
  `;
}

function renderIncidentResponse() {
  const highest = incidentResponse.highestSeverityScenario || {};
  const scenarios = incidentResponse.scenarios || [];
  const principles = incidentResponse.operatingPrinciples || [];
  return `
    <section class="panel incident-panel" id="incident-response">
      <div class="section-label">Incident Response</div>
      <div class="reported-grid">
        <div><strong>${incidentResponse.scenarioCount || 0}</strong><span>tabletops</span></div>
        <div><strong>${(incidentResponse.severityCounts || {}).sev2 || 0}</strong><span>SEV2</span></div>
        <div><strong>${(incidentResponse.severityCounts || {}).sev3 || 0}</strong><span>SEV3</span></div>
        <div><strong>${escapeHtml((highest.severity || "n/a").toUpperCase())}</strong><span>highest</span></div>
      </div>
      <div class="incident-scenario-list">
        ${scenarios
          .slice(0, 3)
          .map(
            (scenario) => `
              <div>
                <span>${escapeHtml((scenario.severity || "").toUpperCase())}</span>
                <strong>${escapeHtml(scenario.title)}</strong>
                <p>${escapeHtml(scenario.trigger)}</p>
              </div>
            `,
          )
          .join("")}
      </div>
      <div class="qa-standard-list compact">
        ${principles
          .slice(0, 3)
          .map((principle) => `<div><span>Principle</span><strong>${escapeHtml(principle)}</strong></div>`)
          .join("")}
      </div>
    </section>
  `;
}

function renderEvalGate() {
  const checks = evalGate.checks || [];
  return `
    <section class="panel gate-panel" id="eval-gate">
      <div class="section-label">Launch Gate</div>
      <div class="reported-grid">
        <div><strong>${evalGate.passed ? "Pass" : "Fail"}</strong><span>gate status</span></div>
        <div><strong>${evalGate.checkCount || 0}</strong><span>checks</span></div>
        <div><strong>${evalGate.failedCount || 0}</strong><span>failures</span></div>
        <div><strong>${checks.length ? percentage(checks.filter((item) => item.passed).length / checks.length) : "0%"}</strong><span>coverage</span></div>
      </div>
      <div class="gate-check-list">
        ${checks
          .slice(0, 6)
          .map(
            (item) => `
              <div class="${item.passed ? "passed" : "failed"}">
                <span>${item.passed ? "Pass" : "Fail"}</span>
                <strong>${escapeHtml(item.name)}</strong>
              </div>
            `,
          )
          .join("")}
      </div>
      <p>
        Regression gates protect false-positive control, review routing, evidence faithfulness,
        calibration coverage, and incident readiness before changes ship.
      </p>
    </section>
  `;
}

function renderGovernanceReport() {
  const queue = governanceReport.queueMetrics || {};
  const appeals = governanceReport.appealMetrics || {};
  const transparency = governanceReport.transparencyMetrics || {};
  const scenarios = (governanceReport.appealScenarios || []).slice(0, 4);
  const notices = (governanceReport.noticeTemplates || []).slice(0, 2);
  const scorecard = governanceReport.standardsScorecard || {};
  const controls = (scorecard.controls || []).slice(0, 5);
  return `
    <section class="panel governance-panel" id="governance">
      <div class="section-label">Appeals and transparency</div>
      <div class="reported-grid">
        <div><strong>${queue.reviewedOrTriaged || 0}</strong><span>reviewed or triaged</span></div>
        <div><strong>${transparency.totalActioned || 0}</strong><span>actioned locally</span></div>
        <div><strong>${appeals.submitted || 0}</strong><span>appeals tested</span></div>
        <div><strong>${appeals.reversed || 0}</strong><span>reversals tested</span></div>
      </div>
      <div class="notice-grid">
        ${notices
          .map(
            (notice) => `
              <div class="notice-card">
                <span>${escapeHtml(notice.trigger)}</span>
                <strong>${escapeHtml(notice.title)}</strong>
                <p>${escapeHtml(notice.body)}</p>
              </div>
            `,
          )
          .join("")}
      </div>
      <div class="appeal-flow-list">
        ${scenarios
          .map(
            (scenario) => `
              <div class="appeal-flow-card ${scenario.reversed ? "reversed" : "upheld"}">
                <div>
                  <strong>${escapeHtml(scenario.title)}</strong>
                  <span>${escapeHtml(scenario.initialAction)} to ${escapeHtml(humanize(scenario.finalOutcome))}</span>
                </div>
                <p>${escapeHtml(scenario.appealClaim)}</p>
                <div class="appeal-checks">
                  ${(scenario.reviewerChecks || [])
                    .slice(0, 2)
                    .map((check) => `<span>${escapeHtml(check)}</span>`)
                    .join("")}
                </div>
              </div>
            `,
          )
          .join("")}
      </div>
      <div class="standards-scorecard">
        <div class="scorecard-head">
          <strong>${decimal(scorecard.summary?.averageScore || 0)}</strong>
          <span>${scorecard.summary?.implementedCount || 0}/${scorecard.summary?.controlCount || 0} controls implemented</span>
        </div>
        ${controls
          .map(
            (control) => `
              <div class="scorecard-row">
                <span>${escapeHtml(control.standard)}</span>
                <strong>${escapeHtml(control.control)}</strong>
                <b>${escapeHtml(humanize(control.status))}</b>
              </div>
            `,
          )
          .join("")}
      </div>
      <p>
        The report separates local queue metrics from sanitized appeal scenarios so procedural-fairness coverage is visible without exposing live user content.
      </p>
    </section>
  `;
}

function renderCampaignGraph() {
  const counts = campaignGraph.entityTypeCounts || {};
  const topCampaign = (campaignGraph.campaigns || [])[0];
  const sharedEntities = (campaignGraph.sharedEntities || []).slice(0, 6);
  return `
    <section class="panel graph-panel" id="campaign-graph">
      <div class="section-label">Campaign graph</div>
      <div class="reported-grid">
        <div><strong>${campaignGraph.campaignCount || 0}</strong><span>clusters</span></div>
        <div><strong>${campaignGraph.sharedEntityCount || 0}</strong><span>shared entities</span></div>
        <div><strong>${(counts.domain || 0) + (counts.wallet || 0)}</strong><span>domains + wallets</span></div>
        <div><strong>${campaignGraph.linkedItemCount || 0}</strong><span>linked posts</span></div>
      </div>
      ${
        topCampaign
          ? `
            <div class="campaign-summary">
              <div>
                <span>Top cluster</span>
                <strong>${topCampaign.itemCount} posts / ${percentage(topCampaign.riskScore)} graph risk</strong>
              </div>
              <div class="campaign-status">
                ${Object.entries(topCampaign.statusCounts || {})
                  .map(([status, count]) => `<span>${escapeHtml(humanize(status))}: ${count}</span>`)
                  .join("")}
              </div>
            </div>
          `
          : "<p>No shared domain, wallet, shortener, or handle cluster in the current queue.</p>"
      }
      <div class="graph-entity-list">
        ${sharedEntities
          .map(
            (entity) => `
              <div class="graph-entity">
                <span>${escapeHtml(humanize(entity.type))}</span>
                <strong>${escapeHtml(compactEntity(entity.label || entity.value))}</strong>
                <b>${entity.itemCount} posts</b>
              </div>
            `,
          )
          .join("")}
      </div>
      <p>
        Entity links are deterministic extractions from the local queue: domains, wallet-like strings, handles, brands, and high-risk policy phrases.
      </p>
    </section>
  `;
}

function renderCampaignGallery() {
  return `
    <section class="panel campaign-gallery-panel" id="campaign-gallery">
      <div class="section-label">Campaign gallery</div>
      <div class="gallery-grid">
        ${(campaignGallery.campaigns || [])
          .map(
            (item) => `
              <article class="gallery-card ${escapeHtml(item.riskLevel)}">
                <div class="gallery-card-head">
                  <span>${escapeHtml(humanize(item.riskLevel))}</span>
                  <strong>${escapeHtml(item.title)}</strong>
                </div>
                <p>${escapeHtml(item.pattern)}</p>
                <div class="gallery-signal-row">
                  ${(item.visibleSignals || []).map((signal) => `<span>${escapeHtml(signal)}</span>`).join("")}
                </div>
                <b>${escapeHtml(item.defaultAction)}</b>
              </article>
            `,
          )
          .join("")}
      </div>
      <p>${escapeHtml(campaignGallery.privacyBoundary)}</p>
    </section>
  `;
}

function renderQueue(queue, selected) {
  const labels = [
    ["flagged", "Flagged"],
    ["review", "Review"],
    ["live", `Live (${liveReviewQueue.count || 0})`],
    ["falsePositive", "False positives"],
    ["falseNegative", "False negatives"],
    ["all", "All"],
  ];
  return `
    <section class="panel queue-panel" id="queue">
      <div class="section-label">Reviewer queue</div>
      <div class="segmented queue-tabs">
        ${labels
          .map(
            ([key, label]) => `
              <button type="button" class="${state.queue === key ? "active" : ""}" data-queue="${key}">
                ${label}
              </button>
            `,
          )
          .join("")}
      </div>
      <div class="queue-count">${queue.length} visible cases</div>
      <div class="queue-list">
        ${queue.length ? queue.map((item) => renderQueueItem(item, selected)).join("") : "<p>No cases match this queue.</p>"}
      </div>
    </section>
  `;
}

function renderProjectPrimer(metrics) {
  return `
    <section class="project-primer" id="overview">
      <div class="primer-hero">
        <div class="primer-copy">
          <span class="section-label">The problem</span>
          <h2>Catch scams without silencing crypto conversation</h2>
          <p>
            On social platforms, investment scams often appear as giveaways, wallet recovery, support replies,
            guaranteed returns, or urgent connection prompts. The same words also appear in warnings, news,
            technical help, satire, and honest questions.
          </p>
          <p>
            This project turns a policy proposal and coursework labeler into a working safety system. It separates
            public labels from human review, exposes the evidence behind each decision, and tests whether the system
            protects legitimate speech when scammers change tactics.
          </p>
          <div class="primer-actions" aria-label="Project entry points">
            <a href="#queue">Review a case</a>
            <a href="#tester">Test a post</a>
            <a href="#evals">Inspect evals</a>
          </div>
        </div>
        <div class="primer-case-file">
          <span>Three possible outcomes</span>
          <div class="snapshot-grid">
            <div><strong>${posts.length}</strong><small>labeled examples</small></div>
            <div><strong>${percentage(metrics.recall)}</strong><small>simulated recall</small></div>
            <div><strong>${metrics.fp}</strong><small>false positives at this threshold</small></div>
          </div>
          <div class="signal-stage" aria-label="Moderation flow preview">
            <div class="flow-row risk">
              <span class="signal-dot" aria-hidden="true"></span>
              <strong>Official giveaway, send ETH</strong>
              <small>Public label</small>
            </div>
            <div class="flow-row review">
              <span class="signal-dot" aria-hidden="true"></span>
              <strong>Is this a legit airdrop?</strong>
              <small>Human review</small>
            </div>
            <div class="flow-row safe">
              <span class="signal-dot" aria-hidden="true"></span>
              <strong>Warning: do not connect</strong>
              <small>No label</small>
            </div>
          </div>
          <p>
            The goal is not to maximize one model score. The goal is to decide when to label,
            when to review, and when to leave speech alone.
          </p>
        </div>
      </div>

      <section class="policy-brief" aria-labelledby="policy-brief-title">
        <header class="policy-brief-head">
          <span class="section-label">Assignment 2, distilled</span>
          <div>
            <h3 id="policy-brief-title">The policy proposal behind the product</h3>
            <p>
              Assignment 2 asked a concrete decision question: how should Bluesky reduce investment scams
              without suppressing legitimate financial speech? The proposal answered it in five parts.
            </p>
          </div>
        </header>
        <div class="policy-brief-grid">
          ${assignmentPolicyBrief
            .map(
              (item, index) => `
                <article class="policy-brief-item">
                  <span>${String(index + 1).padStart(2, "0")} / ${escapeHtml(item.label)}</span>
                  <h3>${escapeHtml(item.title)}</h3>
                  <p>${escapeHtml(item.text)}</p>
                </article>
              `,
            )
            .join("")}
        </div>
      </section>

      <section class="build-path" aria-labelledby="build-path-title">
        <div class="build-path-head">
          <span class="section-label">From policy to product</span>
          <h3 id="build-path-title">One decision system, built in three steps</h3>
        </div>
        <div class="build-path-grid">
          ${primerSteps
          .map(
            (step, index) => `
              <article class="build-path-item">
                <span>${String(index + 1).padStart(2, "0")} / ${escapeHtml(step.label)}</span>
                <h3>${step.title}</h3>
                <p>${step.text}</p>
              </article>
            `,
          )
          .join("")}
        </div>
      </section>

      <section class="glossary-band" aria-label="Key terms">
        <span class="section-label">Key terms</span>
        <dl>
          ${glossaryTerms
            .map(
              (item) => `
                <div>
                  <dt>${escapeHtml(item.term)}</dt>
                  <dd>${escapeHtml(item.definition)}</dd>
                </div>
              `,
            )
            .join("")}
        </dl>
      </section>
    </section>
  `;
}

function renderPolicyCard() {
  return `
    <section class="panel policy-panel" id="policy">
      <div class="section-label">Policy boundary</div>
      <div class="policy-grid">
        <div>
          <h3>Apply</h3>
          <p>Guaranteed returns, crypto transfer requests, suspicious airdrops, impersonation, or wallet connection pressure.</p>
        </div>
        <div>
          <h3>Do not apply</h3>
          <p>General market commentary, news reporting, technical project discussion, or clear satire without fund solicitation.</p>
        </div>
      </div>
      ${renderLens()}
    </section>
  `;
}

function renderConsoleNav() {
  let currentGroup = "";
  return `
    <aside class="console-sidebar" aria-label="Lab navigation">
      <div class="console-brand">
        <span>Safety console</span>
        <strong>Crypto Scam Moderation</strong>
        <small>Policy, evidence, evals, and operations in one inspectable browser lab.</small>
      </div>
      <label class="mobile-module-select" for="module-select">
        <span>Workspace</span>
        <select id="module-select">
          ${consoleModules
            .map(
              (module) => `
                <option value="${escapeHtml(module.id)}" ${state.activeModule === module.id ? "selected" : ""}>
                  ${escapeHtml(module.label)}
                </option>
              `,
            )
            .join("")}
        </select>
      </label>
      <nav class="console-nav">
        ${consoleModules
          .map((module) => {
            const groupLabel =
              module.group !== currentGroup
                ? `<span class="nav-group">${escapeHtml(module.group)}</span>`
                : "";
            currentGroup = module.group;
            return `
              ${groupLabel}
              <button
                type="button"
                class="module-button ${state.activeModule === module.id ? "active" : ""}"
                data-module="${escapeHtml(module.id)}"
                aria-current="${state.activeModule === module.id ? "page" : "false"}"
              >
                <span>${escapeHtml(module.label)}</span>
              </button>
            `;
          })
          .join("")}
      </nav>
    </aside>
  `;
}

function renderSystemBar(metrics, queue, selected) {
  const liveCounts = liveReviewQueue.statusCounts || {};
  return `
    <section class="system-bar" aria-label="System status">
      <div class="system-title">
        <span>${escapeHtml(activeModule().group)}</span>
        <strong>${escapeHtml(activeModule().label)}</strong>
      </div>
      <div class="system-metric">
        <span>Visible cases</span>
        <strong>${queue.length}</strong>
      </div>
      <div class="system-metric">
        <span>Threshold</span>
        <strong>${percentage(state.threshold)}</strong>
      </div>
      <div class="system-metric">
        <span>Precision / recall</span>
        <strong>${percentage(metrics.precision)} / ${percentage(metrics.recall)}</strong>
      </div>
      <div class="system-metric">
        <span>Selected risk</span>
        <strong>${percentage(selected.score)}</strong>
      </div>
      <div class="system-metric">
        <span>Live queue</span>
        <strong>${liveReviewQueue.count || 0}</strong>
        <small>${liveCounts.review || 0} in review</small>
      </div>
    </section>
  `;
}

function renderModuleHeader() {
  const module = activeModule();
  return `
    <header class="module-header">
      <span>${escapeHtml(module.group)}</span>
      <h2>${escapeHtml(module.title)}</h2>
      <p>${escapeHtml(module.description)}</p>
    </header>
  `;
}

function renderSummaryStrip(metrics) {
  return `
    <section class="summary-strip" aria-label="Project summary">
      <div><strong>Potential Crypto Fraud</strong><span>conservative label</span></div>
      <div><strong>${posts.length}</strong><span>assignment posts</span></div>
      <div><strong>${percentage(metrics.recall)}</strong><span>simulated recall</span></div>
      <div><strong>${metrics.fp}</strong><span>false positives at current threshold</span></div>
    </section>
  `;
}

function renderEvidenceRail(selected, metrics, queue) {
  const matchedRules = (selected.ruleResults || []).filter((rule) => rule.matched).slice(0, 4);
  const liveCounts = liveReviewQueue.statusCounts || {};
  return `
    <aside class="evidence-rail" aria-label="Selected case and system context">
      <section class="rail-card selected-rail-card">
        <span class="rail-label">Selected case</span>
        <strong>${state.selectedMode === "custom" ? "Draft post" : escapeHtml(selected.id)}</strong>
        <p>${escapeHtml(selected.text.slice(0, 168))}${selected.text.length > 168 ? "..." : ""}</p>
        <div class="rail-decision">
          <span class="${selected.prediction ? "bad" : "good"}">${labelForPrediction(selected.prediction)}</span>
          <b>${percentage(selected.score)}</b>
        </div>
      </section>
      <section class="rail-card">
        <span class="rail-label">Evidence</span>
        ${
          matchedRules.length
            ? matchedRules
                .map(
                  (rule) => `
                    <div class="rail-evidence-row">
                      <strong>${escapeHtml(rule.label)}</strong>
                      <span>+${Math.round(rule.weight * 100)}</span>
                    </div>
                  `,
                )
                .join("")
            : "<p>No high-weight policy evidence matched this case.</p>"
        }
      </section>
      <section class="rail-card">
        <span class="rail-label">Queue health</span>
        <div class="rail-stat"><strong>${queue.length}</strong><span>visible</span></div>
        <div class="rail-stat"><strong>${metrics.fp}</strong><span>false positives</span></div>
        <div class="rail-stat"><strong>${metrics.fn}</strong><span>false negatives</span></div>
      </section>
      <section class="rail-card">
        <span class="rail-label">Launch gate</span>
        <div class="gate-pill ${evalGate.passed ? "passed" : "failed"}">${evalGate.passed ? "Pass" : "Fail"}</div>
        <p>${evalGate.failedCount || 0} failed checks across ${evalGate.checkCount || 0} safeguards.</p>
      </section>
      <section class="rail-card">
        <span class="rail-label">Live store</span>
        <div class="rail-stat"><strong>${liveReviewQueue.count || 0}</strong><span>candidates</span></div>
        <div class="rail-stat"><strong>${liveCounts.new || 0}</strong><span>new</span></div>
      </section>
    </aside>
  `;
}

function renderModuleContent({ metrics, curvePoints, queue, selected }) {
  if (state.activeModule === "overview") {
    return renderProjectPrimer(metrics);
  }

  if (state.activeModule === "queue") {
    return `
      <div class="module-grid review-grid">
        ${renderQueue(queue, selected)}
        <div class="module-stack">
          ${renderSelected(selected)}
          ${renderPolicyCard()}
        </div>
      </div>
    `;
  }

  if (state.activeModule === "tester") {
    return `
      <div class="module-grid two-column">
        <div class="module-stack">
          ${renderTester()}
          ${renderSelected(selected)}
        </div>
        <div class="module-stack">
          ${renderEvidenceExtractor()}
          ${renderAdversarialLab()}
        </div>
      </div>
    `;
  }

  if (state.activeModule === "evals") {
    return `
      <div class="module-grid two-column">
        <div class="module-stack">
          ${renderEvalSuite()}
          ${renderHardeningEvals()}
        </div>
        <div class="module-stack">
          ${renderEvalGate()}
          ${renderAgenticAbuseLab()}
          ${renderAdversarialLab()}
          ${renderEvidenceExtractor()}
        </div>
      </div>
    `;
  }

  if (state.activeModule === "agentic") {
    return `
      <div class="module-grid two-column">
        ${renderAgenticAbuseLab()}
        <div class="module-stack">
          ${renderEvidenceExtractor()}
          ${renderEvalGate()}
        </div>
      </div>
    `;
  }

  if (state.activeModule === "campaigns") {
    return `
      <div class="module-grid two-column">
        <div class="module-stack">
          ${renderCampaignGraph()}
          ${renderCampaignGallery()}
        </div>
        <div class="module-stack">
          ${renderLiveStore()}
          ${renderOpsAnalytics()}
        </div>
      </div>
    `;
  }

  if (state.activeModule === "ops") {
    return `
      <div class="module-grid two-column">
        ${renderMetrics(metrics, curvePoints)}
        ${renderOpsAnalytics()}
      </div>
    `;
  }

  if (state.activeModule === "qa") {
    return `
      <div class="module-grid two-column">
        <div class="module-stack">
          ${renderCalibrationSimulator()}
          ${renderQualityCalibration()}
        </div>
        <div class="module-stack">
          ${renderPolicyCard()}
          ${renderEvidenceExtractor()}
        </div>
      </div>
    `;
  }

  if (state.activeModule === "incidents") {
    return `
      <div class="module-grid two-column">
        <div class="module-stack">
          ${renderIncidentReplay()}
          ${renderIncidentResponse()}
        </div>
        <div class="module-stack">
          ${renderEvalGate()}
          ${renderOpsAnalytics()}
        </div>
      </div>
    `;
  }

  if (state.activeModule === "governance") {
    return `
      <div class="module-grid two-column">
        ${renderGovernanceReport()}
        <div class="module-stack">
          ${renderPolicyCard()}
          ${renderQualityCalibration()}
        </div>
      </div>
    `;
  }

  return `
    <div class="module-grid two-column">
      ${renderReportedModel()}
      <div class="module-stack">
        ${renderMetrics(metrics, curvePoints)}
        ${renderEvalSuite()}
      </div>
    </div>
  `;
}

function renderConsoleWorkspace(context) {
  return `
    <main class="console-main">
      ${renderSystemBar(context.metrics, context.queue, context.selected)}
      <section class="console-workspace">
        ${state.activeModule === "overview" ? "" : renderModuleHeader()}
        <div class="module-content" data-active-module="${escapeHtml(state.activeModule)}">
          ${renderModuleContent(context)}
        </div>
      </section>
    </main>
  `;
}

function render() {
  const scored = scoredDataset();
  const testItems = scored.filter((item) => item.split === "test");
  const metrics = computeMetrics(testItems);
  const queue = queueItems(scored);
  const selected = selectedItem(scored, queue);
  const curvePoints = thresholdCurve(testItems);

  app.innerHTML = `
    <div class="console-shell">
      ${renderConsoleNav()}
      ${renderConsoleWorkspace({ metrics, curvePoints, queue, selected })}
      ${renderEvidenceRail(selected, metrics, queue)}
    </div>
  `;

  attachEvents();
}

function attachEvents() {
  document.querySelectorAll("[data-module]").forEach((button) => {
    button.addEventListener("click", () => {
      activateModule(button.dataset.module);
    });
  });

  const moduleSelect = document.querySelector("#module-select");
  if (moduleSelect) {
    moduleSelect.addEventListener("change", (event) => {
      activateModule(event.target.value);
    });
  }

  document.querySelectorAll("[data-queue]").forEach((button) => {
    button.addEventListener("click", () => {
      state.queue = button.dataset.queue;
      state.selectedMode = button.dataset.queue === "live" ? "live" : "dataset";
      render();
    });
  });

  document.querySelectorAll("[data-select]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedId = button.dataset.select;
      state.selectedMode = button.dataset.selectMode || "dataset";
      render();
    });
  });

  document.querySelectorAll("[data-lens]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeLens = button.dataset.lens;
      render();
    });
  });

  document.querySelectorAll("[data-agent-strategy]").forEach((button) => {
    button.addEventListener("click", () => {
      state.agentStrategy = button.dataset.agentStrategy;
      render();
    });
  });

  document.querySelectorAll("[data-incident]").forEach((button) => {
    button.addEventListener("click", () => {
      state.incidentId = button.dataset.incident;
      render();
    });
  });

  document.querySelectorAll("[data-incident-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      state.incidentChoice = button.dataset.incidentChoice;
      render();
    });
  });

  document.querySelectorAll("[data-calibration-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      const item = activeCalibrationCase();
      state.calibrationAnswers[item.id] = button.dataset.calibrationChoice;
      render();
    });
  });

  document.querySelectorAll("[data-calibration-nav]").forEach((button) => {
    button.addEventListener("click", () => {
      const cases = calibrationCases();
      const delta = Number(button.dataset.calibrationNav);
      state.calibrationIndex = (state.calibrationIndex + delta + cases.length) % cases.length;
      render();
    });
  });

  document.querySelectorAll("[data-scenario]").forEach((button) => {
    button.addEventListener("click", () => {
      const scenario = scenarioTexts.find((item) => item.id === button.dataset.scenario);
      if (scenario) {
        state.customText = scenario.text;
        state.selectedMode = "custom";
        render();
      }
    });
  });

  document.querySelectorAll("[data-mutation]").forEach((button) => {
    button.addEventListener("click", () => {
      const mutation = testerMutations.find((item) => item.id === button.dataset.mutation);
      if (mutation) {
        state.customText = mutation.apply(state.customText);
        state.selectedMode = "custom";
        render();
      }
    });
  });

  const threshold = document.querySelector("#threshold");
  if (threshold) {
    threshold.addEventListener("input", (event) => {
      state.threshold = Number(event.target.value);
      render();
    });
  }

  const customText = document.querySelector("#custom-text");
  const evaluate = document.querySelector("#evaluate-custom");
  if (customText && evaluate) {
    evaluate.addEventListener("click", () => {
      state.customText = customText.value;
      state.selectedMode = "custom";
      render();
    });
  }
}

window.addEventListener("hashchange", () => {
  const nextModule = moduleFromHash();
  if (nextModule !== state.activeModule) {
    state.activeModule = nextModule;
    render();
    scrollToConsoleTop();
  }
});

state.activeModule = moduleFromHash();
render();
scrollToConsoleTop();
