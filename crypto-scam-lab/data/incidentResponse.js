export const incidentResponse = {
  "generatedAt": "2026-07-02T03:16:16.138531+00:00",
  "scenarioCount": 3,
  "severityCounts": {
    "sev2": 1,
    "sev3": 2
  },
  "highestSeverityScenario": {
    "id": "ir_wallet_drainer_campaign",
    "title": "Coordinated wallet-drainer airdrop campaign",
    "severity": "sev2"
  },
  "operatingPrinciples": [
    "Preserve evidence before broad enforcement changes.",
    "Route ambiguity to review instead of forcing a public label.",
    "Use shared entities as campaign leads, not standalone proof.",
    "Convert incidents into eval, policy, QA, or tooling updates.",
    "Track false-positive impact alongside fraud mitigation."
  ],
  "scenarios": [
    {
      "id": "ir_wallet_drainer_campaign",
      "title": "Coordinated wallet-drainer airdrop campaign",
      "severity": "sev2",
      "trigger": "Multiple new accounts reuse the same defanged airdrop domain and wallet-connection language within a short window.",
      "signals": [
        "shared suspicious domain",
        "shared wallet-connection phrase",
        "high-confidence model action",
        "duplicate observations",
        "new-account posting pattern"
      ],
      "first_actions": [
        "Freeze automatic public-enforcement expansion until evidence is reviewed",
        "Create campaign cluster and preserve entity evidence",
        "Route representative samples to senior reviewer",
        "Add temporary warning friction for repeated domain if policy evidence is confirmed"
      ],
      "cross_functional_partners": [
        "T&S Operations",
        "Policy",
        "Product",
        "Engineering",
        "Legal/Compliance"
      ],
      "mitigations": [
        "Domain-level warning friction",
        "Reviewer priority boost for shared-infrastructure posts",
        "Temporary rate limits on new accounts posting the repeated domain",
        "Add campaign examples to hardening evals and reviewer calibration"
      ],
      "success_metrics": [
        "time to cluster confirmation",
        "review SLA for high-risk samples",
        "false-positive review rate",
        "repeat-domain exposure reduction",
        "appeal reversal rate"
      ],
      "postmortem_questions": [
        "Which signal first identified the campaign?",
        "Did any benign posts share the same entity pattern?",
        "Which workflow step created delay?",
        "Which eval or policy update should prevent recurrence?"
      ]
    },
    {
      "id": "ir_false_positive_spike",
      "title": "False-positive spike after policy update",
      "severity": "sev3",
      "trigger": "Reviewer dismissals and appeals increase after a new policy rule starts routing educational warnings to review.",
      "signals": [
        "higher dismissal rate",
        "appeal reversals",
        "protected-context phrases",
        "consumer-warning language",
        "reviewer notes citing over-enforcement"
      ],
      "first_actions": [
        "Pause promotion of the new rule to public labels",
        "Sample dismissed cases and appeals",
        "Run protected-context eval and calibration cases",
        "Patch policy guidance before changing model thresholds"
      ],
      "cross_functional_partners": [
        "Policy",
        "Quality",
        "T&S Operations",
        "Data Science",
        "Product"
      ],
      "mitigations": [
        "Protected-context suppression rule",
        "Reviewer training update",
        "False-positive eval gate",
        "Notice copy clarification"
      ],
      "success_metrics": [
        "dismissal rate among reviewed items",
        "appeal reversal rate",
        "protected-context eval pass rate",
        "reviewer calibration accuracy"
      ],
      "postmortem_questions": [
        "Was the policy rule too broad?",
        "Did reviewer guidance include enough examples?",
        "Did evals include warnings, satire, and help-seeking cases?",
        "What launch gate should have caught the issue?"
      ]
    },
    {
      "id": "ir_ocr_qr_ambiguity",
      "title": "OCR/QR scam reports with missing source context",
      "severity": "sev3",
      "trigger": "Users report screenshots containing QR codes and wallet-connection text, but source accounts and links are cropped.",
      "signals": [
        "OCR text contains claim/wallet language",
        "source account missing",
        "link cropped",
        "QR code visible",
        "model probability elevated"
      ],
      "first_actions": [
        "Route to human review rather than automatic public labeling",
        "Ask reviewer to verify source/link context where available",
        "Track OCR ambiguity separately from confirmed wallet-drainer cases",
        "Create examples for multimodal hardening evals"
      ],
      "cross_functional_partners": [
        "T&S Operations",
        "Policy",
        "ML/Evaluation",
        "Product"
      ],
      "mitigations": [
        "OCR-specific review queue",
        "Source-context requirement for public labels",
        "Screenshot/QR evidence checklist",
        "User-facing notice that explains missing context decisions"
      ],
      "success_metrics": [
        "OCR review precision",
        "time to source verification",
        "public-label downgrade rate",
        "appeal reversal rate for OCR cases"
      ],
      "postmortem_questions": [
        "What context was missing at review time?",
        "Could product affordances collect safer source metadata?",
        "Should OCR-only content be a separate review tier?",
        "Which evals need new screenshot examples?"
      ]
    }
  ]
};
