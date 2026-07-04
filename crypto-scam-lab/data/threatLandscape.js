// Authored reference data. Sources: FBI IC3 2024 Annual Report; Chainalysis 2025/2026
// Crypto Crime Reports; FBI Operation Level Up. Last verified July 2026.
// See threat_landscape/THREAT_LANDSCAPE.md for full citations and caveats.
export const threatLandscape = {
  headline: [
    {
      value: "$9.3B",
      label: "U.S. digital-asset fraud losses reported to FBI IC3 in 2024",
      detail: "~150,000 complaints, up 66% year-over-year.",
      source: "FBI IC3 2024 Annual Report",
    },
    {
      value: "$5.8B",
      label: "of that was investment fraud — the largest category",
      detail: "Dominated by fake-platform (pig butchering) schemes.",
      source: "FBI IC3 2024 Annual Report",
    },
    {
      value: "$14B+",
      label: "estimated on-chain scam revenue in 2025",
      detail: "Impersonation schemes grew ~1,400% year-over-year.",
      source: "Chainalysis 2026 Crypto Crime Report",
    },
    {
      value: "77%",
      label: "of contacted victims didn't know they were being scammed",
      detail: "Why help-seeking posts are protected and warnings are allies.",
      source: "FBI Operation Level Up",
    },
  ],
  typologies: [
    {
      name: "Pig butchering / fake investment platforms",
      documented: "Top loss category in IC3 2024; highest-revenue scam type in Chainalysis reporting.",
      labSubtype: "Guaranteed-return / HYIP promotion",
      detects: "Guarantee language, deposit solicitation, repeated platform domains in the campaign graph.",
      blindSpot: "Relationship-building happens in DMs and off-platform apps; only the recruitment surface is visible here.",
    },
    {
      name: "Celebrity giveaway doubling scams",
      documented: "Long-documented pattern, including the 2020 Twitter account-compromise wave.",
      labSubtype: "Send-to-receive schemes; impersonation",
      detects: "Doubling structure, authority name-drops, wallet addresses.",
      blindSpot: "Whether a named account is compromised versus a lookalike handle.",
    },
    {
      name: "Wallet drainers / approval phishing",
      documented: "Growing via fake claim pages and drainer kits rented to affiliates (Chainalysis).",
      labSubtype: "Wallet-drainer lures; airdrop fraud",
      detects: "Connect-wallet instructions tied to free claims, unverified domains, urgency.",
      blindSpot: "The landing page's actual drainer contract — URL evidence is deterministic and no-fetch in the demo.",
    },
    {
      name: "Advance-fee recovery scams",
      documented: "Recurring IC3 warning; targets prior victims for re-victimization.",
      labSubtype: "Advance-fee recovery",
      detects: "Recovery offers with upfront fees, DM funnels, victim-targeting language.",
      blindSpot: "Which users are recent victims — a platform-level protection signal this lab lacks.",
    },
    {
      name: "Impersonated exchange support",
      documented: "IC3 and FTC social-media fraud advisories.",
      labSubtype: "Impersonation",
      detects: "Support-escalation lures, credential and connection asks, brand-plus-urgency co-occurrence.",
      blindSpot: "Off-platform ticket systems and voice channels where the scam completes.",
    },
    {
      name: "AI-accelerated fraud",
      documented: "Deepfaked endorsements, AI personas, AI KYC bypass (Chainalysis 2025/2026).",
      labSubtype: "Cross-cutting; GenAI abuse lab",
      detects: "Template and mutation reuse at campaign level; generation-side guardrail tests.",
      blindSpot: "Authorship detection — the system deliberately scores behavior, not whether AI wrote the text.",
    },
  ],
  productImplications: [
    "Losses concentrate in persuasion over time, not single posts — campaign-level signals outrank any one post score.",
    "Victims defend the scam while it is happening — help-seeking must be protected, and warning content is the platform's ally.",
    "The highest-loss typology is mostly invisible to single-post classification — this system catches its recruitment surface, and says so.",
  ],
};
