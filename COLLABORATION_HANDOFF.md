# Fable Review — 2026-07-16

Reviewed at commit `80c33b4` ("Refocus lab around narrative and published failures"), live at https://crypto-scam-lab.vercel.app. The four-destination structure is a real improvement: the console chrome is gone, the held-out numbers are now reconciled and provenance-labeled, the serif/warm-paper direction reads editorial, and What breaks is finally a top-level destination. The findings below are refinements to that structure, not a new direction.

## What I Reviewed

- **Live pages (desktop ~1280px):** The story (full scroll), Try it (including clicking "Evaluate draft" and inspecting the result-panel state change), What breaks → Published failures, The full system, and Case archive via the appendix index. `#overview` correctly lands on The story; no orphan destinations found. Zero console errors.
- **Live pages (mobile 375×812):** The story hero, masthead tab behavior.
- **Source:** `crypto-scam-lab/app.js` (module/subtab definitions ~lines 112–210; `renderWelcome` ~2238; `renderProjectPrimer` ~1990; `renderTester` ~1002; case-review panel ~974–977), `crypto-scam-lab/styles.css` (token root, type-scale rules, radius usage), `crypto-scam-lab/index.html`, README, case study, explainer.
- **Interactions tested:** stance presets on the story tester (verdict + copy flip correctly), Try it presets and Evaluate draft, appendix navigation in and back out, mobile tab scrolling.

## Highest-Leverage Findings

1. **The story restarts itself mid-page (narrative sequencing).** The merged page has two beginnings: the hero (question → lede → three stats → three path cards) and then, after "Provenance," a second full introduction — "The problem / Catch scams without silencing crypto conversation" with near-duplicate framing and a *second* set of three path links ("Try a decision / See the failures / Open the appendix," `app.js:2008–2010`). A reader who was following the argument gets sent back to the starting line. The seam from merging the old welcome and approach pages is the single most visible flaw in the flagship page.

2. **Two testers, two interaction grammars — and the weaker one owns the "Try it" tab.** The story tester is the thesis: live as-you-type scoring, stance presets (scam / warning / joke / skeptical question), stance-aware verdict copy. Try it (`renderTester`, `app.js:1002`) is a different machine: a static textarea, an "Evaluate draft" button instead of live updates, presets (`scenarioTexts`, `app.js:243`) that omit the warning/skeptic stance pair entirely, four unexplained jargon chips (Space / Leet / Defang / OCR), and a result panel that on first load shows an unrelated pre-loaded case ("Case review / Unrealistic returns / test-051 · 98%") — which reads as if it were the verdict on the draft sitting above it. The site's best interaction and its dedicated interaction page currently disagree about how interaction works.

3. **Two design systems still ship in one stylesheet (typography and shape).** The editorial layer is appended as overrides rather than replacing what came before: `.welcome-hero h1` is declared twice (`styles.css:2536–2537` at clamp 24–34px, then re-declared at `styles.css:3425` at clamp 2.35–5rem); the serif stack (Iowan Old Style/Baskerville/Georgia) only enters at `styles.css:3228` instead of living in the base heading rules; and corner language is split between the editorial 2px radius and leftover SaaS rounding — `border-radius: 999px` pills and 12–16px cards at `styles.css:612, 2626, 2683, 2828, 3008, 3092, 3139, 3146, 3175`. It's visible in product: Try it's rule-score bars, What breaks' stat cards, and Case archive rows are rounded soft-UI cards sitting inside an otherwise hairline-and-2px editorial page. This is also why regressions keep leaking: overrides-of-overrides make every future change a scavenger hunt.

4. **Appendix pages drop wayfinding.** Inside Case archive, Campaigns, At scale, or Accountability, no masthead tab shows an active state and there is no link back to The full system other than re-clicking the tab. The "Appendix" eyebrow is right; it just isn't clickable. On mobile, the fourth tab ("The full system") sits off-screen with only a faint scrollbar as the affordance, so the appendix is close to undiscoverable at 375px.

5. **Label soup at the exact moments of highest attention.** The result panel a visitor studies most is captioned with three competing names at once: eyebrow "Case review," heading "Live post tester," sub-line "draft" (`app.js:974–977`, `app.js:1025`). "Evaluate draft" is system-internal vocabulary — visitors are testing a post, not drafting one. Same pattern on What breaks: the intro paragraph is a container inventory ("the eval suites, the release gate, the published error analysis, the LLM comparison, and the GenAI abuse lab - together...") rather than the claim that page actually makes, which the Standing Error Analysis card states perfectly two inches lower.

## Recommended Changes

