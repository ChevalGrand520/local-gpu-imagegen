# Local GPU Imagegen: Durable run records for local image generation

Zhen Cheng

School of Computer Science and Technology (School of Artificial Intelligence), Zhejiang Sci-Tech University, Hangzhou, China

Correspondence: ChengZhen0105@outlook.com

## Abstract

Local GPU Imagegen is an open-source Python control plane for local image-generation workflows. Through Model Context Protocol, clients can inspect durable run records, frozen execution routes and uncertain submission outcomes. Six fixed paired Windows operations illustrate the ComfyUI submission guard. After acceptance-response loss, the guard retains one accepted job while leaving the original client run incomplete. A pre-send failure also causes a false block. A synthetic stop-after-unknown control matches these outcomes. Source-based checks distinguish backend acceptance, execution lifecycles and client completion. The software brings these interfaces and records into one inspectable system. Raw captures from the study remain private.

Keywords: research software; Model Context Protocol; ComfyUI; durable run records; submission uncertainty; local image generation

## Software metadata

| Item | Candidate value |
|---|---|
| Software name | Local GPU Imagegen |
| Current package version | 0.9.1 |
| Source repository | https://github.com/ChevalGrand520/local-gpu-imagegen |
| Source snapshot | dfc8378cb3d891f7951786bc4544cd971bd56a11; immutable GitHub commit link |
| Paired experiment source | 08539d5; distinct from the draft input |
| License | MIT |
| Implementation language | Python |
| Declared Python requirement | >=3.11; CI matrix uses Python 3.11 and 3.12 |
| Supported product platform | Windows; Ubuntu CI is software test coverage, not retained GPU generation evidence |
| Package dependency | py7zr==1.1.3; backend, model and workflow requirements are separate |
| Main interface | local-gpu-imagegen CLI and stdio MCP server |
| Documentation | Repository README.md and docs/ |
| Research supplement | scripts/research/export_records.py in the source checkout; excluded from the wheel and sdist |
| Permanent software archive | Not yet selected for this candidate |

## 1. Motivation and significance

Local image-generation clients use backend adapters to select workflows, submit parameters, inspect progress and retrieve images. A product call passes through several events: an adapter send, backend acceptance, execution and client completion. A failed response can leave a backend job running. Records that distinguish these events help users investigate incomplete operations.

Remote procedure calls and idempotent API design explain how communication failures can cause retries to repeat an operation's effects [1,2]. In local image generation, losing an acceptance response can lead to a second accepted job. Stopping after an uncertain outcome can also block completion when nothing was sent. The controller must record the available information and decide which subsequent actions to permit.

Local GPU Imagegen combines a thin MCP transport with backend discovery, trust checks, a durable run engine and backend adapters. Li evaluates a closely related guard in simulated services: it remembers writes with unknown outcomes and refuses unverifiable repeats [3]. We implement this kind of guard in a local image-generation system and examine its submission and completion behavior, including a pre-send false block. The contribution is an integration and a limited characterization of its behavior; the recovery policy is not new, and its comparative efficacy remains unestablished. Li also identifies a verification-only limit when no in-flight bound is known. That result does not establish that the unresolved runs in our study were unavoidable.

Effect-history models distinguish external events from runtime observations and identify the capabilities needed at the tool boundary to resolve ambiguous effects [4]. Verification-aware wrappers query task-specific postconditions before retrying and use server-side idempotency where available [5]. ToolPro records completed WRITE outcomes and replays them during program repair under an effect-typed replay discipline [6]. Each mechanism depends on information that a local unresolved record alone does not supply, such as an authoritative postcondition or a recorded completed-write outcome. Local GPU Imagegen makes this information gap visible in its ComfyUI integration. Its scope excludes ToolPro's program runtime and preserves the need for the verification and backend contracts studied in these works.

The software is intended for workflows that need explicit local backend selection and records of completion failures. Users can inspect retained state to investigate an unresolved run. External adoption has not been measured.

