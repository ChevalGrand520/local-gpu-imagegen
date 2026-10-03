# SoftwareX revision validation receipt

Source snapshot: dfc8378cb3d891f7951786bc4544cd971bd56a11.
Product/research source remained unchanged during these commands. Later edits
are manuscript, figure/builder and README changes; not backend/GPU execution.

| Check | Exact invocation / artifact | Result / boundary |
|---|---|---|
| Research suite | `uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python -m unittest discover -s tests/research -q` | exit 0; 96 tests in 10.416 s; model-free |
| Build | `uv build --offline --out-dir /tmp/softwarex-review-build` | exit 0; 0.9.1 wheel and sdist; not uploaded |
| Isolated wheel | `uv run --offline --no-project --python 3.12 --with /tmp/softwarex-review-build/local_gpu_imagegen-0.9.1-py3-none-any.whl local-gpu-imagegen verify` | exit 0; ok=true; version 0.9.1; 17 tools; interface only |
| Wheel inventory | ZIP member and METADATA inspection | Author Zhen Cheng; no research exporter or paired checker members |

Historical receipts, available in the same source snapshot:
- `paper/evidence/v022-probe-command-receipt.json`, introduced at 9dd0634:
  twelve synthetic offline fixture probes, Python 3.13.15, no Windows/GPU.
- `paper/evidence/revision-v012-runtime-check.json`, introduced at 01c5e33:
  thirteen-test older offline subset, Python 3.13.15; not the 96-test suite.
- CI at caaa2e0: https://github.com/ChevalGrand520/local-gpu-imagegen/actions/runs/37090919543
  GitHub-hosted Windows/Ubuntu Python 3.11/3.12; historic retained result,
  not a new real-generation validation or author-machine health check.

PyPI 0.9.1 JSON was read during this revision:
https://pypi.org/pypi/local-gpu-imagegen/0.9.1/json . It exists and retains
historical author metadata Capricorn. The above wheel was rebuilt from the
cited source, with Zhen Cheng metadata; do not conflate those artifacts.
No registry upload, package replacement or new release occurred.

v0.3 document gate: final six-page rendering inspected in full; figure and
caption are together, five numbered main headings and page numbers correct,
no clipping or table split. DOCX section XML and metadata left columns match
the retained template exactly; 26 preserve-only original parts are identical.
The six DOCX result rows match the tracked projection JSON. The projection
checker passed again; derived consistency only. Abstract remains 100 words;
the full Markdown is below 2700 words, conservatively under the template limit.
