# V2 Crash-Safe Transport Gate

**Status:** offline engineering preparation only. No provider client, provider
SDK, credentials, external request, paid computation, or V2 model result is
included in this gate.

## Purpose

The V2 shared-action comparison must not make a duplicate request merely
because a runner crashes, a result is only partly persisted, or two processes
start together. `v2_transport.py` therefore uses a durable local reservation
journal before it calls an injected transport.

## Required Current Authorization Fields

In addition to the existing corpus, prompt, policy, model, date, and budget
identities, a future current access context must contain:

- `authorizationId`: a stable identifier for one reviewed authorization;
- `budgetCapUsd`: the reviewed total liability cap; and
- `maxInvocationLiabilityUsd`: a reviewed maximum liability for one provider
  invocation, positive and no greater than the total cap.

`estimate_cost_usd` is adapter metadata only. It is checked to ensure it does
not exceed the configured maximum liability, but it does not reserve capacity
and is not treated as a provider-enforced price or hard cap.

## Fail-Closed State Machine

1. A single process acquires an advisory file lock.
2. It atomically writes and fsyncs an immutable `reserved` event for the full
   configured maximum invocation liability.
3. It records `invocation_started`, then calls the injected transport.
4. It atomically persists the attempt result before recording an immutable
   known-cost settlement.
5. If a response/cost/result is unknown or result persistence fails, the full
   reservation remains committed to the cap and receives an immutable
   `requires_reconciliation` event. Automatic retry is blocked.

On restart, the runner may settle a reservation only when it finds one matching
immutable attempt result with a known cost. It never invokes a provider during
recovery. A human operator may append a reconciliation event with a verified
cost and nonempty note; this does not reopen the same invocation key for an
automatic retry.

Total capacity is always computed as known committed cost plus all unresolved
reservations. The journal is bound to authorization, cap, corpus, prompt,
policy, allowed-model, and V2 spec identities and lives outside the attempt
cache, so changing a cache or authorization-file path does not reset it.

## Verified Offline Coverage

`model_comparison.test_v2_transport` uses only temporary directories and fake
injected transports. It covers two concurrent processes, cache/context changes,
crashes before invocation and before settlement, recovery from an already
persisted result, partial journal data, duplicate invocation keys, unknown
costs with immutable reconciliation, malformed numeric values, and configured
liability distinct from a small adapter estimate.

## Remaining Live Gates

This control cannot guarantee a provider's actual billing behavior or provide a
provider-enforced hard cap. Before any live transport, a named operator must
review provider availability, current pricing and maximum liability, a real
access context, retention and incident procedures, and the remaining source,
rights, and model-comparison gates. The historical V1 `$80` configuration is
not authorization for V2.