## 2. Software description

### 2.1. Architecture

The transport exposes a Model Context Protocol interface that declares protocol revision 2024-11-05 [7] and handles JSON-RPC, schemas, validation, dispatch, timeouts and structured results. Before execution, the system discovers backends, checks trust and selects a route according to backend capabilities. The run engine orchestrates execution, while RunStore persists its state. The generation module and its adapters load backends and generate images. The repository includes ComfyUI [8] and WebUI adapters, along with a Diffusers compatibility path. The retained paired experiment evaluates ComfyUI only.

![Figure 1. Installed control plane and source-only research supplement](figures/architecture.png)

Figure 1. Local GPU Imagegen architecture. Solid arrows show control relationships; dashed arrows show retained-record access. The exporter and checker are source-only supplements; the backend and models are user supplied. OpenAI Codex assisted in drafting the diagram specification and rendering code; its exact model version is pending confirmation.

A durable manifest records the selected route, submission state and outputs. Immutable child runs preserve earlier revisions. Subsequent attempts check the frozen route, reject changes to it and return unresolved state for inspection.

Users supply the GPU backend and model weights, then review the workflow and model selection. Neither is bundled with the distribution. The MCP process does not call an application-specific cloud image API. A confirmed LAN endpoint receives prompts and source images on its server; a loopback endpoint keeps this traffic local. Trust records remain outside Git, and downloading models requires an explicit download option. Input and generated images are ordinary local files. Users are responsible for their directory permissions.

### 2.2. Software functionalities

In the evaluated same-run path, the guard reads retained state and returns an unresolved result when the submission outcome is unknown. It then withholds another automatic submission. Withholding alone neither identifies an accepted job nor reconciles its output or completes the client run. Deduplication across arbitrary processes or newly created runs is outside the guard's scope.

The guard responds to recorded uncertainty, including uncertainty recorded before a request reaches the backend. The cases in Section 3 show the resulting completion cost.

When a backend job identifier is known, the ComfyUI adapter can poll `/history/<job_id>`, including during explicit recovery. In the unknown-submission path, the response has supplied no retained identifier. The product neither discovers that identifier automatically from backend history nor determines whether an unbound request is in flight. `local_gpu_get_run` reads local retained state and leaves backend acceptance unresolved. These implementation limits account for the uncertainty in F02; they establish no general impossibility result for ComfyUI.

The product's idempotency key binds an attempt to its locally retained request hash. The adapter sends this key as ComfyUI's `client_id`. A server-side deduplication guarantee has not been independently verified for this integration, so repeated `/prompt` requests cannot be assumed to return the original outcome required by Li's key-enabled contracts [3]. Recovering a retained job through history uses a different mechanism from service-level idempotent resubmission.

### 2.3. Inspection and interfaces

The installed CLI has serve, doctor, verify, config and setup commands. The verify command checks the MCP interface. In an isolated wheel installation, it reported version 0.9.1 and seventeen tools. This result confirms interface availability; a complete image-generation workflow was not validated on that machine.

The code and documentation links point to an immutable source snapshot containing README.md, Licence.txt, the product and research scripts. From the checkout root, `python -m pip install .` installs the product and `local-gpu-imagegen verify` checks its interface. The README covers backend setup. PyPI also has version 0.9.1 as a historical artifact separate from the cited source snapshot. Running `python paper/scripts/verify_paired_projection.py` from the checkout root checks the included derived table without submitting a backend job. The checker and exporter require the source checkout and are absent from the product wheel. This check verifies the accepted-job and completion distinctions in Section 3 without rerunning the Windows campaign.

