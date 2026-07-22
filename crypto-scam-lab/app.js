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
import { errorAnalysis } from "./data/errorAnalysis.js";
import { llmComparison } from "./data/llmComparison.js";
import { scaleSimulation } from "./data/scaleSimulation.js";
import { threatLandscape } from "./data/threatLandscape.js";
import { liveStreamCalibration } from "./data/liveStreamCalibration.js";
import { attachLiveRadar, configureLiveRadar, renderLiveRadar, stopLiveRadar } from "./radar.js";

const app = document.querySelector("#app");

const state = {
  threshold: 0.48,
  queue: "falsePositive",
  selectedId: null,
  selectedMode: "dataset",
  activeLens: "content",
  activeModule: "welcome",
  heroText:
    "Elon Musk is giving away 1000 ETH to celebrate. Send 0.1 ETH to our verified wallet and get 0.5 ETH back instantly.",
  tourStep: null,
  subTabs: { assurance: "failures", intel: "campaigns", operations: "ops", govern: "governance" },
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
    id: "welcome",
    label: "The story",
    subtitle: "The central question",
    group: "",
    title: "The story",
    description: "What this project is, why it exists, and a live demo you can try without reading anything else.",
    featured: true,
  },
  {
    id: "overview",
    label: "The approach",
    subtitle: "Policy to product",
    group: "",
    title: "Crypto Scam Moderation Lab",
    description: "A browser-based safety product for deciding when crypto-related posts should be labeled, reviewed, escalated, or left alone.",
  },
  {
    id: "queue",
    label: "Case archive",
    subtitle: "Evidence behind decisions",
    group: "Appendix",
    title: "Case archive",
    description: "Browse annotated examples, their evidence, and the decision boundary used by the labeler.",
  },
  {
    id: "tester",
    label: "Try it",
    subtitle: "Try the policy boundary",
    group: "",
    title: "Try it",
    description: "Try clean examples, borderline cases, and obfuscated variants against the same policy rubric and risk scorer.",
    featured: true,
  },
  {
    id: "assurance",
    label: "What breaks",
    subtitle: "Proof, and published mistakes",
    group: "",
    title: "What breaks",
    description: "Authored suites that pass 100% prove only that the boundary holds. This is what the system actually gets wrong, published on purpose.",
    featured: true,
  },
  {
    id: "intel",
    label: "Campaigns",
    subtitle: "Campaigns and real-world fraud",
    group: "Appendix",
    title: "Intelligence",
    description: "Campaign infrastructure graphing across posts, and the documented fraud landscape this system models.",
  },
  {
    id: "operations",
    label: "At scale",
    subtitle: "Queues, staffing, incidents",
    group: "Appendix",
    title: "Operations",
    description: "Queue health, reviewer calibration, incident response, and what every threshold costs at 50,000 posts a day.",
  },
  {
    id: "govern",
    label: "Accountability",
    subtitle: "Appeals, audits, transparency",
    group: "Appendix",
    title: "Governance",
    description: "Notices, appeals, reversals, transparency reporting, and the model audit trail.",
  },
  {
    id: "system",
    label: "The full system",
    subtitle: "Methods and operating artifacts",
    group: "",
    title: "The full system",
    description: "The underlying policy, evaluations, investigations, operations, and governance artifacts.",
    featured: true,
  },
];

const SUBTAB_DEFS = {
  assurance: [
    { id: "failures", label: "Published failures" },
    { id: "evals", label: "Evaluation record" },
    { id: "llm", label: "LLM evidence" },
    { id: "agentic", label: "Agentic pressure tests" },
  ],
  intel: [
    { id: "campaigns", label: "Campaign Graph" },
    { id: "threat", label: "Threat Landscape" },
  ],
  operations: [
    { id: "ops", label: "Ops Analytics" },
    { id: "scale", label: "Scale & Capacity" },
    { id: "qa", label: "QA Calibration" },
    { id: "incidents", label: "Incident Response" },
  ],
  govern: [
    { id: "governance", label: "Appeals & Transparency" },
    { id: "model", label: "Model Audit" },
  ],
};

