# Deterministic Fault Coverage

This directory contains bounded W0/W1/W2 deterministic fault coverage generated
from the fixed B2 checkout. The files are research records, not public
acceptance evidence or deployment failure estimates.

`w2-fault-matrix.json` contains six deterministic CPU/fake-backend cases:
F00/F02/F03, each stratified by ordinary single-stage and existing two-stage
product paths. F00 is a control arm and is excluded from fault injection
denominators. Each case retains the product-reported manifest and a separate
worker-entry CPU oracle. The fake runner writes tiny synthetic PNGs; no model,
GPU, Windows host, online ComfyUI, or ROS2 service is used.

The denominator fields use these meanings:

- `scheduled`: cases in the frozen CPU schedule.
- `started`: scheduled cases whose product generation entrance was invoked.
- `injection-confirmed`: fault cases whose versioned barrier and error code
  were observed; F00 controls are not part of this denominator.
- `oracle-evaluable`: every observed execution start has exactly one matching
  finish event, or the case has no execution start.
- `resolved`: the first fault boundary had a product recovery path in this
  package; known-job two-stage recovery counts as resolved.
- `unresolved`: the first fault boundary remained ambiguous to the product
  caller or had no durable recovery binding.
- `failed`: at least one product attempt was reported `failed`; this does not
  mean the backend execution failed.
- `not-run`: scheduled cases not executed.

`submission_count` comes from independent `request_received` events. It is
separate from `oracle_execution_count`; `duplicate_submission` must not be
renamed to `duplicate_execution`.

The matrix reports deterministic fault coverage only. Its execution counts are
synthetic worker observations and cannot be converted into deployment failure
rates or real-backend duplicate-execution rates.