To inspect an existing run, a client calls `local_gpu_get_run` with `{"run_id":"<existing-run-id>"}`. The response includes retained `state`, `request.route` and `attempts`. It also includes `recoverable_next_actions`, which retrieval computes and which need not be stored in the disk manifest. In the unknown-submission branch, the attempt has `status: unresolved` and `submission_outcome: unknown`, and the run has `state: unresolved`. A retry encounters `submission_outcome_unknown` before another send.

Other unresolved attempts can retain a backend job without an unknown-outcome field. RunStore permits recovery only when the idempotency key and request hash match. For the two-stage ComfyUI route, the engine forwards `recovery_job_id` so the adapter can poll the retained job without posting again. This recovery path differs from the evaluated unknown-submission branch. The frozen `request.route` records the backend, endpoint/model identity and workflow/compiler versions for subsequent checks. Retrieval can update local bookkeeping for stale attempts, but does not certify backend completion.

From the source checkout, scripts/research/export_records.py exports research records. Twelve synthetic offline probes produced equal classifications for the exporter and a field parser written by the same author. These probes used fixtures separate from the Windows capture bytes and involved no Windows or GPU execution. The Python 3.13.15 receipt is paper/evidence/v022-probe-command-receipt.json in the cited snapshot. Parser superiority and reduced audit effort remain unestablished by this comparison.

## 3. Illustrative examples

### 3.1. Fixed paired protocol

In the retained F02 guarded case, the product submits the selected ComfyUI workflow and the backend accepts it. Injected response loss prevents the product from retaining the returned job identifier. The observer records backend completion, while the original client run remains unresolved and the guard withholds another same-run generation call. A client can inspect this local state through `local_gpu_get_run` (Section 2.3), but retrieval cannot recover the missing identifier. This account combines the recorded outcome with the source interface contract. No later client session or recovery was measured. In the B2 path, repeated submission completes the client operation (Table 1).

The corrected Windows capture uses source revision 08539d5 and comprises six operations: one B2 path and one guarded W3 path for each of three fixed conditions. F00 is the normal condition. F02 loses a response after acceptance. FPRE fails before upstream sending. B2 repeats after the injected failure; W3 retains the unknown state and withholds another same-run submission. These labels denote the particular paths tested, not populations of users or workloads.

The campaign records ten product calls, eight proxy POSTs and six upstream sends. We report proxy submissions, upstream sends, accepted jobs, bound execution lifecycles and client completion separately. An accepted job count does not measure GPU work, and backend execution success does not imply completion of the original client run.

| Condition and path | Proxy POSTs | Upstream sends | Accepted jobs | Bound lifecycles | Client completed |
|---|---:|---:|---:|---:|---|
| F00 B2 | 1 | 1 | 1 | 1 | Yes |
| F00 W3 | 1 | 1 | 1 | 1 | Yes |
| F02 B2 | 2 | 2 | 2 | 2 | Yes |
| F02 W3 | 1 | 1 | 1 | 1 | No |
| FPRE B2 | 2 | 1 | 1 | 1 | Yes |
| FPRE W3 | 1 | 0 | 0 | 0 | No |

The table reproduces the tracked paired-windows-projection-v1 record. Its checker verifies derived rows and totals; it does not authenticate execution or reconstruct the private raw capture.

### 3.2. Accepted response loss and false blocking

In F02, B2 produces two accepted jobs with two bound execution lifecycles and completes the client operation. W3 retains one accepted job and one lifecycle. Although the observer records backend completion, the original W3 run remains unresolved: withholding the second submission has not reconciled the client run.

The second B2 F02 lifecycle reports cached nodes 3 through 9. The retained aggregate progress events provide no measured amount of GPU computation for that lifecycle. Two accepted jobs therefore do not establish twice the computation, and withholding the second submission establishes no measured GPU savings.

In FPRE, B2 eventually sends one upstream request and completes. W3 sends none and remains unresolved. The guard blocks an operation whose first attempt never reached the backend because its retained state lacks enough information to determine whether sending occurred.

