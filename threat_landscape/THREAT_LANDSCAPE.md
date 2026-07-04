# Threat Landscape: Crypto Investment Scams on Social Platforms

This document grounds the lab's synthetic taxonomy in documented, real-world fraud data. Every violation subtype in the [Enforcement Matrix](../policy/ENFORCEMENT_MATRIX.md) corresponds to a typology documented by the FBI's Internet Crime Complaint Center (IC3), Chainalysis, or the FTC. The lab's eval and mutation cases are authored, but the behaviors they encode are not invented.

*Figures below are as reported by the cited sources; last verified July 2026.*

---

## 1. Scale of the problem

- **$9.3B** reported U.S. losses involving digital assets in 2024, across ~150k complaints — up 66% year-over-year ([FBI IC3 2024 Annual Report](https://www.ic3.gov/AnnualReport/Reports/2024_IC3Report.pdf)).
- **$5.8B** of that was investment fraud specifically — the largest crypto-crime category, dominated by fake-platform ("pig butchering") schemes (IC3 2024).
- **≥$14B** estimated on-chain scam revenue in 2025, with impersonation schemes growing ~1,400% year-over-year and average scam payment rising to ~$2,764 ([Chainalysis 2026 Crypto Crime Report](https://www.chainalysis.com/blog/2026-crypto-crime-report-introduction/)).
- In the FBI's Operation Level Up, **77% of identified crypto-investment-fraud victims did not know they were being scammed** when contacted ([FBI](https://www.fbi.gov/how-we-can-help-you/victim-services/national-crimes-and-victim-resources/operation-level-up)) — a key fact for notice design: victims resist warnings.

Two product implications drive this lab's design. First, losses are concentrated in *persuasion over time*, not single posts — which is why the campaign graph and repeated-infrastructure signals matter more than any one post score. Second, victims defend the scam — which is why help-seeking posts must never be treated as violations (protected context), and why warning content is the platform's ally.

## 2. Typology map: documented behavior → lab taxonomy → detection surface

| Documented typology (source) | Lab taxonomy subtype | Primary detection signals in this system | What this system cannot see |
| --- | --- | --- | --- |
| Pig butchering / fake investment platforms (IC3 top category; Chainalysis "highest-revenue scam type") | Guaranteed-return / HYIP promotion | Guarantee language, deposit solicitation, platform links, repeated domains in campaign graph | The relationship-building phase happens in DMs and off-platform apps; a text classifier sees only the recruitment surface |
| Celebrity/brand giveaway doubling scams (long-documented; e.g., the 2020 Twitter compromise pattern) | Send-to-receive schemes; impersonation | Doubling structure, authority name-drops, wallet addresses, send-X-receive-2X templates | Whether the named account is actually compromised vs. a lookalike handle |
| Wallet drainers / approval phishing (Chainalysis: growing via fake claim pages) | Wallet-drainer lures; giveaway/airdrop fraud | Connect-wallet instructions tied to free claims, unverified domains, urgency framing | The landing page's actual drainer contract — URL evidence is deterministic and no-fetch in the public demo |
| Advance-fee recovery scams targeting prior victims (IC3 recurring warning) | Advance-fee recovery | Recovery offers + upfront fee, DM funnels, victim-targeting language | Which users are recent victims (would require platform-level victim-protection signals) |
| Impersonated exchange support / account-restriction phishing (IC3; FTC social-media fraud warnings) | Impersonation | Support-escalation lures, credential/connection asks, brand + urgency co-occurrence | Off-platform ticket systems and voice channels where the scam completes |
| Pump-and-dump groups and paid signal channels | Pump groups / insider signals | Guaranteed-profit claims, paid-access funnels | Actual market manipulation happens on exchanges, outside content moderation's view |
| AI-accelerated fraud: deepfaked endorsements, AI-generated personas, AI KYC bypass (Chainalysis 2025/2026) | Cross-cutting; GenAI abuse lab | Template/mutation detection, campaign-level reuse; the GenAI lab tests generation-side guardrails | Detection of AI-generated text per se — the lab deliberately scores behavior, not authorship |

## 3. Actor model (who is on the other side)

The ABC model from the policy work, grounded in the enforcement literature: **organized fraud networks** (industrial pig-butchering operations, increasingly using trafficked labor — see [DOJ Scam Center Strike Force actions](https://www.justice.gov/opa/pr/scam-center-strike-force-takes-major-actions-against-southeast-asian-scam-centers-targeting)); **drainer-kit affiliates** renting phishing infrastructure; **opportunistic imitators** copying templates (the reason template mutation testing matters); and **compromised or impersonated accounts** lending stolen credibility. The campaign graph exists because all four actor classes reuse infrastructure — domains, wallets, handles, phrasing — faster than they rotate it.

## 4. What the landscape implies about this system's limits

Honest boundaries, stated plainly: the highest-loss typology (pig butchering) is mostly invisible to single-post text classification — this system catches its *recruitment surface* only. Loss concentration is in DMs and off-platform migration, which content moderation cannot reach and account-level friction (rate limits, new-account link restrictions) addresses better than labels. And every documented typology now has an AI-accelerated variant; the mutation lab's operators (leetspeak, spacing, defanging) model yesterday's evasion, while paraphrase-scale evasion is tested only in the GenAI abuse lab's bounded variants. These limits are why the roadmap prioritizes campaign intelligence and account-history enrichment over squeezing more F1 out of a post classifier.

## 5. Sources

- [FBI IC3 2024 Annual Report](https://www.ic3.gov/AnnualReport/Reports/2024_IC3Report.pdf) — loss figures, complaint volumes, investment-fraud category.
- [FBI Operation Level Up](https://www.fbi.gov/how-we-can-help-you/victim-services/national-crimes-and-victim-resources/operation-level-up) — victim-awareness statistics.
- [Chainalysis 2025 Crypto Crime Report](https://www.chainalysis.com/blog/2025-crypto-crime-report-introduction/) and [2026 introduction](https://www.chainalysis.com/blog/2026-crypto-crime-report-introduction/) — on-chain scam revenue, impersonation growth, AI-enabled fraud trends.
- [FBI press release: Cryptocurrency and AI scams](https://www.fbi.gov/news/press-releases/cryptocurrency-and-ai-scams-bilk-americans-of-billions) — AI-assisted fraud framing.
- [DOJ Scam Center Strike Force](https://www.justice.gov/opa/pr/scam-center-strike-force-takes-major-actions-against-southeast-asian-scam-centers-targeting) — organized scam-center enforcement context.
