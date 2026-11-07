# V2 Transport Reuse Decision

## What Was Reused

The V2 transport preparation follows StanceBench's cache-first architecture:
content-addressed cache keys, atomic JSON writes, per-attempt provenance,
explicit compatibility state, and a gate that runs before any transport method.
The V2 record fields intentionally mirror the StanceBench concepts for input,
prompt, model, policy/config identity, latency, cost, raw output, and
incompatibility reason.

## Why This Repo Does Not Import StanceBench Directly

Both repositories expose a top-level package named `model_comparison`. Direct
import therefore resolves to whichever checkout appears first on `sys.path`.
StanceBench also imports its separate `stancebench` package and uses a different
tuple/config schema and action vocabulary (`flag/review/no_flag` rather than the
V2 shared contract). Mutating `sys.path` to force that import would make this
lab's execution environment order-dependent.

## Minimal Interface Here

`v2_transport.py` implements only the crypto-specific pieces needed to prepare
the preregistered 168-row run: a V2 namespace, pinned-corpus check, current
access/budget context gate, atomic attempt records, and injected transport
protocol. It contains no provider SDK, network client, or credential loader.

## Follow-up Proposal for StanceBench

If both studies proceed to live execution, its owner should extract cache and
gate primitives into a separately versioned shared package or a uniquely named
module. Then this repo can migrate with a compatibility test proving that V2
records preserve their namespace and existing replay semantics. Do not copy V2
records into the V1 cache or StanceBench cache before that interface exists.
