# Known-job CPU walkthrough scope

Command actually executed, exit 0:
`uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python paper-softwarex/known_job_recovery_demo.py`
Output is retained in known-job-recovery-receipt.json. Product/test source is
unchanged from cited snapshot dfc8378; the walkthrough itself is new manuscript
supplement code. No full suite rerun or GPU/model operation occurred.

The walkthrough reuses the existing engine fixture and adapter fake-server
fixture. Engine calls and HTTP calls are intentionally separate checks. The
fixture reports a job ID before timeout, which differs from the missing-ID
accepted-response-loss condition. The defined stop-only control is a manifest
copy receiving no action, not the campaign's original P-stop execution. A
positive result establishes interface/retained-state behavior under these
synthetic conditions only.

Actual interface sequence:
`unresolved + backend_job.job_id` -> `get_run` ->
`[get_run, generate_round:recover]` -> same-key/hash `generate_round` ->
forwarded `recovery_job_id` -> `generated + rounds[0].image.path`.
Adapter-only sequence: known recovery_job_id -> GET history -> GET view;
zero POST prompt. There is no poll_history tool/action or completed run state.
get_run does not start the history query. A newly rendered synthetic image in
the fixture is not a previously generated real GPU image.

The adapter sends local idempotency_key as client_id. We have not verified a
server-side deduplication guarantee, so the paper describes the local key and
backend contract separately. Attempts to retrieve current upstream ComfyUI
server.py through official GitHub endpoints failed with connection resets;
do not replace this uncertainty with a universal claim about all versions.

The repeated Metadata-position criticism remains false for the actual DOCX:
its C1–C8 table immediately follows Metadata. Existing SVG is editable figure
source. Reference count alone is not a template-stated acceptance condition;
ecosystem references may be added when their primary sources are verified.