function resolveTarget(rawId) {
  const id = moduleHashAliases[rawId] || rawId;
  if (consoleModules.some((module) => module.id === id)) {
    return { module: id, subtab: null };
  }
  for (const [parent, tabs] of Object.entries(SUBTAB_DEFS)) {
    if (tabs.some((tab) => tab.id === id)) {
      return { module: parent, subtab: id };
    }
  }
  return { module: "welcome", subtab: null };
}

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
  falsePositives: errorAnalysis.summary?.falsePositiveCount ?? 8,
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
    label: "Space out letters",
    apply: (text) =>
      text
        .replace(/\bwallet\b/gi, "w a l l e t")
        .replace(/\bconnect\b/gi, "c o n n e c t")
        .replace(/\bclaim\b/gi, "c l a i m")
        .replace(/\bairdrop\b/gi, "a i r d r o p"),
  },
  {
    id: "leet",
    label: "Swap lookalike characters",
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
    label: "Defang the link",
    apply: (text) => {
      const defanged = text
        .replace(/https?:\/\//gi, "hxxps://")
        .replace(/\b([a-z0-9-]+)\.(xyz|top|click|cash|net|io|com)\b/gi, "$1[.]$2");
      return defanged === text ? `${text} hxxps://secure-claim[.]xyz` : defanged;
    },
  },
  {
    id: "ocr",
    label: "Move the ask into an image",
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

function targetFromHash(hash = window.location.hash) {
  const key = String(hash || "#welcome").replace(/^#/, "") || "welcome";
  return resolveTarget(key);
}

function applyTarget(target) {
  state.activeModule = target.module;
  if (target.subtab) {
    state.subTabs[target.module] = target.subtab;
  }
}

function activeModule() {
  return consoleModules.find((module) => module.id === state.activeModule) || consoleModules[0];
}

function scrollToConsoleTop() {
  window.requestAnimationFrame(() => window.scrollTo(0, 0));
  window.setTimeout(() => window.scrollTo(0, 0), 0);
  window.setTimeout(() => window.scrollTo(0, 0), 80);
}

function activateModule(rawId, updateHash = true) {
  const target = resolveTarget(rawId);
  if (target.module !== "tester") stopLiveRadar();
  applyTarget(target);
  if (updateHash) {
    window.history.replaceState(null, "", `#${rawId}`);
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

configureLiveRadar(scoreText);

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

function queueDisplayTitle(item) {
  return `${friendlyName(item)} <small class="case-id">${escapeHtml(item.id)}</small>`;
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
        <strong>${escapeHtml(friendlyName(item))}</strong>
        <span>${escapeHtml(item.id)} &middot; ${labelForGroundTruth(item.groundTruth)}</span>
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
          <h2>${state.selectedMode === "custom" ? "Live post tester" : escapeHtml(friendlyName(item))}</h2>
          <span>${state.selectedMode === "custom" ? "draft" : `${escapeHtml(item.id)} &middot; ${escapeHtml(item.split)} set &middot; ground truth: ${labelForGroundTruth(item.groundTruth)}`}</span>
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
  const extraPresets = scenarioTexts.filter(
    (scenario) => !heroPresets.some((preset) => preset.text === scenario.text),
  );
  return `
    <section class="panel tester-panel" id="tester">
      <div class="section-label">Try a post</div>
      <p class="panel-intro">The verdict updates as you type. Change the context, then watch how the same scam vocabulary can mean something different.</p>
      <textarea id="custom-text" rows="6">${escapeHtml(state.customText)}</textarea>
      <div class="hero-presets tester-presets" aria-label="Example posts">
        ${heroPresets
          .map(
            (preset) => `
              <button type="button" class="hero-preset ${state.customText === preset.text ? "active" : ""}" data-tester-preset="${escapeHtml(preset.id)}">
                ${escapeHtml(preset.label)}
              </button>
            `,
          )
          .join("")}
        ${extraPresets
          .map(
            (preset) => `
              <button type="button" class="hero-preset ${state.customText === preset.text ? "active" : ""}" data-tester-preset="${escapeHtml(preset.id)}">
                ${escapeHtml(preset.label)}
              </button>
            `,
          )
          .join("")}
      </div>
      <div class="mutation-row" aria-label="Evasion experiments">
        ${testerMutations
          .map(
            (mutation) => `
              <button type="button" data-mutation="${escapeHtml(mutation.id)}">${escapeHtml(mutation.label)}</button>
            `,
          )
          .join("")}
      </div>
      <section class="tester-verdict" aria-live="polite">
        <div class="section-label">Verdict</div>
        <div id="custom-result">${renderHeroResult(state.customText)}</div>
      </section>
    </section>
  `;
}

function renderMetrics(metrics, curvePoints) {
  return `
    <section class="panel metrics-panel" id="metrics">
      <div class="section-label">Threshold tuning</div>
      <p class="metric-provenance">Browser rubric simulator for exploration. The held-out v2 artifact is reported separately in the model audit.</p>
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
      <div class="in-progress-strip" aria-label="In progress, gated work">
        <strong>In progress, gated</strong>
        <a href="https://github.com/AliHasan-786/crypto-scam-moderation-lab/blob/main/audit_outputs/reviewer_assist_red_team.md" target="_blank" rel="noreferrer">Reviewer-assistant red team: deterministic pilot, 12 cases, one protected-context route kept open.</a>
        <a href="https://github.com/AliHasan-786/crypto-scam-moderation-lab/blob/main/model_comparison/PREREGISTRATION.md" target="_blank" rel="noreferrer">Guard-model comparison: preregistered; awaiting approved model access.</a>
        <a href="https://github.com/AliHasan-786/crypto-scam-moderation-lab/blob/main/docs/SHADOW_SERVICE_GATE_BRIEF.md" target="_blank" rel="noreferrer">Shadow service: build-only by decision; controls tested, no live collection.</a>
      </div>
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
      <div class="section-label">Annotated examples</div>
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
      <div class="queue-count">${queue.length} examples in this view</div>
      <div class="queue-list">
        ${queue.length ? queue.map((item) => renderQueueItem(item, selected)).join("") : "<p>No cases match this queue.</p>"}
      </div>
    </section>
  `;
}

function renderProjectPrimer() {
  return `
    <section class="project-primer" id="overview">
      <section class="story-artifact" aria-labelledby="artifact-title">
        <div class="primer-case-file">
          <span>Held-out test artifact</span>
          <h2 id="artifact-title">The system catches every held-out scam. It still gets eight legitimate posts wrong.</h2>
          <div class="snapshot-grid">
            <div><strong>${reportedMetrics.testRows}</strong><small>test posts</small></div>
            <div><strong>${percentage(reportedMetrics.fraudRecall)}</strong><small>fraud recall</small></div>
            <div><strong>${reportedMetrics.falsePositives}</strong><small>false positives</small></div>
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
            This is the reproducible v2 held-out artifact, not the adjustable browser simulator.
            The goal is not one model score: it is deciding when to label, review, or leave speech alone.
          </p>
        </div>
      </section>

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

      <section class="welcome-provenance story-provenance">
        <div class="section-label">Provenance</div>
        <p>
          Started as Cornell Tech Trust &amp; Safety coursework (CS 5342); rebuilt solo into this system after
          auditing the original model and finding its evaluation flaws. The
          <a href="${REPO_URL}" target="_blank" rel="noopener">repository</a> contains the policy pack,
          eval suites, decision log, and release gate. Deliberate limits: sanitized public data, no enforcement
          capability, and no tracking of visitors.
        </p>
      </section>
    </section>
  `;
}

const REPO_URL = "https://github.com/AliHasan-786/crypto-scam-moderation-lab";

const PLAIN_ACTION_EXPLAINER = {
  "Block pending reviewer confirmation": {
    tone: "bad",
    plain: "Strong scam evidence. A human reviewer confirms before anything becomes public.",
  },
  "Interstitial plus downrank": {
    tone: "bad",
    plain: "High risk: shown behind a warning screen and ranked lower while review happens.",
  },
  "Potential Crypto Fraud label": {
    tone: "bad",
    plain: "Enough evidence for a public warning label - after a human confirms it.",
  },
  "Human review queue": {
    tone: "warn",
    plain: "The system is not sure, so it asks a human instead of guessing.",
  },
  "No label": {
    tone: "good",
    plain: "No scam evidence. The post is left completely alone.",
  },
};

function friendlyName(item) {
  const top = (item.ruleResults || [])
    .filter((rule) => rule.matched)
    .sort((a, b) => b.weight - a.weight)[0];
  return top
    ? top.label
    : item.groundTruth === 1
      ? "Suspicious post"
      : "Ordinary post";
}

const heroPresets = [
  {
    id: "hero-scam",
    label: "An obvious scam",
    text: "Elon Musk is giving away 1000 ETH to celebrate. Send 0.1 ETH to our verified wallet and get 0.5 ETH back instantly.",
  },
  {
    id: "hero-warning",
    label: "A warning about scams",
    text: "PSA: do NOT send crypto to anyone promising to double it. These giveaway posts are scams. Report and move on.",
  },
  {
    id: "hero-satire",
    label: "A joke",
    text: "I am obviously not the CEO of Bitcoin, but if you send me one imaginary coin I will send back two imaginary coins.",
  },
  {
    id: "hero-skeptic",
    label: "A skeptical question",
    text: "A platform is promising 10% monthly returns on stablecoin deposits. Claims to be licensed offshore. I can't verify anything about them.",
  },
];

const HERO_STANCES = {
  satire: {
    chip: "Stance: joke / satire",
    decision: "No label",
    tone: "good",
    explain:
      "The doubling structure is there, but the assets are imaginary and the authority claim negates itself. Satire is a protected context: no real funds are solicited, so the system leaves it alone.",
  },
  helpseek: {
    chip: "Stance: asking for help",
    decision: "No label",
    tone: "good",
    explain:
      "This is a victim (or potential victim) asking for help. Enforcing here would silence exactly the people the policy protects - the system routes them to support, never to enforcement.",
  },
  protective: {
    chip: "Stance: warning others",
    decision: "No label",
    tone: "good",
    explain:
      "Scam vocabulary, protective intent. The speaker is warning people, not soliciting them. Warnings are the platform's allies - punishing them is the worst failure this system can make.",
  },
  reportage: {
    chip: "Stance: describing, not promoting",
    decision: "Human review queue",
    tone: "warn",
    explain:
      "Here is the honest part: the lexical risk score is HIGH, because this post quotes a scam's own claims. A keyword system would label it. Stance analysis notices the speaker is describing and doubting - so it goes to a human, never straight to a public label. This is the system's hardest class; see Error Analysis for the real false positives it produces.",
  },
};

function heroStance(text) {
  const lower = text.toLowerCase();
  if (/imaginary|obviously not the|obviously a joke|trust me bro/.test(lower)) return "satire";
  if (/what do i (even )?do|did i (just )?get scammed|how do i report|i think i got scammed|i feel so stupid|he won'?t listen/.test(lower)) return "helpseek";
  if (/\bpsa\b|do not send|do not connect|don'?t send|don'?t connect|beware|report and move on|these .{0,40}are scams|stay safe/.test(lower)) return "protective";
  if (/can'?t verify|cannot verify|haven'?t verified|claims? to be licensed|they claim|not sure if|is it legit|anyone (else )?(used|tried)|i saw an ad|no idea if/.test(lower)) return "reportage";
  return null;
}

function renderHeroResult(text) {
  const heroResult = scoreText(text);
  const stanceKey = heroStance(text);
  const stance = stanceKey ? HERO_STANCES[stanceKey] : null;
  const decision = stance ? stance.decision : heroResult.action;
  const tone = stance ? stance.tone : (PLAIN_ACTION_EXPLAINER[heroResult.action] || { tone: "warn" }).tone;
  const explain = stance ? stance.explain : (PLAIN_ACTION_EXPLAINER[heroResult.action] || { plain: "" }).plain;
  const matched = heroResult.ruleResults.filter((rule) => rule.matched).slice(0, 4);
  return `
    <div class="hero-result hero-result-${tone}">
      <div class="hero-result-head">
        <span class="hero-decision">${escapeHtml(decision)}</span>
        <span class="hero-risk" title="Raw keyword-evidence score, before stance and context are considered">lexical risk ${percentage(heroResult.score)}</span>
      </div>
      ${stance ? `<span class="stance-chip stance-${tone}">${escapeHtml(stance.chip)}</span>` : ""}
      <p>${escapeHtml(explain)}</p>
      ${
        matched.length
          ? `<div class="hero-evidence">${matched
              .map(
                (rule) =>
                  `<span class="hero-evidence-chip">${escapeHtml(rule.label)} +${Math.round(rule.weight * 100)}</span>`,
              )
              .join("")}</div>`
          : `<div class="hero-evidence"><span class="hero-evidence-chip neutral">No policy evidence matched</span></div>`
      }
    </div>
  `;
}

function renderWelcome() {
  const sim = scaleSimulation || {};
  const opPoint = sim.operatingPoint || {};
  const errSummary = (errorAnalysis && errorAnalysis.summary) || {};
  return `
    <div class="welcome-shell">
      <section class="welcome-hero panel">
        <span class="welcome-kicker">Crypto Scam Moderation Lab</span>
        <h1>Can a platform catch crypto scams without silencing everyone who talks about them?</h1>
        <p class="welcome-lede">
          Scammers, journalists, victims, comedians, and researchers all use the same words.
          This is a working moderation system that draws that boundary: it turns a written policy
          into evidence, sends uncertainty to people, and makes its mistakes inspectable. Everything
          runs in your browser on sanitized examples.
        </p>
        <div class="welcome-stats">
          <div class="welcome-stat">
            <strong>3 outcomes</strong>
            <span>Label only with strong evidence. Review uncertainty. Leave protected speech alone.</span>
          </div>
          <div class="welcome-stat">
            <strong>${errSummary.falsePositiveCount ?? 8} mistakes</strong>
            <span>False positives published and explained instead of hidden.</span>
          </div>
          <div class="welcome-stat">
            <strong>${errSummary.unsolvedStillFailing ?? 5} open questions</strong>
            <span>Hard cases still failing, kept visible as the next work to do.</span>
          </div>
        </div>
        <div class="welcome-paths">
          <button type="button" class="path-card" data-scroll-story>
            <strong>Read the policy</strong>
            <span>The original proposal, distilled into the decisions this system makes.</span>
          </button>
          <button type="button" class="path-card" data-goto="tester">
            <strong>Try the boundary</strong>
            <span>Test a post and see the evidence that changes a decision.</span>
          </button>
          <button type="button" class="path-card" data-goto="failures">
            <strong>See what breaks</strong>
            <span>The published mistakes and deliberately unsolved cases.</span>
          </button>
        </div>
      </section>

      <section class="panel welcome-tester" id="hero-tester">
        <div class="section-label">Try it yourself</div>
        <h2>Paste any post. The verdict updates as you type.</h2>
        <p class="welcome-hint">The same words appear in a scam and in a warning about that scam. The score alone can't tell them apart - stance can. Try all four:</p>
        <div class="hero-presets">
          ${heroPresets
            .map(
              (preset) => `
                <button type="button" class="hero-preset ${state.heroText === preset.text ? "active" : ""}" data-hero-preset="${escapeHtml(preset.id)}">
                  ${escapeHtml(preset.label)}
                </button>
              `,
            )
            .join("")}
        </div>
        <textarea id="hero-text" rows="3" aria-label="Post text to evaluate">${escapeHtml(state.heroText)}</textarea>
        <div id="hero-result">${renderHeroResult(state.heroText)}</div>
      </section>

      <section class="panel welcome-how">
        <div class="section-label">How it works</div>
        <div class="how-steps">
          <div class="how-step"><span>1</span><strong>A post arrives</strong><p>Real systems see millions a day. This demo simulates that stream with sanitized data.</p></div>
          <div class="how-step"><span>2</span><strong>Evidence, not vibes</strong><p>A written policy turns into scored evidence: transfer asks, fake authority, impossible returns.</p></div>
          <div class="how-step"><span>3</span><strong>Three-way decision</strong><p>Strong evidence &rarr; label candidate. Uncertainty &rarr; human review. No evidence &rarr; leave it alone.</p></div>
          <div class="how-step"><span>4</span><strong>Humans stay in charge</strong><p>Reviewers confirm every label. Users get notices and appeals. Mistakes get published.</p></div>
        </div>
      </section>

    </div>
  `;
}

function renderErrorAnalysisPanel() {
  const summary = errorAnalysis.summary || {};
  const categories = errorAnalysis.falsePositiveCategories || {};
  return `
    <section class="panel error-analysis-panel" id="error-analysis">
      <div class="section-label">Standing error analysis</div>
      <p class="panel-intro">
        Authored eval suites that pass 100% are indistinguishable from suites written to pass.
        This page is the antidote: the system's real mistakes on held-out data, plus hard cases it
        still fails, kept public on purpose (Decision Log 010).
      </p>
      <div class="stat-grid">
        <div class="stat-card"><strong>${summary.falsePositiveCount ?? 0}</strong><span>false positives at the operating point</span></div>
        <div class="stat-card"><strong>${summary.missCount ?? 0}</strong><span>scams missed entirely</span></div>
        <div class="stat-card"><strong>${summary.unsolvedStillFailing ?? 0}/${summary.unsolvedTotal ?? 0}</strong><span>hard cases still failing</span></div>
        <div class="stat-card ${summary.guardsPassing ? "good" : "bad"}"><strong>${summary.guardsPassing ? "Pass" : "FAIL"}</strong><span>protected-context guards</span></div>
      </div>
      <h3>The false positives, by class</h3>
      ${Object.entries(categories)
        .map(
          ([category, count]) => `
            <details class="fp-category">
              <summary><strong>${escapeHtml(humanize(category))}</strong><span>${count} case${count === 1 ? "" : "s"}</span></summary>
              <p>${escapeHtml((errorAnalysis.categoryCommentary || {})[category] || "")}</p>
              ${(errorAnalysis.falsePositives || [])
                .filter((fp) => fp.category === category)
                .map(
                  (fp) => `
                    <blockquote class="fp-quote">
                      <p>${escapeHtml(fp.text)}</p>
                      <footer>score ${percentage(fp.score)} &middot; ${escapeHtml(humanize(fp.action))}</footer>
                    </blockquote>
                  `,
                )
                .join("")}
            </details>
          `,
        )
        .join("")}
      <h3>Unsolved hard cases</h3>
      <p class="panel-intro">
        When one of these starts passing, it gets promoted into the regression suite and replaced
        with something harder. Failures are the roadmap.
      </p>
      <div class="unsolved-list">
        ${(errorAnalysis.unsolvedCases || [])
          .map(
            (item) => `
              <div class="unsolved-card status-${item.status === "pass" ? "pass" : "fail"}">
                <div class="unsolved-head">
                  <strong>${escapeHtml(humanize(item.category))}</strong>
                  <span class="status-chip ${item.status === "pass" ? "good" : "bad"}">${escapeHtml(item.status)}</span>
                </div>
                <blockquote>${escapeHtml(item.text)}</blockquote>
                <div class="unsolved-actions">
                  <span>expected: <b>${escapeHtml(humanize(item.expectedAction))}</b></span>
                  <span>actual: <b>${escapeHtml(humanize(item.actualAction))}</b></span>
                </div>
                <p>${escapeHtml(item.rationale)}</p>
                ${item.knownBlindSpot ? `<p class="blind-spot">Blind spot: ${escapeHtml(item.knownBlindSpot)}</p>` : ""}
              </div>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderLlmComparisonPanel() {
  const rows = llmComparison.perCase || [];
  const disagreements = rows.filter((row) => !row.agree);
  const showdown = llmComparison.stanceShowdown || [];
  return `
    <section class="panel llm-panel" id="llm-comparison">
      <div class="section-label">Where a language model earns its cost</div>
      <p class="panel-intro showdown-intro">
        The cheap baseline's worst real failure mode is <b>stance blindness</b>: people describing
        scams get scored like people running them. Below are actual false positives from the held-out
        test set - the baseline's real verdict on the left, a language model's stance reading on the
        right. This one distinction is the argument for LLM assistance; everything else on this page
        is supporting detail.
      </p>
      ${showdown
        .map(
          (item) => `
            <div class="showdown-card">
              <blockquote>${escapeHtml(item.text)}</blockquote>
              <div class="showdown-verdicts">
                <div class="verdict bad">
                  <span>Baseline (keywords) - real verdict</span>
                  <strong>${escapeHtml(humanize(item.baselineAction))} at ${percentage(item.baselineScore)} risk</strong>
                </div>
                <div class="verdict good">
                  <span>LLM (stance reading)</span>
                  <strong>${escapeHtml(item.llmStance)} &rarr; ${escapeHtml(humanize(item.llmVerdict))}</strong>
                </div>
              </div>
              <p class="showdown-note">${escapeHtml(item.llmAnalysis)}</p>
            </div>
          `,
        )
        .join("")}
      <h3>So why not use the LLM for everything?</h3>
      <div class="cost-grid">
        <div><span>Baseline</span><strong>${escapeHtml((llmComparison.costModel || {}).baselinePer1kPosts || "")}</strong></div>
        <div><span>Hosted LLM</span><strong>${escapeHtml((llmComparison.costModel || {}).llmPer1kPosts || "")}</strong></div>
        <div><span>Latency</span><strong>${escapeHtml((llmComparison.costModel || {}).llmLatencyPerPost || "")}</strong></div>
      </div>
      <p class="panel-intro">${escapeHtml((llmComparison.costModel || {}).operationalNote || "")}</p>
      <h3>An unresolved disagreement, kept on purpose</h3>
      ${
        disagreements.length
          ? disagreements
              .map(
                (row) => `
                  <div class="disagreement-card">
                    <strong>${escapeHtml(row.caseId)}</strong>
                    <div class="unsolved-actions">
                      <span>suite expects: <b>${escapeHtml(humanize(row.expected))}</b></span>
                      <span>baseline: <b>${escapeHtml(humanize(row.baseline))}</b></span>
                      <span>LLM: <b>${escapeHtml(humanize(row.llm))}</b></span>
                    </div>
                    <p>${escapeHtml(row.reviewerSummary || "")}</p>
                    <p class="showdown-note">The eval suite says route this help-seeker to review; the model declined to burden a likely victim. Both positions are defensible - it is a live policy question, so the disagreement stays visible instead of being tuned away.</p>
                  </div>
                `,
              )
              .join("")
          : "<p>Full agreement on the current suite.</p>"
      }
      <details class="llm-table-details">
        <summary>Boundary-suite agreement detail (${rows.length} authored cases - encodes policy, not a benchmark)</summary>
        <p class="panel-intro">
          Provider: ${escapeHtml(llmComparison.provider || "")}. Both systems are checked against the
          authored boundary suite; high agreement here means both respect the encoded policy line.
          It is deliberately NOT presented as a performance benchmark - for real failures, see Error Analysis.
        </p>
        <div class="stat-grid">
          <div class="stat-card"><strong>${percentage(llmComparison.baselineExpectationPassRate || 0)}</strong><span>baseline boundary conformance</span></div>
          <div class="stat-card"><strong>${percentage(llmComparison.llmExpectationPassRate || 0)}</strong><span>LLM boundary conformance</span></div>
          <div class="stat-card"><strong>${percentage(llmComparison.actionAgreementRate || 0)}</strong><span>action agreement</span></div>
          <div class="stat-card"><strong>${percentage(llmComparison.spanFaithfulnessRate || 0)}</strong><span>span faithfulness (hard gate: every claim must quote the source)</span></div>
        </div>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Case</th><th>Expected</th><th>Baseline</th><th>LLM</th></tr></thead>
            <tbody>
              ${rows
                .map(
                  (row) => `
                    <tr class="${row.agree ? "" : "row-disagree"}">
                      <td>${escapeHtml(row.caseId)}</td>
                      <td>${escapeHtml(humanize(row.expected))}</td>
                      <td>${escapeHtml(humanize(row.baseline))}${row.baselinePass ? "" : " &#10060;"}</td>
                      <td>${escapeHtml(humanize(row.llm))}${row.llmPass ? "" : " &#10060;"}</td>
                    </tr>
                  `,
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  `;
}

function renderScalePanel() {
  const sweep = scaleSimulation.thresholdSweep || [];
  const weeks = scaleSimulation.weeklySeries || [];
  const assumptions = scaleSimulation.assumptions || {};
  const op = scaleSimulation.operatingPoint || {};
  const maxReviewers = Math.max(...sweep.map((row) => row.reviewersNeeded), 1);
  const chartW = 560;
  const chartH = 190;
  const barW = chartW / sweep.length;
  const maxQueue = Math.max(...weeks.map((week) => week.reviewQueue), 1);
  const weekBarW = 560 / weeks.length;
  return `
    <section class="panel scale-panel" id="scale-capacity">
      <div class="section-label">Scale &amp; capacity</div>
      <p class="panel-intro">
        Everything else in this lab works on hundreds of posts. This module asks what the thresholds
        cost at ${((scaleSimulation.corpus || {}).dailyVolume || 50000).toLocaleString()} posts/day:
        every threshold choice is a staffing decision with a payroll number attached.
      </p>
      <div class="stat-grid">
        <div class="stat-card"><strong>${percentage((scaleSimulation.corpus || {}).truePrevalence || 0)}</strong><span>true scam prevalence (knowable because synthetic)</span></div>
        <div class="stat-card"><strong>${op.reviewersNeededAtOperatingPoint ?? "-"}</strong><span>reviewers needed at the operating point</span></div>
        <div class="stat-card"><strong>${percentage(op.falseLabelShareOnLegit || 0)}</strong><span>legit posts reaching label-candidate stage</span></div>
        <div class="stat-card"><strong>${assumptions.decisionsPerReviewerDay ?? "-"}</strong><span>decisions per reviewer per day (90s handle time)</span></div>
      </div>
      <h3>The threshold sweep: recall vs payroll</h3>
      <svg viewBox="0 0 ${chartW + 60} ${chartH + 46}" class="sweep-chart" role="img" aria-label="Reviewers needed and review-net recall by threshold">
        ${sweep
          .map((row, index) => {
            const barH = (row.reviewersNeeded / maxReviewers) * (chartH - 20);
            return `
              <rect x="${30 + index * barW + 6}" y="${chartH - barH}" width="${barW - 12}" height="${barH}" class="sweep-bar" />
              <text x="${30 + index * barW + barW / 2}" y="${chartH + 16}" class="chart-tick" text-anchor="middle">${row.threshold.toFixed(2)}</text>
              <text x="${30 + index * barW + barW / 2}" y="${chartH - barH - 6}" class="chart-value" text-anchor="middle">${row.reviewersNeeded}</text>
            `;
          })
          .join("")}
        <polyline
          class="sweep-recall-line"
          points="${sweep
            .map(
              (row, index) =>
                `${30 + index * barW + barW / 2},${chartH - row.reviewNetRecall * (chartH - 20)}`,
            )
            .join(" ")}"
        />
        <text x="${chartW - 80}" y="16" class="chart-legend">&#9632; reviewers</text>
        <text x="${chartW - 80}" y="34" class="chart-legend recall">&#9472; recall</text>
        <text x="30" y="${chartH + 38}" class="chart-tick">review threshold &rarr;</text>
      </svg>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Threshold</th><th>Queue/day</th><th>Review-net recall</th><th>Reviewers</th><th>Daily cost</th><th>Cost per caught scam</th></tr></thead>
          <tbody>
            ${sweep
              .map(
                (row) => `
                  <tr class="${row.threshold === 0.4 ? "row-operating" : ""}">
                    <td>${row.threshold.toFixed(2)}${row.threshold === 0.4 ? " (policy floor)" : ""}</td>
                    <td>${row.queuePerDay.toLocaleString()}</td>
                    <td>${percentage(row.reviewNetRecall)}</td>
                    <td>${row.reviewersNeeded}</td>
                    <td>$${row.dailyReviewCost.toLocaleString()}</td>
                    <td>$${row.costPerCaughtScam.toLocaleString()}</td>
                  </tr>
                `,
              )
              .join("")}
          </tbody>
        </table>
      </div>
      <h3>Twelve weeks, two campaign waves</h3>
      <p class="panel-intro">Point-in-time metrics mislead. The waves in weeks 5 and 9 show why burst capacity - not steady state - is the real staffing problem, and why the incident runbook exists.</p>
      <svg viewBox="0 0 620 170" class="weeks-chart" role="img" aria-label="Weekly review queue with campaign waves">
        ${weeks
          .map((week, index) => {
            const barH = (week.reviewQueue / maxQueue) * 120;
            return `
              <rect x="${20 + index * weekBarW + 4}" y="${140 - barH}" width="${weekBarW - 8}" height="${barH}" class="week-bar ${week.campaignWave ? "wave" : ""}" />
              <text x="${20 + index * weekBarW + weekBarW / 2}" y="156" class="chart-tick" text-anchor="middle">W${week.week}</text>
            `;
          })
          .join("")}
      </svg>
      <p class="panel-intro">${escapeHtml(scaleSimulation.interpretation || "")}</p>
    </section>
  `;
}

function renderThreatPanel() {
  return `
    <section class="panel threat-panel" id="threat-landscape">
      <div class="section-label">Threat landscape</div>
      <p class="panel-intro">
        The eval cases in this lab are authored, but the behaviors they encode are not invented.
        Every violation subtype maps to fraud typologies documented by the FBI's IC3, Chainalysis,
        and the FTC. Figures as reported by sources; verified July 2026.
      </p>
      <div class="stat-grid threat-stats">
        ${(threatLandscape.headline || [])
          .map(
            (stat) => `
              <div class="stat-card">
                <strong>${escapeHtml(stat.value)}</strong>
                <span>${escapeHtml(stat.label)}</span>
                <small>${escapeHtml(stat.detail)} <em>${escapeHtml(stat.source)}</em></small>
              </div>
            `,
          )
          .join("")}
      </div>
      <h3>Documented typology &rarr; what this system sees &rarr; what it cannot</h3>
      <div class="typology-list">
        ${(threatLandscape.typologies || [])
          .map(
            (typology) => `
              <details class="typology-card">
                <summary><strong>${escapeHtml(typology.name)}</strong><span>${escapeHtml(typology.labSubtype)}</span></summary>
                <p><b>Documented:</b> ${escapeHtml(typology.documented)}</p>
                <p><b>Detected here via:</b> ${escapeHtml(typology.detects)}</p>
                <p class="blind-spot"><b>Blind spot:</b> ${escapeHtml(typology.blindSpot)}</p>
              </details>
            `,
          )
          .join("")}
      </div>
      <h3>What the landscape implies</h3>
      ${(threatLandscape.productImplications || []).map((implication) => `<p class="implication">${escapeHtml(implication)}</p>`).join("")}
    </section>
  `;
}

function computeNetworkLayout() {
  const entityNodes = (campaignGraph.topEntities || []).map((entity) => ({
    id: entity.id,
    label: entity.type === "wallet" ? compactEntity(entity.label) : entity.label,
    type: entity.type,
    shared: entity.shared,
    kind: "entity",
  }));
  const itemIds = new Set();
  (campaignGraph.edges || []).forEach((edge) => itemIds.add(edge.target));
  const itemNodes = Array.from(itemIds).map((id) => ({
    id,
    label: id.split("/").pop().replace(/-/g, " "),
    type: "post",
    kind: "item",
  }));
  const nodes = [...entityNodes, ...itemNodes];
  const index = new Map(nodes.map((node, position) => [node.id, position]));
  const links = (campaignGraph.edges || [])
    .filter((edge) => index.has(edge.source) && index.has(edge.target))
    .map((edge) => ({ source: index.get(edge.source), target: index.get(edge.target) }));

  const width = 620;
  const height = 380;
  const rand = (seed) => {
    let value = seed;
    return () => {
      value = (value * 1103515245 + 12345) % 2147483648;
      return value / 2147483648;
    };
  };
  const random = rand(5342);
  nodes.forEach((node) => {
    node.x = 60 + random() * (width - 120);
    node.y = 50 + random() * (height - 100);
    node.vx = 0;
    node.vy = 0;
  });
  for (let iteration = 0; iteration < 260; iteration += 1) {
    for (let a = 0; a < nodes.length; a += 1) {
      for (let b = a + 1; b < nodes.length; b += 1) {
        const dx = nodes[b].x - nodes[a].x;
        const dy = nodes[b].y - nodes[a].y;
        const distSq = Math.max(80, dx * dx + dy * dy);
        const force = 2600 / distSq;
        const dist = Math.sqrt(distSq);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        nodes[a].vx -= fx;
        nodes[a].vy -= fy;
        nodes[b].vx += fx;
        nodes[b].vy += fy;
      }
    }
    links.forEach((link) => {
      const source = nodes[link.source];
      const target = nodes[link.target];
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const dist = Math.max(1, Math.sqrt(dx * dx + dy * dy));
      const pull = (dist - 92) * 0.02;
      const fx = (dx / dist) * pull;
      const fy = (dy / dist) * pull;
      source.vx += fx;
      source.vy += fy;
      target.vx -= fx;
      target.vy -= fy;
    });
    nodes.forEach((node) => {
      node.vx += (width / 2 - node.x) * 0.004;
      node.vy += (height / 2 - node.y) * 0.004;
      node.x = Math.min(width - 30, Math.max(30, node.x + node.vx * 0.5));
      node.y = Math.min(height - 24, Math.max(24, node.y + node.vy * 0.5));
      node.vx *= 0.62;
      node.vy *= 0.62;
    });
  }
  return { nodes, links, width, height };
}

let cachedNetworkLayout = null;

function renderCampaignNetwork() {
  if (!cachedNetworkLayout) {
    cachedNetworkLayout = computeNetworkLayout();
  }
  const { nodes, links, width, height } = cachedNetworkLayout;
  return `
    <section class="panel network-panel" id="campaign-network">
      <div class="section-label">Campaign network</div>
      <p class="panel-intro">
        Scam campaigns rotate accounts faster than they rotate infrastructure. Wallets, domains, and
        recycled phrasing connect posts that look unrelated one at a time.
      </p>
      <svg viewBox="0 0 ${width} ${height}" class="network-svg" role="img" aria-label="Campaign graph: posts connected by shared wallets, domains, and phrases">
        ${links
          .map(
            (link) =>
              `<line x1="${nodes[link.source].x.toFixed(1)}" y1="${nodes[link.source].y.toFixed(1)}" x2="${nodes[link.target].x.toFixed(1)}" y2="${nodes[link.target].y.toFixed(1)}" class="network-link" />`,
          )
          .join("")}
        ${nodes
          .map(
            (node) => `
              <g class="network-node node-${node.type} ${node.shared ? "shared" : ""}">
                <circle cx="${node.x.toFixed(1)}" cy="${node.y.toFixed(1)}" r="${node.kind === "item" ? 13 : node.shared ? 10 : 7}" />
                <text x="${node.x.toFixed(1)}" y="${(node.y + (node.kind === "item" ? 26 : 21)).toFixed(1)}" text-anchor="middle">${escapeHtml(node.label.length > 22 ? node.label.slice(0, 20) + "…" : node.label)}</text>
              </g>
            `,
          )
          .join("")}
      </svg>
      <div class="network-legend">
        <span class="legend-item post">post</span>
        <span class="legend-item wallet">wallet</span>
        <span class="legend-item domain">domain</span>
        <span class="legend-item risk_phrase">risk phrase</span>
        <span class="legend-item brand">brand</span>
        <span class="legend-item actor">handle</span>
        <span class="legend-item sharednote">larger = shared across posts</span>
      </div>
    </section>
  `;
}

const tourSteps = [
  {
    module: "welcome",
    title: "What this is",
    body: "A working crypto-scam moderation system built from a written policy. The hard part is not catching scams - it is not catching everyone else. Use Next to walk through it.",
  },
  {
    module: "queue",
    title: "The review queue",
    body: "Every flagged post lands here ranked by risk, with the evidence shown, not hidden. Click any case on the left to see exactly why the system scored it.",
  },
  {
    module: "tester",
    title: "Try to fool it",
    body: "Paste anything, or hit the obfuscation buttons (leetspeak, spacing, defanged links) to attack the system the way scammers do. Watch evidence and decisions change live.",
  },
  {
    module: "evals",
    title: "Proving it protects speech",
    body: "Evals here measure two different promises: scams get caught, AND warnings, satire, research, and help-seeking stay untouched. A release gate blocks any change that breaks either.",
  },
  {
    module: "failures",
    title: "What it gets wrong - in public",
    body: "Real false positives with explanations, and hard cases the system still fails, published deliberately. Failure honesty is a feature: suites that pass 100% prove nothing.",
  },
  {
    module: "llm",
    title: "Where an LLM earns its cost",
    body: "A hosted-LLM evidence assistant compared honestly against the cheap baseline: accuracy, cost, latency, and one unresolved disagreement about a help-seeker, kept visible.",
  },
  {
    module: "scale",
    title: "Thresholds are staffing decisions",
    body: "At 50,000 posts/day, moving one threshold from 0.40 to 0.30 roughly doubles reviewer payroll. This module turns model knobs into money and people.",
  },
  {
    module: "governance",
    title: "Appeals and accountability",
    body: "Every label ships with a notice and an appeal path. Reversals feed back into policy. That loop - not the classifier - is what makes a moderation system legitimate. End of tour!",
  },
];

function renderTourOverlay() {
  if (state.tourStep === null) return "";
  const step = tourSteps[state.tourStep];
  return `
    <div class="tour-overlay" role="dialog" aria-label="Guided tour">
      <div class="tour-card">
        <div class="tour-progress">Step ${state.tourStep + 1} of ${tourSteps.length}</div>
        <strong>${escapeHtml(step.title)}</strong>
        <p>${escapeHtml(step.body)}</p>
        <div class="tour-actions">
          <button type="button" data-tour="exit">Exit</button>
          <div>
            ${state.tourStep > 0 ? '<button type="button" data-tour="back">Back</button>' : ""}
            ${
              state.tourStep < tourSteps.length - 1
                ? '<button type="button" class="tour-next" data-tour="next">Next</button>'
                : '<button type="button" class="tour-next" data-tour="exit">Done</button>'
            }
          </div>
        </div>
      </div>
    </div>
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
  const featuredModules = consoleModules.filter((module) => module.featured);
  return `
    <header class="console-sidebar" aria-label="Lab navigation">
      <div class="console-brand">
        <span>Interactive case study</span>
        <strong>Crypto Scam<br />Moderation Lab</strong>
      </div>
      <nav class="console-nav" aria-label="Project sections">
        ${featuredModules
          .map((module) => {
            const isAppendix = activeModule().group === "Appendix";
            const isActive = state.activeModule === module.id || (module.id === "system" && isAppendix);
            return `
              <button
                type="button"
                class="module-button ${isActive ? "active" : ""}"
                data-module="${escapeHtml(module.id)}"
                aria-current="${isActive ? "page" : "false"}"
              >
                <span>${escapeHtml(module.label)}</span>
              </button>
            `;
          })
          .join("")}
      </nav>
      <a class="source-link" href="${REPO_URL}" target="_blank" rel="noopener">Source &amp; methods</a>
    </header>
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
      ${module.group === "Appendix" ? '<a class="appendix-link" href="#system">Appendix <span>&larr; The full system</span></a>' : module.group ? `<span>${escapeHtml(module.group)}</span>` : ""}
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

function renderSystemIndex() {
  const sections = [
    ["queue", "Case archive", "Annotated examples and the evidence behind each decision."],
    ["intel", "Campaigns", "Shared infrastructure, campaign patterns, and the threat landscape."],
    ["operations", "At scale", "Threshold tradeoffs, calibration, incidents, and capacity."],
    ["govern", "Accountability", "Appeals, notices, transparency, and the model audit."],
  ];
  return `
    <section class="system-index" aria-label="Full system appendix">
      <p class="system-index-intro">
        The public story focuses on the policy boundary and the project’s failures. These working artifacts
        hold the deeper operating detail behind that argument.
      </p>
      <div class="system-index-grid">
        ${sections
          .map(
            ([id, title, description], index) => `
              <button type="button" class="system-index-item" data-goto="${id}">
                <span>${String(index + 1).padStart(2, "0")}</span>
                <strong>${title}</strong>
                <p>${description}</p>
              </button>
            `,
          )
          .join("")}
      </div>
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
        <strong>${state.selectedMode === "custom" ? "Draft post" : escapeHtml(friendlyName(selected))}</strong>
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

function renderSubtabContent(tabId, { metrics, curvePoints, queue, selected }) {
  switch (tabId) {
    case "evals":
      return `
        <div class="caveat-banner">
          <strong>Read these numbers correctly:</strong> the suites below are authored - they encode the
          policy boundary, so passing them means the boundary holds, nothing more. 100% here is table
          stakes. Real performance lives in <button type="button" class="inline-link" data-subtab="failures">Error Analysis</button>,
          where the system's actual mistakes are published.
        </div>
        <div class="module-grid two-column">
          <div class="module-stack">
            ${renderEvalSuite()}
            ${renderHardeningEvals()}
          </div>
          <div class="module-stack">
            ${renderEvalGate()}
            ${renderAdversarialLab()}
            ${renderEvidenceExtractor()}
          </div>
        </div>
      `;
    case "failures":
      return `<div class="module-grid single-column">${renderErrorAnalysisPanel()}</div>`;
    case "llm":
      return `<div class="module-grid single-column">${renderLlmComparisonPanel()}</div>`;
    case "agentic":
      return `
        <div class="module-grid two-column">
          ${renderAgenticAbuseLab()}
          <div class="module-stack">
            ${renderEvidenceExtractor()}
            ${renderEvalGate()}
          </div>
        </div>
      `;
    case "campaigns":
      return `
        <div class="module-grid two-column">
          <div class="module-stack">
            ${renderCampaignNetwork()}
            ${renderCampaignGraph()}
            ${renderCampaignGallery()}
          </div>
          <div class="module-stack">
            ${renderLiveStore()}
            ${renderOpsAnalytics()}
          </div>
        </div>
      `;
    case "threat":
      return `<div class="module-grid single-column">${renderThreatPanel()}</div>`;
    case "ops":
      return `
        <div class="module-grid two-column">
          ${renderMetrics(metrics, curvePoints)}
          ${renderOpsAnalytics()}
        </div>
      `;
    case "scale":
      return `<div class="module-grid single-column">${renderScalePanel()}</div>`;
    case "qa":
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
    case "incidents":
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
    case "governance":
      return `
        <div class="module-grid two-column">
          ${renderGovernanceReport()}
          <div class="module-stack">
            ${renderPolicyCard()}
            ${renderQualityCalibration()}
          </div>
        </div>
      `;
    case "model":
      return `
        <div class="module-grid two-column">
          ${renderReportedModel()}
          <div class="module-stack">
            ${renderMetrics(metrics, curvePoints)}
            ${renderEvalSuite()}
          </div>
        </div>
      `;
    default:
      return "";
  }
}

function renderModuleContent(context) {
  if (state.activeModule === "welcome") {
    return `${renderWelcome()}${renderProjectPrimer()}`;
  }

  if (state.activeModule === "overview") {
    return `${renderWelcome()}${renderProjectPrimer()}`;
  }

  if (state.activeModule === "system") {
    return renderSystemIndex();
  }

  if (state.activeModule === "queue") {
    return `
      <div class="module-grid review-grid">
        ${renderQueue(context.queue, context.selected)}
        <div class="module-stack">
          ${renderSelected(context.selected)}
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
          ${renderLiveRadar(liveStreamCalibration)}
        </div>
        <div class="module-stack">
          ${renderPolicyCard()}
          ${renderEvidenceExtractor()}
          ${renderAdversarialLab()}
        </div>
      </div>
    `;
  }

  const tabs = SUBTAB_DEFS[state.activeModule];
  if (tabs) {
    const active = state.subTabs[state.activeModule] || tabs[0].id;
    return `
      <div class="subtab-bar" role="tablist" aria-label="Sections">
        ${tabs
          .map(
            (tab) => `
              <button type="button" role="tab" class="subtab ${tab.id === active ? "active" : ""}" data-subtab="${escapeHtml(tab.id)}" aria-selected="${tab.id === active}">
                ${escapeHtml(tab.label)}
              </button>
            `,
          )
          .join("")}
      </div>
      ${renderSubtabContent(active, context)}
    `;
  }

  return renderWelcome();
}

const RAIL_MODULES = new Set(["queue"]);
const SYSTEM_BAR_MODULES = new Set();

function renderConsoleWorkspace(context) {
  return `
    <main class="console-main">
      ${SYSTEM_BAR_MODULES.has(state.activeModule) ? renderSystemBar(context.metrics, context.queue, context.selected) : ""}
      <section class="console-workspace">
        ${state.activeModule === "overview" || state.activeModule === "welcome" ? "" : renderModuleHeader()}
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

  const showRail = RAIL_MODULES.has(state.activeModule);
  app.innerHTML = `
    <div class="console-shell ${showRail ? "" : "no-rail"}">
      ${renderConsoleNav()}
      ${renderConsoleWorkspace({ metrics, curvePoints, queue, selected })}
      ${showRail ? renderEvidenceRail(selected, metrics, queue) : ""}
    </div>
    ${renderTourOverlay()}
  `;

  attachEvents();
}

function attachEvents() {
  document.querySelector(".module-button.active")?.scrollIntoView({ block: "nearest", inline: "center" });
  if (state.activeModule === "tester") attachLiveRadar();

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

  document.querySelectorAll("[data-tester-preset]").forEach((button) => {
    button.addEventListener("click", () => {
      const preset = [...heroPresets, ...scenarioTexts].find((item) => item.id === button.dataset.testerPreset);
      if (preset) {
        state.customText = preset.text;
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

  document.querySelectorAll("[data-subtab]").forEach((button) => {
    button.addEventListener("click", () => {
      state.subTabs[state.activeModule] = button.dataset.subtab;
      window.history.replaceState(null, "", `#${button.dataset.subtab}`);
      render();
    });
  });

  document.querySelectorAll("[data-goto]").forEach((button) => {
    button.addEventListener("click", () => {
      activateModule(button.dataset.goto);
    });
  });

  document.querySelectorAll("[data-scroll-story]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelector("#overview")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  document.querySelectorAll("[data-tour]").forEach((button) => {
    button.addEventListener("click", () => {
      const command = button.dataset.tour;
      if (command === "start") {
        state.tourStep = 0;
      } else if (command === "next") {
        state.tourStep = Math.min(tourSteps.length - 1, state.tourStep + 1);
      } else if (command === "back") {
        state.tourStep = Math.max(0, state.tourStep - 1);
      } else {
        state.tourStep = null;
        render();
        return;
      }
      const step = tourSteps[state.tourStep];
      if (step.module !== state.activeModule) {
        activateModule(step.module);
      } else {
        render();
      }
    });
  });

  document.querySelectorAll("[data-hero-preset]").forEach((button) => {
    button.addEventListener("click", () => {
      const preset = heroPresets.find((entry) => entry.id === button.dataset.heroPreset);
      if (preset) {
        state.heroText = preset.text;
        render();
      }
    });
  });

  const heroText = document.querySelector("#hero-text");
  if (heroText) {
    heroText.addEventListener("input", () => {
      state.heroText = heroText.value;
      const container = document.querySelector("#hero-result");
      if (container) {
        container.innerHTML = renderHeroResult(state.heroText);
      }
    });
  }

  const customText = document.querySelector("#custom-text");
  if (customText) {
    customText.addEventListener("input", () => {
      state.customText = customText.value;
      const container = document.querySelector("#custom-result");
      if (container) {
        container.innerHTML = renderHeroResult(state.customText);
      }
    });
  }
}

window.addEventListener("hashchange", () => {
  const target = targetFromHash();
  const subtabNow = SUBTAB_DEFS[target.module] ? state.subTabs[target.module] : null;
  if (target.module !== state.activeModule || (target.subtab && target.subtab !== subtabNow)) {
    applyTarget(target);
    render();
    scrollToConsoleTop();
  }
});

applyTarget(targetFromHash());
render();
scrollToConsoleTop();