A synthetic CPU stop-after-unknown control matches W3 on the reported F00, F02 and FPRE counts and completion outcomes. The match establishes equality in these fields only, leaving other run-state details outside its scope. This CPU result adds no Windows execution evidence and supports no claim of policy superiority. The six Windows operations are fixed examples without a repeated randomized campaign or a population-level failure-rate estimate.

### 3.3. Known-job recovery walkthrough

A separate CPU fixture exercises the retained-job branch of the two-stage route. The fake backend reports a job identifier through the product callback, then raises a timeout. The engine records `state: unresolved` and `attempts[-1].backend_job.job_id`. Calling `local_gpu_get_run` returns `get_run` and `generate_round:recover` without making a backend call. Re-entering `generate_round` with the same key and request hash forwards `recovery_job_id` to the fake runner. The engine records one round, its existing synthetic image and `state: generated`. It rejects a changed key before the call reaches the runner. A defined stop-only control takes no further action on the same retained manifest and remains unresolved. This fixture demonstrates the recovery operation; statistical policy superiority remains unestablished.

In a separate adapter check against a loopback fake HTTP server, a known `recovery_job_id` produces `/history/prompt-1` and `/view` requests with zero `/prompt` POSTs. The engine and adapter are checked independently, so the results cover two components without an integrated backend execution. The executable walkthrough and receipt accompany the manuscript as known_job_recovery_demo.py and known-job-recovery-receipt.json. Both checks use source-snapshot test fixtures, synthetic outputs and known identifiers. They involve no GPU execution, missing-identifier reconciliation or Windows F03 case. The walkthrough ends at `generated`; image acceptance/finalization remains a later operation.

![Figure 2. Retained-job recovery in the CPU engine fixture](figures/known-job-recovery.png)

Figure 2. CPU engine fixture with a retained job identifier. Retrieval exposes the recovery action; same-key/hash re-entry forwards the identifier and records a generated round. The stop-only branch takes no further action. The separate HTTP-adapter check queries history/view with zero prompt POSTs. OpenAI Codex assisted in drafting the schematic and Python rendering code; its exact model version is pending confirmation.

### 3.4. Software validation boundaries

GitHub-hosted Windows and Ubuntu CI passed on Python 3.11/3.12 (run 37090919543). At the cited software snapshot, 96 research tests passed under Python 3.12 with Pillow installed. An isolated rebuilt wheel also reported seventeen tools through `local-gpu-imagegen verify`. These checks used no models and ran in separate environments. Their scope excludes validation of the author's machine or GPU generation. An older Python 3.13.15 receipt records a distinct thirteen-test offline subset. Exact revisions, commands and scopes are recorded at https://github.com/ChevalGrand520/local-gpu-imagegen/blob/abb363992469c23eae354f2374af32ffc8c6b1ad/paper-softwarex/VALIDATION_20261004.md . The validation materials have their own revision, separate from the cited software snapshot.

A macOS full-suite attempt did not pass. The public validation materials do not include its full failure log. Windows is the product platform, and successful Mac interface checks do not establish full macOS support.

The manuscript package includes final-check-receipt-20261004.json and validation/cpu-report-20261004.json for repeated model-free software checks and the synthetic stop-control comparison. The CPU comparison uses frozen B2 and W3 variants, separately identified in validation/cpu-source-freeze-20261004.json; it does not replay the Windows capture. OpenAI Codex assisted with experimental code prototyping. The reported outcomes are taken from retained records and executable fixture checks.

## 4. Impact

A researcher can inspect an incomplete generation operation through its retained manifest and the retrieval tool. The records identify the confirmed route and distinguish unresolved submissions from generated or finalized images. The six derived rows can also be checked without loading a model.

The source-based checks report accepted-job counts, execution lifecycles and client completion separately. Researchers can use them to examine whether withholding another submission preserves completion and whether a repeated accepted job incurs additional computation. In the fixed examples, the guarded F02 and FPRE runs remain incomplete. Caching leaves the amount of additional computation unmeasured. The software provides these inspection functions around an existing backend.

