# GenAI And Agentic Abuse Lab Report

Generated: 2026-06-21.

## Summary

- 4 synthetic abuse strategies.
- 12 deterministic variants.
- 8 risk-bearing variants.
- 4 protected-context variants.
- 4 reviewer-assistant risk tests.
- 0.0 assistant overreach rate in the authored guardrail checks.

## What This Tests

The module checks whether generated or agent-assisted safety tooling stays bounded. Scam-like synthetic variants should route to review or public-label candidacy, while warnings, research notes, and help-seeking contexts should not receive public labels.

## Abuse Strategies

- Airdrop funnel.
- Recovery service.
- Support impersonation.
- Localized lure.

## Agent Risk Scenarios

- Prompt injection.
- Tool misuse.
- Excessive agency.
- Memory poisoning.

## Safety Boundary

The lab uses deterministic templates and placeholder infrastructure. It does not call a generation API, create real scam links, or take platform actions.
