export const campaignGallery = {
  generatedAt: "2026-06-21",
  privacyBoundary:
    "Gallery examples are sanitized and synthetic. Live Bluesky ingestion stays local-only and does not publish labels or moderation actions.",
  campaigns: [
    {
      id: "gallery_reused_domain_wallet",
      title: "Repeated domain and wallet pattern",
      pattern: "Multiple posts reuse a defanged airdrop domain, wallet-connection language, and one wallet-like string.",
      visibleSignals: ["defanged domain", "wallet connection", "shared wallet", "new-account burst"],
      defaultAction: "Create campaign cluster and route representative samples to review.",
      riskLevel: "high",
    },
    {
      id: "gallery_recovery_scam",
      title: "Recovery-fee pattern",
      pattern: "A service claims it can recover lost funds, then introduces an upfront crypto payment.",
      visibleSignals: ["recovery claim", "processing fee", "certainty language", "crypto transfer ask"],
      defaultAction: "Candidate for public label when fee request and certainty claims are explicit.",
      riskLevel: "high",
    },
    {
      id: "gallery_fake_support",
      title: "Fake support pattern",
      pattern: "A reply impersonates exchange support and asks for wallet verification or a small deposit.",
      visibleSignals: ["brand impersonation", "account restriction claim", "wallet verification", "deposit request"],
      defaultAction: "Escalate repeated support impersonation and preserve account/entity evidence.",
      riskLevel: "high",
    },
    {
      id: "gallery_consumer_warning",
      title: "Consumer-warning false positive",
      pattern: "A user repeats scam phrases while warning others not to send funds or connect wallets.",
      visibleSignals: ["warning language", "do-not-send framing", "scam phrases quoted", "no live claim path"],
      defaultAction: "No public label; use as protected-context calibration and eval coverage.",
      riskLevel: "low",
    },
    {
      id: "gallery_ocr_qr_ambiguity",
      title: "OCR/QR missing-context pattern",
      pattern: "Screenshot text contains claim and wallet language, but the source account or destination link is cropped.",
      visibleSignals: ["OCR text", "QR visible", "source missing", "link cropped"],
      defaultAction: "Human review only until source/link context is verified.",
      riskLevel: "medium",
    },
  ],
};
