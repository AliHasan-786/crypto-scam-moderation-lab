export const liveStreamCalibration = {
  generatedAt: "2026-07-11 22:34Z",
  source: "Public Bluesky Jetstream relay, app.bsky.feed.post create events",
  scope: "A 240-second EN/ES-screened snapshot. It is routing load, not fraud prevalence or model performance.",
  window: {
    seconds: 240,
    nonEmptyPostsObserved: 11353,
    postsScored: 8210,
    scoredLanguages: ["en", "es"],
    skippedOtherLanguages: 3143,
  },
  routing: {
    intermediateReview: { count: 583, share: 0.071 },
    humanOperatedQueue: { count: 600, share: 0.0731 },
    noLabel: { count: 7610, share: 0.9269 },
  },
  modelScore: { p50: 0.3222, p99: 0.4716 },
  privacy: "Aggregate-only. No post text, handle, DID, URI, or per-post record was retained.",
};
