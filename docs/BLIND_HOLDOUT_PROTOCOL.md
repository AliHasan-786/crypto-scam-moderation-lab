# Blind Holdout Protocol — 2026 Q3

**Status:** Preregistered protocol only. No new live posts have been collected.

Before collection, approve a private retention schedule, terms posture, named
operator, kill-switch owner, exact UTC window, and access-controlled storage.
Commit only collection metadata, item hashes, aggregate counts, and the release
manifest. Never commit raw post text or identifiers.

Freeze the current model artifact SHA-256 and thresholds before collection. Keep
the sample unlabeled and inaccessible to tuning for at least 30 days, then label
with a documented human rubric. Report precision, recall, review share,
protected-context error rate, sample size, uncertainty intervals, and exclusions
regardless of outcome. This cannot begin until the real-data gate passes.

Target at least 200 eligible items after exclusions. Exclude deleted/unreadable
records, non-EN/ES records, duplicates, and records that cannot be retained
under the approved schedule; report every exclusion count. Two reviewers label
the full sample independently using `quality/REVIEWER_CALIBRATION_GUIDE.md`;
if only one reviewer is available, publish that limitation and do not report
inter-rater agreement. Disagreements are adjudicated with the recorded rubric.
