# Selected related-work sources — v0.3

Accessed 2026-09-27 using primary project documentation. Scope: focused
responsibility comparison, not systematic review or exhaustive novelty audit.
Earlier RPC and AWS references are retained from v0.2.

| Source | Verified content | Manuscript use | Evidence boundary |
|---|---|---|---|
| Temporal Activity Definition, https://docs.temporal.io/activity-definition | Completed Activity can be retried when worker crashes before notification; recommends idempotence and service-enforced keys | Durable orchestration versus external side effects | Documentation, not reproduced benchmark |
| OpenTelemetry Traces, https://opentelemetry.io/docs/concepts/signals/traces/ | Span is an operation/unit of work; context carries trace/span IDs | Correlation versus application execution-evidence rules | No claim that tracing cannot encode these rules |
| Shopify Toxiproxy README, https://github.com/Shopify/toxiproxy | TCP proxy for deterministic/randomized connection perturbation in tests | Generic transport faults versus selected acceptance-response barrier | No equivalent-setup impossibility or measured superiority claim |

A USENIX candidate page returned 403 and was not used as a citation. An initial
raw GitHub request timed out; the project page and subsequent README fetch
succeeded. These failures are not negative literature evidence.

Open coverage: academic fault-injection/reconciliation nearest work, backend
version-specific interface citation, and target-year DSN requirements.
