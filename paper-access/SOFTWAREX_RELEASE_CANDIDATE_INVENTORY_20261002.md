# SoftwareX release-candidate inventory, 2026-10-02

This is a local inventory, not a released package, submission or approval to
publish private evidence. Branch input: `codex/ieee-access-adaptation-v1` at
`41bdae58bb7f04d444c26afef0a9d9643655a239`. The DSN frozen tag and
`paper/` manuscript were not changed.

## Software identity and distributable pieces

| Piece | Current location and role | Verification / limit |
|---|---|---|
| Product source | `scripts/local_gpu_imagegen/`, `scripts/mcp_server.py`, profiles and workflows in the public `ChevalGrand520/local-gpu-imagegen` repository | The product is an MCP control plane with a same-run unknown-submission guard. Public source and MIT license are present; no backend/model is bundled. |
| Build artifacts | Local `uv build --offline` output: `local_gpu_imagegen-0.9.1.tar.gz` and `local_gpu_imagegen-0.9.1-py3-none-any.whl` | Build exited 0. The wheel metadata says `Author: Zhen Cheng`, MIT, Python >=3.11. SHA256: wheel `53fb809ec5042662950133f797d38a15a745f1325ea3713749e3545e894aa3db`; sdist `5ea20ca02b64a0fcb88fff95fd74a42e77146fe957e5c7f1c1d9ca29f8225481`. These `/tmp` builds are verification outputs, not an uploaded release. |
| Installed interface | Isolated wheel `local-gpu-imagegen verify` | Prior check exited 0, reported `ok: true`, version 0.9.1 and 17 tools on macOS. It proves packaging/interface availability, not Windows/ComfyUI generation. |
| Research exporter | `scripts/research/export_records.py` in source checkout | Not included in the wheel or sdist. A paper naming the exporter as part of the installed software must either package an explicit supported command or identify it accurately as separate supplementary research code. |
| Offline demo | Local ignored `paper/delivery/evidence-tool-anonymous-demo-v0.6.zip` | SHA256 `77213e7c8eb0b18edd335a828d69e0669088564853e4d6ffd202d08206ee0504`. Clean extraction on Python 3.13.15 passed `verify_reviewer_demo.py`, `verify_windows_projection.py`, `verify_paired_projection.py` and 13 exporter tests, all exit 0. Its manifest hashes 22 payload files. It demonstrates mapping and derived-record consistency, not the full product or real guard. It is not tracked in Git or published by this task. |
| Paired Windows projection | `paper/evidence/paired-windows-projection-20261001.json` plus `paper/scripts/verify_paired_projection.py` | Allows checking six derived rows and totals. It does not reconstruct raw observer/proxy/client records. |
| Private raw campaign | `paired-windows-captures/paired-windows-20261001-c.tar.gz` outside the repository | Retained SHA256 `141b1ea66af741f9e8cc917f7a7a33db5cb0d048989f76a25166775180f852f3`. Includes required raw records alongside source snapshots, configuration and generated images. Do not upload it wholesale. |

## Validation boundary

- Focused research suite: `uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python -m unittest discover -s tests/research -q` exited 0, 96 tests.
- Full suite: bare `python3.13 -m unittest discover -s tests -q` exited 1, with 1,173 tests, 23 failures, 29 errors and 32 skips. This is outside the documented Python 3.11/3.12 support range and lacked the project's isolated dependency recipe. Reported failures included postprocess preview evidence and release-candidate checks; this run does not identify a single root cause. The older classified macOS baseline also failed its full suite. Do not claim a passing full release gate.
- Clean demo tests are limited to the offline evidence subset. No GPU, model download, backend call or Windows validation was performed in this inventory.

## Minimum candidate before a SoftwareX manuscript

1. Keep the paper's software object explicit: the complete Local GPU Imagegen
   product, with the exporter named as a separate supplement until it is
   deliberately packaged and supported. Do not combine distinct artifacts into
   one claimed installed interface.
2. Select exact product, supplement and evidence commit IDs. Produce a clean
   checkout plus installation command and demo commands that a reviewer can
   run without private paths or a GPU for the offline portion.
3. Run the full product release gate on a supported Windows/Python setup and
   keep its failures and platform limits separate from the Mac component checks.
4. Decide whether a minimized, privacy-reviewed raw capture can support
   third-party recomputation. Inventory filenames and sensitive fields first;
   preserve the original TAR and its checksum. If no raw release is feasible,
   state exactly what cannot be rerun.
5. Resolve manuscript metadata: official English college name, ORCID if
   required, current journal template and current APC. Formal software author
   metadata is now `Zhen Cheng`; GitHub account `ChevalGrand520` is author
   controlled by the user's statement.

The next action is a candidate package design and privacy inventory. It does
not require a new GPU experiment. Public release, PyPI publication, a journal
submission or a stable-branch merge remain separate decisions.
