# I built a scam-detection system, then published everything it gets wrong

*Draft for LinkedIn / personal blog. ~4 minute read.*

---

Last fall, for a Trust & Safety course at Cornell Tech, I built a classifier that catches crypto scams on social platforms. It scored well. It was also, I later realized, quietly broken — leaky evaluation, cherry-picked model selection, one flattering number hiding two very different failure modes.

The instinct is to fix that quietly. Instead I audited my own model, published the audit in the repo, and rebuilt the project into something closer to what Trust & Safety work actually is. Here's what I learned.

**The hard part isn't catching scams. It's not catching everyone else.**

"Send me 0.1 BTC and get 0.2 back" is a scam. It's also a quote in a news article, a line in a research paper, the setup of a joke, and — most importantly — the thing a victim types when asking "did I just get scammed?" A system optimized purely for catch rate punishes journalists, researchers, comedians, and victims. My rebuilt system treats those protected contexts as first-class policy, enforced in code and tested by a release gate: warnings, news, research, satire, debugging, and help-seeking suppress public labels no matter what the risk score says.

**One F1 score hides two different harms.**

A wrong public "fraud" label is the platform accusing an innocent person. A scam missed by review is a victim the platform failed. These deserve separate metrics with separate bars — so I split them: public-label precision (currently 0.882, every false positive published) and review-or-label recall (1.0 on the held-out set, a fact that says as much about corpus size as about the model — and the report says so).

**Eval suites that pass 100% prove nothing.**

If you author your own test cases, passing them is circular. So the system maintains a standing error analysis: the eight real false positives at the current operating point, categorized and explained, plus nine authored hard cases it's *supposed* to struggle with — five still fail, and they stay published until solved. The most interesting finding: six of the eight false positives are people *skeptically describing* scams ("they claim 80% returns, but I can't verify the license..."). The system hears scam vocabulary; it can't hear the speaker's stance. That single insight now drives the LLM-assistance roadmap.

**Thresholds are staffing decisions wearing a math costume.**

I simulated a 50,000-post day with realistic scam prevalence. Moving the review threshold from 0.40 to 0.30 roughly doubles the reviewers you must employ — for about one point of recall. When a policy team argues about thresholds, they're actually arguing about payroll, burnout, and burst capacity during campaign waves. Every T&S candidate should be able to do this arithmetic; most portfolios never show it.

**LLMs have to earn their seat.**

I added a hosted-LLM evidence assistant — same policy prompt, same faithfulness gate as the deterministic extractor: every claim must quote a verbatim source span. The honest comparison: the cheap baseline wins on cost by three orders of magnitude, and the LLM wins on exactly one thing that matters — stance. It can tell reporting from promoting. The right architecture is boring and defensible: cheap triage first, LLM assistance only on the review slice, humans deciding.

**What made this real wasn't the model.**

It was the appeals flow, the reviewer calibration cases, the incident runbook, the transparency report, the DSA statement-of-reasons sample, the decision log where every tradeoff has a date and an owner. The classifier is maybe 10% of the system. That ratio, I've come to believe, is roughly correct for the industry too.

The whole thing is live — including a 90-second guided tour and a page dedicated to what it gets wrong: [crypto-scam-lab.vercel.app](https://crypto-scam-lab.vercel.app). The repo, policy pack, and decision log are on [GitHub](https://github.com/AliHasan-786/crypto-scam-moderation-lab).

I'm looking for Trust & Safety roles where this kind of thinking is useful. If that's your team, I'd love to talk.
