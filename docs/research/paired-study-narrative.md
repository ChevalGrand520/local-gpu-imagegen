# Paired study narrative: working research extension

Evidence authority: the paired-C rows in
`dsn-tool-description-claim-evidence-matrix.md`. This is a separate draft,
not an amendment to frozen Tool v0.18. No new literature claims are introduced.

## Evaluation question

After a submission response is lost, the client must decide whether to submit
again while the backend may already be processing the request. We examine that
decision at the same-run boundary. The evaluation asks whether an unknown-outcome
guard withholds an additional submission and what happens to the original run
when it does. Backend lifecycle completion and client recovery are recorded
separately, because either one can occur without the other.

## Protocol

The paired campaign used pinned native B2 and W3 products with the same
generation semantics, including seed, model and workflow. A shared research
caller issued one normal call in F00 and at most two same-run calls in each
fault condition. F02 suppressed the first response after backend acceptance;
FPRE closed the connection before the proxy entered the upstream send path.
The caller scheduled the retry after the first call returned, without waiting
for an oracle completion decision. Each operation used a fresh backend process;
the two calls within a fault operation shared that process and its cache.

Both F00 controls completed. Their generation RPC intervals were 35.77 and
24.20 seconds, yielding a 107.32-second fault observation deadline under the
predefined calibration rule. These intervals include client and MCP processing.
The campaign ran in a Windows desktop environment with retained background
process observations, so they serve as deadline calibration rather than an
isolated hardware benchmark.

## Submission and completion results

In F02, B2 issued two proxy submissions and obtained two bound backend
lifecycles. Its retry completed the original run. W3 returned
`submission_outcome_unknown` on the retry and issued no additional proxy POST.
The single accepted backend job completed, while W3's original run remained
unresolved. This pair demonstrates the intended submission boundary and the
outstanding recovery obligation in the same record.

FPRE exposed the cost of the same conservative decision. Proxy stage records
show that the first request never entered the upstream send path. B2 retried,
submitted once upstream and completed. W3 blocked the retry, with zero upstream
sends and an unresolved original run. The guard cannot use the research proxy's
pre-send evidence to resolve the client's unknown outcome; its observed behavior
is consistent with the information available at its entry point.

Across the six operations, the caller made ten product calls, the proxy
received eight prompt POSTs and the upstream send path was entered six times.
These units describe different stages of the operation. In particular, B2's
second F02 lifecycle reported cache reuse of nodes 3 through 9, covering the
generation graph. The lifecycle difference therefore does not quantify repeated
GPU computation or compute saved by the guard.

## Interpretation and evidence export

The observed tradeoff is between withholding another submission and completing
the original run. W3 enforced the former in both fault conditions; B2 completed
the run through retry. A simple stop-after-unknown strategy matched W3's
submission counts in the earlier CPU checks, and was not included in this
Windows campaign. The contribution supported here is the scoped product behavior
and its inspectable evidence, rather than dominance over all retry policies.

W3/F02 also supplies a concrete backend-complete/client-unresolved record for
the evidence representation. The campaign did not newly evaluate exporter
normalization or its verification veto. Earlier same-information CPU probes
gave the ordinary parser and exporter identical decisions. Exporter integration,
field validation and interpretation remain separate claims from the measured
submission behavior.

## Retention and study boundary

The complete private archive was transferred with matching SHA-256 hashes.
Offline checks rehashed source and raw-message bytes, replayed event binding,
recomputed proxy counts and checked paired semantics, manifests and retained
client artifacts. This validates consistency of the retained record, not the
authenticity of its execution. The replay uses the project's own binding rules.
The study covers three fixed pairs on one model/workflow/platform; it estimates
no deployment rate or population effect. Earlier stopped batches remain separate,
including the observer timeout defect fixed before this campaign.
