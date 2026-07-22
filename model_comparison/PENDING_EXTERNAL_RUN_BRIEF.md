# Pending External Benchmark Run

**Status:** Do not run. This repository is configured only to validate local
readiness. No provider request, credential validation, model discovery, or
spend is authorized until Ali explicitly approves the first external run.

Before that approval: place `GROQ_API_KEY` and `OPENAI_API_KEY` in the ignored
`model_comparison/.env`; verify the `$80` cap; and confirm the pinned IDs in
`PREREGISTRATION.md` with the selected providers. The first run must record
provider-resolved IDs and the preregistration hash before requests begin.