1. **Re-sequence The story into one continuous argument** (fixes finding 1). Target order: question hero (keep as-is) → stance tester → "How it works" → held-out artifact strip (keep the provenance sentence) → "Assignment 2, distilled" → "From policy to product" → key terms → provenance → single closing set of next-step links. Concretely: delete the duplicated intro ("The problem" header block and its lede paragraphs in `renderProjectPrimer`), keep exactly one set of path cards (the hero's three), and let "Provenance" close the page rather than interrupt it. No content is lost — only the second beginning and the duplicate CTA row are removed.

2. **Make Try it the same tester, deeper** (fixes findings 2 and 5). One shared tester component: live as-you-type scoring, the story's four stance presets plus Try it's additional examples in one preset row, and the result panel always reflecting the current textarea (never a pre-loaded unrelated case — the annotated case browsing already lives in Case archive). Keep the mutation chips but give each a plain-language flip label ("sp ace out letters," "l33t-swap characters," "de-fang the link," "move the ask into an image") and let them mutate the current text live. Remove the "Evaluate draft" button and its vocabulary; rename the result panel to one name ("Verdict" or "The decision") used identically on both pages.

3. **Consolidate the stylesheet to one system** (fixes finding 3). One type scale with the serif hoisted into base heading rules; one radius token (2px) applied to the pills, rule bars, stat cards, and case rows listed above; delete the superseded declarations (e.g., `styles.css:2536` block) rather than out-overriding them. Intended visual change: corners and heading font only — everything else should render identically, which is what makes this safe to verify.

4. **Give the appendix a spine** (fixes finding 4). When an appendix module is open: highlight "The full system" as the active masthead tab, and make the "Appendix" eyebrow a link back to `#system` (e.g., "Appendix ← The full system"). On mobile, ensure the active tab scrolls into view and the tab row shows a visible cue that it scrolls (fade edge or partial next-label peek — not a new control).

5. **Rewrite the What breaks intro as its claim** (fixes finding 5). One sentence in the voice the page already has, e.g.: "Authored suites that pass 100% prove only that the boundary holds. This page is what the system actually gets wrong — published on purpose." The subtab list already communicates the contents; the paragraph doesn't need to.

## Preserve

- **The stance-aware tester's behavior and verdict copy** — especially "Warnings are the platform's allies - punishing them is the worst failure this system can make." This is the best moment on the site.
- **The Published failures content in full:** the 8 false positives by class, the 9 hard cases with expected/actual and "Blind spot" lines, the promote-and-replace rule, and the "authored suites … indistinguishable from suites written to pass" framing.
- **The held-out artifact strip and its provenance sentence** ("This is the reproducible v2 held-out artifact, not the adjustable browser simulator") — this reconciliation was the most important fix of the last pass; do not let any number appear without its source again.
- **"Assignment 2, distilled"** — all five parts, and the "From policy to product" three-step bridge.
- **The four-destination masthead** and the names The story / Try it / What breaks / The full system.
- **The serif display + warm paper + terracotta/teal palette**, hairline rules, and the numbered appendix index page.
- **The honesty caveats** ("Read these numbers correctly…") on the evaluation record, and all stated limitations (sanitized data, no enforcement, reviewer-assist-only LLM).
- **"How it works" step copy** ("Evidence, not vibes") and the key-terms glossary.

## Acceptance Criteria

1. The story contains exactly one introductory block and exactly one set of path cards; the phrase "Catch scams without silencing crypto conversation" and the "Try a decision / See the failures / Open the appendix" link row no longer appear as a second opening.
2. Typing in the Try it textarea updates the verdict without pressing any button; no "Evaluate draft" button exists; on first load the Try it result panel scores the text in the textarea, never test-051.
3. The Try it preset row includes the warning-about-scams and skeptical-question stance presets, and each mutation chip has a visible plain-language label; toggling a chip visibly changes the textarea content and the verdict.
4. `grep -c "border-radius: 999px" crypto-scam-lab/styles.css` returns 0, 12–16px radii are gone (or reduced to a single documented token), `.welcome-hero h1` is declared exactly once, and the serif stack appears in the base heading rules rather than only in a late override block.
5. Opening `#queue`, `#intel`, `#operations`, or `#govern` shows "The full system" as the active masthead tab and a working link back to the appendix index; at 375px width all four masthead tabs are reachable with an evident scroll affordance.
6. The What breaks intro paragraph no longer enumerates its five subsystems; it states the failure-publishing claim in ≤2 sentences.
7. Existing checks still pass: `bash scripts/run_all_checks.sh` completes, and no quantitative claim on any page appears without its source artifact named (browser simulator vs. held-out v2).

## Open Questions

1. **Story length vs. split.** The story is now ~9 sections on one scroll. I recommend keeping the single scroll (the merge was right; only the seam is wrong), but if you'd rather cap the page at the held-out artifact and move "Assignment 2, distilled" + "From policy to product" to a linked second chapter ("The policy"), that changes recommendation 1 — which do you want?
2. **Mutation chips' home.** Space/Leet/Defang/OCR are adversarial-evasion demonstrations. Keep them on Try it (my recommendation, with plain-language labels), or move them into What breaks next to the mutation-retention evidence where they argue the same point?
3. **Case archive's default filter.** It currently opens on "Flagged" (80 items). Opening on "False positives" (8 items, each one a story the site already tells) would make the archive lead with the project's signature honesty — acceptable, or do you want the fuller flagged view first?