### 4.1. Limitations

External adoption, changes in users' daily practice and downstream scientific or commercial impact remain unmeasured. The fixed cases establish neither general reliability nor improvements in completion, image quality, performance, resource use or audit effort. Request counts and cached execution lifecycles cannot establish GPU savings.

The private raw paired capture contains configuration, source snapshots, logs and images beyond the derived public record. The author-side consistency audit does not independently authenticate execution. A private sanitized prototype preserves the derived rows and selected semantic relations, but remains unreleased and incomplete as a replacement for the raw data. The distributed software and derived checks therefore support only limited reproduction.

## 5. Conclusions

Local GPU Imagegen integrates an MCP interface with local backend adapters and durable run records. The fixed ComfyUI examples document the completion cost of withholding uncertain submissions. After acceptance-response loss, the guarded path retains fewer accepted jobs; before sending, the same guard can falsely block completion. The simple-stop and parser controls produce equal outcomes in the compared fields, limiting the contribution to software integration and a bounded characterization of its behavior. Users can inspect the distributed source and derived records, subject to the limits on reproducing backend execution and validating additional platforms.

## Code and data availability

The cited software snapshot is https://github.com/ChevalGrand520/local-gpu-imagegen/tree/dfc8378cb3d891f7951786bc4544cd971bd56a11, with package version 0.9.1, MIT LICENSE and identical Licence.txt. This explicit snapshot is separate from the repository's default branch and historical PyPI artifact. The earlier paired experiment uses source revision 08539d5. The derived paired record and checker are in paper/evidence/paired-windows-projection-20261001.json and paper/scripts/verify_paired_projection.py. The exporter and checker are source-checkout supplements. The original paired raw archive and private sanitized prototype are unavailable for third-party recomputation. No archival DOI is claimed.

## Declaration of generative AI assistance

OpenAI Codex assisted with language refinement, experimental code prototyping, and cross-checking of author records. The author reviewed and revised the resulting materials and takes full responsibility for the manuscript.

Codex also assisted in drafting the explanatory diagram specifications and rendering code. The retained specifications and code render Figures 1 and 2. The exact model versions used for this assistance are pending confirmation before submission.

## Funding

This research received no specific grant from funding agencies in the public, commercial, or not-for-profit sectors. The author completed the work independently.

## References

[1] Birrell AD, Nelson BJ. Implementing Remote Procedure Calls. ACM Transactions on Computer Systems. 1984;2(1):39–59. https://www.cs.cmu.edu/~15712/papers/birrell84.pdf

[2] Featonby M. Making retries safe with idempotent APIs. Amazon Builders' Library. https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/

[3] Li J. Where Does Exactly-Once Live? Model, Harness, and Tool-Contract Effects on Duplicate Side Effects in LLM Agents. arXiv:2609.29095v1. 2026. https://arxiv.org/abs/2609.29095v1

[4] Trofimov A, Novikov B. When Tool Calls Succeed but Workflows Fail: Anomalies at the Agent-Tool Boundary. arXiv:2609.15397. 2026. https://arxiv.org/abs/2609.15397

[5] Mansoor IK, Phadke A, Rana P. Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures. arXiv:2608.02645. 2026. https://arxiv.org/abs/2608.02645

[6] Liu M, Li S, Zhang Y, Ma Y. Beyond Static Endpoints: Tool Programs as an Interface for Flexible Agentic Web Services. arXiv:2606.19992. 2026. https://arxiv.org/abs/2606.19992

[7] Model Context Protocol. Specification, protocol revision 2024-11-05. https://modelcontextprotocol.io/specification/2024-11-05 (accessed 2026-10-04).

[8] Comfy-Org. ComfyUI. Source repository. https://github.com/Comfy-Org/ComfyUI (accessed 2026-10-04).
