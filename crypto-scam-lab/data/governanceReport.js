export const governanceReport = {
  "generatedAt": "2026-07-04T02:16:03.981609+00:00",
  "suite": "governance_transparency_v1",
  "caveat": "Operational queue metrics come from the local SQLite review store. Appeal examples are authored, sanitized portfolio scenarios that exercise notice, appeal, and reversal flows without using live user data.",
  "queueMetrics": {
    "totalCandidates": 5,
    "reviewedOrTriaged": 3,
    "actioned": 1,
    "labeled": 0,
    "escalated": 1,
    "dismissed": 1,
    "appealed": 0,
    "reversed": 0,
    "automationAssistedRate": 1.0,
    "reviewAutomationAssistedRate": 1.0,
    "statusCounts": {
      "dismissed": 1,
      "escalated": 1,
      "new": 2,
      "review": 1
    },
    "decisionCounts": {
      "fraud": 1,
      "needs_more_context": 1,
      "none": 2,
      "not_fraud": 1
    },
    "eventCounts": {
      "ingested": 5,
      "review_decision": 3,
      "upsert_duplicate": 3
    },
    "falsePositiveCategories": {
      "consumer_warning": 1
    }
  },
  "appealMetrics": {
    "scenarioCount": 4,
    "submitted": 4,
    "reversed": 2,
    "upheld": 1,
    "clarificationOnly": 1,
    "reversalRate": 0.5,
    "falsePositiveCategories": {
      "consumer_warning": 1,
      "help_seeking": 1,
      "not_false_positive": 1,
      "satire": 1
    },
    "transparencyBuckets": {
      "ambiguous_recovery": 1,
      "protective_speech": 1,
      "satire": 1,
      "wallet_drainer": 1
    }
  },
  "transparencyMetrics": {
    "totalReviewed": 3,
    "totalActioned": 1,
    "totalAppealedInQueue": 0,
    "totalReversedInQueue": 0,
    "authoredAppealScenarios": 4,
    "authoredReversals": 2,
    "automationAssistedRate": 1.0,
    "reviewAutomationAssistedRate": 1.0
  },
  "noticeTemplates": [
    {
      "id": "potential_crypto_fraud_label",
      "title": "Potential Crypto Fraud label notice",
      "trigger": "Reviewer confirms concrete scam evidence.",
      "body": "We added a Potential Crypto Fraud label because the post appears to request crypto, wallet connection, or payment using scam-like claims. You can appeal if context is missing.",
      "includedFields": [
        "policy rule",
        "matched evidence",
        "appeal link",
        "automation disclosure"
      ]
    },
    {
      "id": "high_confidence_escalation",
      "title": "Escalation notice",
      "trigger": "High-risk wallet, domain, or impersonation evidence requires deeper review.",
      "body": "This post was escalated for additional review because it combines high-risk crypto-scam signals such as wallet requests, impersonation, urgency, or repeated campaign infrastructure.",
      "includedFields": [
        "escalation reason",
        "review status",
        "appeal/feedback path"
      ]
    },
    {
      "id": "appeal_received",
      "title": "Appeal received notice",
      "trigger": "A user challenges a label or moderation decision.",
      "body": "We received your appeal. A reviewer will check the original evidence, your added context, and whether the post falls into a protected context such as warning, research, satire, or help-seeking.",
      "includedFields": [
        "case id",
        "expected review window",
        "what reviewers check"
      ]
    }
  ],
  "appealScenarios": [
    {
      "id": "consumer_warning_reversed",
      "title": "Consumer warning false positive",
      "initialAction": "Potential Crypto Fraud label",
      "appealClaim": "The post is warning people about scams, not promoting one.",
      "finalOutcome": "reversed",
      "reversed": true,
      "falsePositiveCategory": "consumer_warning",
      "reviewerChecks": [
        "Checked for direct transfer request from the speaker.",
        "Confirmed the post uses protective language.",
        "Verified there is no risky link, wallet address, or solicitation."
      ],
      "userNotice": "We removed the Potential Crypto Fraud label after review. Your post appears to warn others about scam behavior rather than request funds."
    },
    {
      "id": "satire_multiplier_reversed",
      "title": "Satire mistaken for solicitation",
      "initialAction": "Potential Crypto Fraud label",
      "appealClaim": "The post is an obvious joke using imaginary assets.",
      "finalOutcome": "reversed",
      "reversed": true,
      "falsePositiveCategory": "satire",
      "reviewerChecks": [
        "Checked whether the post asks for real funds.",
        "Confirmed satire markers and imaginary-asset language.",
        "Confirmed no wallet, link, QR code, or off-platform funnel is present."
      ],
      "userNotice": "We removed the label because the post is clear satire and does not request real funds."
    },
    {
      "id": "wallet_drainer_airdrop_upheld",
      "title": "Wallet-drainer airdrop appeal",
      "initialAction": "Potential Crypto Fraud label",
      "appealClaim": "The claim page is a legitimate promotion.",
      "finalOutcome": "upheld",
      "reversed": false,
      "falsePositiveCategory": null,
      "reviewerChecks": [
        "Checked the post for wallet-connection pressure.",
        "Checked urgency and free-token claim language.",
        "Confirmed the domain pattern is campaign-like and not an established official domain."
      ],
      "userNotice": "After review, the label remains because the post asks users to connect a wallet through an unverified airdrop claim."
    },
    {
      "id": "recovery_service_context_needed",
      "title": "Recovery-service ambiguity",
      "initialAction": "Sent to human review",
      "appealClaim": "The post asks for advice and should not be publicly labeled.",
      "finalOutcome": "clarification_sent",
      "reversed": false,
      "falsePositiveCategory": "help_seeking",
      "reviewerChecks": [
        "Checked whether the speaker is advertising the service.",
        "Confirmed the post is help-seeking.",
        "Kept the item in review because recovery-service scams are high-risk but context-dependent."
      ],
      "userNotice": "No public label was applied. We routed the post to review because recovery-service claims can be high-risk and context-dependent."
    }
  ],
  "standardsScorecard": {
    "summary": {
      "controlCount": 7,
      "implementedCount": 6,
      "partialCount": 1,
      "averageScore": 0.914
    },
    "controls": [
      {
        "id": "clear_rules",
        "standard": "Santa Clara Principles",
        "control": "Clear public rule and boundary examples",
        "evidence": "Policy boundary card, scenario eval cases, and notice templates.",
        "status": "implemented",
        "score": 1.0
      },
      {
        "id": "appealability",
        "standard": "Santa Clara Principles",
        "control": "Appeal path and reversal tracking",
        "evidence": "Appeal scenarios, reversed outcomes, and review-store statuses for appealed/reversed items.",
        "status": "implemented",
        "score": 0.9
      },
      {
        "id": "measure_risk",
        "standard": "NIST AI RMF Measure",
        "control": "Measure false positives, ambiguity routing, and reviewer-action distribution",
        "evidence": "Scenario evals, evidence-extractor evals, adversarial lab, and transparency report metrics.",
        "status": "implemented",
        "score": 1.0
      },
      {
        "id": "manage_risk",
        "standard": "NIST AI RMF Manage",
        "control": "Route uncertainty to humans before public enforcement",
        "evidence": "Human-review tier, missing-context evidence field, and recovery-service appeal scenario.",
        "status": "implemented",
        "score": 0.95
      },
      {
        "id": "detect_respond",
        "standard": "NIST CSF 2.0",
        "control": "Detect scam campaigns and respond through review/escalation",
        "evidence": "SQLite review store, entity extraction, campaign graph, and escalation status.",
        "status": "implemented",
        "score": 0.85
      },
      {
        "id": "llm_agency_boundary",
        "standard": "OWASP LLM / Agentic AI",
        "control": "Constrain LLM output to evidence assistance, not autonomous action",
        "evidence": "Structured evidence schema, span-faithfulness evals, and no publishing capability.",
        "status": "implemented",
        "score": 0.95
      }
    ]
  }
};
