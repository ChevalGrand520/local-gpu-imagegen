# Selective response to the supplied review, v0.18

This note records an author-side assessment and editorial response. The supplied
model review is advice, not a peer-review decision. No new experiment was run.

| Suggestion | Assessment and action |
|---|---|
| Stronger novelty statement | Adopt the request for a concrete contribution. The introduction now describes the persistent run/job-ID gap, preserved disagreement and run-scoped submission decision. Do not claim that expensive computation or file outputs distinguish GenAI fundamentally from all RPC systems. Backend-supported idempotency remains relevant; deduplication is unestablished in the evaluated workflow. |
| Add quantitative metrics | The tables already quantify calls, submissions and lifecycle bindings. Comparative latency, compute cost and false-positive measurements are absent. CPU B2=2/W3=1 is a synthetic fixture result; historical Windows B2 and W3 both have two F02 submissions. The revised Windows v2 records two calls, one POST and one lifecycle, without a matched Windows B2 guard comparison. Cached F02 lifecycles cannot establish physical GPU savings. No missing metric was invented. |
| Increase n or rename the paper | Larger coverage can help a full research evaluation, but 20--30 configurations is not a general statistical adequacy threshold. This manuscript is explicitly a Tool Description with fixed-case demonstrations. Keep the title and keep claims at that scope. |
| Consolidate repetitive qualifiers | Adopt selectively. Remove the unprompted complete-filesystem-security caveat. Put the input-provenance assumption in the limitations section once. Retain the mapping's metadata behavior at its interface, the unresolved historical start gap and the cache/computation distinction in the results. |
| Vary prose rhythm | Use concrete actors and actions in the introduction and exporter description. Do not insert dramatic closers such as "This is a hard boundary" solely to imitate a human style. Technical terms remain consistent. |
| Move limitations after related work | Adopt as an organizational choice, not a universal conference rule. Sections V/VI now contain Related Work and Reproducibility/Limitations respectively. |
| Shorten Table I caption | Adopt. Move S/E, Complete and synthetic-trace definitions to a note below the unchanged table. Column headings were already short. |
| Shorten AI disclosure | Adopt. Reduce from 67 to 24 whitespace-delimited source words. Preserve tool attribution and the outstanding human-approval requirement. Do not assert that all claims have already been verified by the human authors. |

## Verification scope

Citation occurrences, figure blocks, table cells/inputs and the vocabulary of
inline technical identifiers are preserved. Some repeated identifier mentions
were removed with redundant prose. Retained measurements, source snapshots,
converter code and the anonymous v0.5 demo are unchanged.

The input-provenance qualification adds ten words to the consolidated limitations
section (127 to 137); it replaces a longer passage in Tool Design. Full audit
coverage remains in `evidence/REPRODUCIBILITY_SCOPE.md`. Current compilation
and visual inspection are recorded in `compile-report.json`.
