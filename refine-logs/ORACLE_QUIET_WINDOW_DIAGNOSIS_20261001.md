# Oracle quiet-window diagnosis

Retained attempt B used d81f667. Offline analysis only; no new GPU run.

## Root cause and evidence

`ComfyUIEventOracle.observe_until` set a one-second socket timeout in the paired
controller and broke out on the first socket.timeout. Thus a quiet model-loading
interval ended observation before the separately configured monotonic deadline.
The W3/F02 raw messages end at wall time 1790842452.5570872; the only retained
history query is at 1790842453.5849013, approximately 1.028 seconds later.
The backend log ends at Requested to load SDXL. This agrees with the early-exit
path, not evidence of failure to finish in the full 109.4845953-second window.

Both healthy controls still have complete bindings. W3/F02 still has an accepted
job, response suppression, same-run guard rejection and one proxy POST. Its
complete lifecycle remains unknown: the runner cleaned the owned backend after
the observer returned. No later completion is reconstructed from these bytes.
This diagnosis does not establish how long the backend would have taken.

## Repair

Use select readiness polling while preserving the operation deadline. Silence
continues observation; terminal events trigger history rechecks. Once readable,
read the frame with the remaining deadline, so a short poll timeout cannot
discard a partly consumed header/body and corrupt the next frame. Socket close,
malformed frame and incomplete frame at deadline remain failure boundaries.
The retry schedule, fault injection, product revisions and T formula are
unchanged. Historical captured observer sources are not modified.

Two CPU real-socket tests cover a greater-than-one-second silence followed by
split terminal-frame delivery and a fully silent socket reaching its fixed
deadline. History content in these tests is synthetic and explicitly mocked.
They establish reader behavior, not Windows completion or GPU execution.

Final local receipt: `python3.13 -m unittest discover -s tests/research -q`,
exit 0, 96 tests PASS in 10.048 seconds. Windows has not run this corrected
observer. `git diff --check` passed.

## Next measurement gate

A rerun needs a new campaign ID, explicit current reservation and corrected
source bytes frozen before launch. Identify it as a corrected-observer revision
of paired-ambiguity-v1; never pool it with attempt B or retrospectively promote
B's E_bound. Preserve the same deadlines initially: no evidence yet justifies
increasing them. Six-operation coverage and paired advantage remain unmeasured.
Tool v0.18 remains frozen; no new efficacy claim enters its manuscript.
