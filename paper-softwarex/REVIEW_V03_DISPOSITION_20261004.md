# Disposition of the supplied v0.3 targeted model review

Input manuscript revision abb3639; revised manuscript v0.4. The model review
concludes that small corrections permit submission-material preparation.
This disposition is not an editor decision or independent execution evidence.

| Item | Verified action |
|---|---|
| N1 validation location | Added a full immutable abb3639 link to VALIDATION_20261004.md and distinguished this manuscript-material revision from software snapshot dfc8378. |
| N2 recovery branch | Restricted submission_outcome_unknown to the unknown-submission branch. Explained retained-job recovery with matching key/hash. Code inspection further limits engine recovery_job_id forwarding to TWO_STAGE_TEMPLATE_ID; the review's unqualified recovery description would be too broad. |
| N3 unresolved state | Explicitly states that other unresolved attempts can retain a backend job without submission_outcome=unknown. No claim that all unresolved records have this field. |
| N4 Li EOS comparison | Optional numerical addition omitted. v0.3 already avoids claiming that Li never measures completion costs. Its composite EOS metric does not directly equal our client-completion count; adding numbers is unnecessary for this local correction. |
| N5 figure arrows | Caption explains solid control relationships and dashed retained-record access. Avoids blanket read-only classification of RunStore operations: get() can perform stale-attempt bookkeeping. |
| N6 derived actions | States that recoverable_next_actions is computed and appended during retrieval, not necessarily a disk-manifest field. |
| Optional machine-readable test receipts | Existing exit-zero test/wheel checks and command receipt retained; no repeated suite run merely to reformat a prior observation. Future release verification should capture structured process output directly. |

Remaining boundaries: no external adoption/research-output evidence, no original
raw-event replay by third parties, no new GPU experiment. Source layouts,
administrative declarations, current APC and other full-guide-only requirements
still need current publisher verification before submission. The review's
"no experiment" recommendation applies to the present claims; it is not a
general ban on all future comparisons because Li exists.

v0.4 keeps software snapshot dfc8378 and paired experimental source 08539d5.
It does not merge main, replace the PyPI artifact, create a DOI or submit.
