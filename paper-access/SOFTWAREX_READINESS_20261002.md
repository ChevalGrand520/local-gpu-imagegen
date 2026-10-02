# SoftwareX route assessment, 2026-10-02

Status: local readiness assessment only. No software or evidence was newly
published, no manuscript submitted, and no GPU/backend experiment run.
Publisher requirements below come from the official-guide check recorded in
`docs/research/fast-journal-fit-20261001.md`; confirm them again before filing.

## Recommended software scope

Describe **Local GPU Imagegen as the software**, with unknown-submission
guarding and inspectable run evidence as its evaluated features. The existing
product is an installable MCP control plane. The anonymous evidence demo is a
supplementary offline verifier, not a replacement for the software. A paper
about only the exporter would need a separately installable, supported tool;
that is not what the current wheel delivers.

The empirical result remains narrow: in six fixed paired Windows operations,
the guard withheld another submission while the original run remained
incomplete; the pre-send case showed a false block. CPU stop-after-unknown
matched W3 on the reported F00/F02/FPRE counts and completion, and twelve
constructed parser probes were equal. Do not claim reliability rates,
policy/classification superiority, image quality or GPU savings.

## Current gates

| Gate | Current evidence | Disposition |
|---|---|---|
| Public source and license | GitHub repository `ChevalGrand520/local-gpu-imagegen` was confirmed public on 2026-10-02. Root `LICENSE` is MIT; product source and English quickstart are present. | Available, but confirm author/rights metadata before submission. The license and `pyproject.toml` name `Capricorn`, while the draft names Cheng Zhen. Do not infer the legal relationship. |
| Installable product | `uv build --offline` built sdist and wheel from this branch (exit 0). Installing the wheel in an isolated, offline `uv run` and invoking `local-gpu-imagegen verify` returned exit 0, `ok: true`, version 0.9.1 and 17 MCP tools. | Component-level installation proven on this Mac. It does not prove the Windows/ComfyUI workflow or a fresh public release. |
| Research-feature packaging | Wheel includes `engine.py` and `run_store.py`, but neither wheel nor sdist contains `scripts/research/export_records.py`. | The guard is in the product; exporter is only in the source checkout/demo. Decide whether the paper's named software includes an installable exporter command or explicitly treats export as supplementary research code. |
| Offline supplementary demo | Clean extraction of `evidence-tool-anonymous-demo-v0.6.zip`; its reviewer, Windows-projection and paired-projection checks exited 0; 13 unit tests passed. | Reproduces mapping and derived consistency only. It omits live guard, backend and original paired raw capture. It is an author-side candidate, not a complete product release. |
| Paired-result reproducibility | Derived paired projection and checker are available. Private TAR matches the recorded SHA256 and contains raw observer/proxy/client records, full source snapshots, configuration and images. | A third party cannot rerun the raw-capture audit from current distributed files. Selective sanitization, rights review and clean extraction are needed before any release decision. Do not publish the whole TAR. |
| Journal format | Prior official-guide check records a mandatory template, at most 4,000 words excluding specified metadata, at most six figures, public repository/README/license and data-availability statement. | No SoftwareX template manuscript has been prepared. The seven-page Access PDF is not a SoftwareX submission file. Recheck live guide before conversion. |
| Cost and authorship | Prior publisher check recorded an APC of USD 1,920 excluding taxes. Current draft uses the provisional Romanized name `Zhen Cheng` and a provisional English college name. | Confirm current APC, budget, preferred author name, official affiliation wording, ORCID and correspondence details before submission. No payment or submission is implied. |

## Manuscript skeleton after the gates

Use SoftwareX's mandatory template and keep the software artifact primary:

1. Software metadata: repository, version/commit, license, platform,
   dependencies, author and code availability.
2. Motivation and significance: ambiguous backend acceptance in an existing
   local image-generation workflow; explicit scope and competing contracts.
3. Software architecture: run store, submission guard, backend adapter,
   evidence exporter, trust boundaries and user decision points.
4. Illustrative example: one accepted-response-loss run and the FPRE no-send
   case, using only supportable fixed-case counts.
5. Impact and limitations: inspectable states, false-block cost, simple-stop
   equivalence, private raw-capture limits and absence of measured GPU savings.
6. Availability and reuse: exact install/demo commands and a candid data
   availability statement.

The next useful local engineering gate is a **release-candidate inventory**:
identify precisely which product commit, exporter files, schema, examples and
derived records would be distributed; run those commands from a clean checkout;
then review licenses and private identifiers before proposing a public change.
This is preparation, not authorization to upload raw evidence, publish a new
package, change stable branches or submit the manuscript.
