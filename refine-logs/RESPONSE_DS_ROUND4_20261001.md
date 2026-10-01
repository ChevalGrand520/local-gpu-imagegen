# Response to DS fourth review: v0.21

Model-assisted author review, not an editorial decision or authenticity certification.
No new Windows/GPU measurement. Historical records unchanged.

V20-1: removed the probe's dependency on tests.test_asset_run_engine by including
its minimal standard-library PNG writer. The current report and stdout explicitly
record agreement_count. A fresh offline twelve-probe run returned PASS: both
views correct=12, unknown=3, false_affirmations=0, agreement_count=12. Main text
now says both matched the twelve declared answers and agreed on classifications.
This local rerun is an offline constructed check, not a replacement historical
receipt or a Windows experiment. Clean-package invocation is verified separately.

V20-2: clarified that zero progress applies to earlier v1/v2 F02 captures.
Paired B2/F02 progress=30 aggregates both lifecycles, whereas its second cache
message reports nodes3..9. Those facts are compatible; aggregate progress does
not assign work to the second lifecycle. Main text no longer treats cached nodes
as proof of zero computation or no full generation; neither count quantifies
physical GPU work. No cache-vs-sampling claim is newly certified.

V20-3: README explicitly labels historical full-checkout tests/research receipts;
the author ZIP does not include that tree. No whole research-suite extraction
claim is made. Probe command now works without it.

V20-4: Python>=3.10 is a prerequisite for the complete command set, not the
minimum of every standalone script. Use an explicit installed interpreter path
where python3.13 is absent from PATH. No unsupported claim of tested 3.10.

Compile: Tectonic exit0; six pages. v0.20 ZIP preserved, v0.21 delivered separately.
Clean v0.21 extraction: 143/143 manifest files match and probe invocation exit0,
agreement_count=12. Local research regression: 96 tests PASS in 9.563s.
Poppler confirms all fonts embedded; changed pages5--6 visually inspected without
obvious clipping or overlap. Anonymous v0.6 package is unchanged.
