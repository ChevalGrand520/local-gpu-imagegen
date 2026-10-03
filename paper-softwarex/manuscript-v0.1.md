# Local GPU Imagegen: A local image-generation control plane with durable run records and explicit submission uncertainty

Zhen Cheng

School of Computer Science and Technology (School of Artificial Intelligence), Zhejiang Sci-Tech University, Hangzhou, China

Correspondence: ChengZhen0105@outlook.com

## Abstract

Local image-generation backends can accept a request even when the calling application loses the response. Repeating the request can create another accepted job, while refusing to repeat it can leave a useful operation incomplete. Local GPU Imagegen is an open-source Python control plane that exposes local image-generation workflows through the Model Context Protocol and an installable command-line interface. Its run engine retains durable records, freezes execution routes and applies an explicit guard when an earlier submission has an unknown outcome. The software separates client state from backend acceptance and completion evidence. We describe its architecture and illustrate its behavior using six fixed paired Windows operations with a ComfyUI backend. In the accepted-response-loss pair, the guarded path retained one accepted job and withheld another submission, but did not complete the original client run. In a pre-send failure pair, it also blocked despite zero upstream sends. A simple stop-after-unknown control matched these reported outcomes. The examples characterize a conservative submission contract and its completion cost; they do not establish improved image quality, saved GPU computation or general reliability. Source code, installation instructions and derived evidence checks support inspection and reuse, while private raw captures remain unavailable for independent recomputation.

Keywords: research software; Model Context Protocol; ComfyUI; durable run records; submission uncertainty; local image generation

## Software metadata

| Item | Candidate value |
|---|---|
| Software name | Local GPU Imagegen |
| Current package version | 0.9.1 |
| Source repository | https://github.com/ChevalGrand520/local-gpu-imagegen |
| Candidate branch | codex/ieee-access-adaptation-v1 |
| Draft input commit | 458cfaa; this is a manuscript input, not a newly published software release |
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

Local image-generation workflows increasingly connect an interactive client to a backend through a software adapter. A client may select a workflow, submit its parameters, inspect progress and retrieve an output image. This sequence involves several observable events: the product receives a call, an adapter sends a request, the backend accepts a job, the backend executes it and the client records completion. These events do not have interchangeable meanings. A failed response does not necessarily imply that no backend job exists.

Remote procedure calls and idempotent API design already explain why retrying an operation after a communication failure can repeat its effects [1,2]. The same problem appears when a local image-generation controller loses a response after backend acceptance. A repeated call can create another accepted job. Conversely, conservatively stopping after uncertainty can prevent a successful completion even if the first request never reached the backend. The useful engineering question is therefore what the software records and permits at this boundary.

Local GPU Imagegen provides a reusable control plane around local backends. It combines a thin MCP transport, explicit discovery and trust checks, a durable run engine and backend adapters. The software contribution described here is an inspectable integration of those components. The uncertainty guard is an evaluated feature of the product. It is not presented as a new exactly-once protocol. Recent work by Li explicitly studies tool-contract guards for unknown writes, readback and idempotency in agent systems [3]; our fixed local examples do not establish a distinct or superior recovery-policy class.

The intended reuse is in workflows that need explicit local backend selection, retained run state and inspectable completion failures. Potential users can examine the stored state and decide whether to investigate an unresolved run rather than infer success from a client message alone. This is a potential use case, not measured external adoption or a quantified improvement in scientific productivity.

## 2. Software description

### 2.1. Architecture

The MCP transport handles JSON-RPC, schemas, validation, dispatch, timeouts and structured results. Discovery, trust and capability routing precede execution. The run engine owns orchestration and delegates persistent state to RunStore. Backend loading and image generation are delegated to the generation module and its adapters. The repository includes ComfyUI and WebUI adapters and a Diffusers compatibility path; the retained paired experiment concerns ComfyUI only.

A durable run record connects the requested operation to its selected route, submission state and outputs. Root and child runs support explicit revisions rather than silently overwriting an earlier operation. The route is fixed for the operation, and route drift is rejected. Persistence allows a later invocation to inspect an unresolved submission state. These are software contracts, whose model-free tests are distinct from the paired backend execution record.

The distribution does not bundle a GPU backend or model weights. A user supplies an appropriate local backend and reviews the workflow and model selection. The MCP process does not call an application-specific cloud image API. Confirmed LAN endpoints transmit prompts and source images to that server; loopback is local. Trust records remain outside Git, and model downloads require an explicit download option. Generated and input images remain ordinary local files whose directory permissions are the user's responsibility.

### 2.2. Submission uncertainty

For the evaluated same-run path, an unknown submission outcome prevents another automatic submission. The guard consults retained run state and returns an unresolved result. This withholding does not by itself identify an accepted backend job, reconcile its output or complete the client operation. It also does not provide backend-wide deduplication across arbitrary processes or newly created runs.

The relevant boundary is the distinction between known failure before sending and an outcome recorded as unknown. If the caller lacks evidence sufficient to distinguish the two, withholding can be conservative with respect to repeated sends and costly with respect to completion. The pre-send example below exposes that cost directly. The implementation should therefore be interpreted as an explicit operational contract, rather than a guarantee that every uncertain operation can recover.

### 2.3. Inspection and interfaces

The installed CLI exposes serve, doctor, verify, config and setup contracts. The verify command checks the MCP interface; an isolated wheel installation reported version 0.9.1 and seventeen tools. That check establishes interface availability, not a complete image-generation workflow on the test machine.

Research records can additionally be exported using scripts/research/export_records.py from the source checkout. This exporter is supplementary research code and is not installed in the current wheel or source distribution. Twelve constructed same-information probes produced equal classifications for the exporter and a same-author field parser. Consequently, the paper does not claim that the exporter interprets records better than an ordinary parser, or that it reduces independent audit effort.

## 3. Illustrative examples and validation

### 3.1. Fixed paired protocol

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

In F02, B2 produces two accepted jobs with two bound execution lifecycles and completes the client operation. W3 retains one accepted job and one lifecycle, but leaves its original run unresolved even though backend completion is observed. This illustrates submission withholding together with a completion cost. It is not evidence of successful reconciliation.

The second B2 F02 lifecycle reports cached nodes 3 through 9. The retained aggregate progress events do not assign a measured amount of GPU computation to that lifecycle. Therefore, two accepted jobs must not be described as twice the computation, and withholding the second submission must not be described as measured GPU savings.

FPRE is the negative example. B2 eventually sends one upstream request and completes. W3 sends none and remains unresolved. The guard has blocked an operation whose first attempt did not reach the backend. This false block shows the consequence of recording an uncertain outcome without enough information to determine whether sending occurred.

A CPU stop-after-unknown control matches W3 on the reported F00, F02 and FPRE counts and completion outcomes. This comparison supports a simple interpretation of the guard and limits any claim of policy superiority. The six operations are fixed examples, with no repeated randomized campaign or population-level failure-rate estimate.

### 3.3. Software validation boundaries

The supported CI matrix passed on GitHub-hosted Windows and Ubuntu runners for Python 3.11 and 3.12 at revision caaa2e0, run 37090919543. These runners are separate from the author's physical Windows computer. CI is model-free software validation and does not establish current endpoint, GPU or named-client generation health. A focused Python 3.12 research suite passed 96 tests, and the isolated offline supplementary demo passed its four verification commands, including thirteen tests.

A macOS Python 3.12 full-suite attempt still reported thirty failures and five errors, with forty skips across 1,274 tests. The distribution identifies Windows as its product platform. Successful wheel/interface checks on the Mac must not be expanded into a macOS support or production-readiness claim. No new GPU run was performed to prepare this manuscript.

## 4. Impact and limitations

The software offers reusable interfaces and retained operational state around existing image-generation backends. A researcher can inspect the route and unresolved state and reproduce the offline derived-record checks without loading a model. The evaluated feature makes an uncertain submission visible and prevents another automatic same-run send. Its usefulness depends on whether this explicit stopping contract fits the user's workflow.

The present evidence does not quantify external reuse, user time savings, independent audit effort, image quality, performance, VRAM usage or general reliability. The examples also do not show that withholding improves eventual completion. Backend acceptance semantics and caching matter: a request count alone is insufficient to infer image-generation cost. Broader efficacy claims would require a separately designed experiment and an appropriate comparison.

The raw paired capture is private. It contains configuration, source snapshots, logs and images beyond the derived public record. An author-side consistency audit is not independent execution authentication. A private sanitized prototype preserves the derived rows and selected semantic relations, but is not yet a released or complete raw-data replacement. Reproducibility claims must remain at the level supported by the distributed software and derived checks.

## 5. Conclusions

Local GPU Imagegen integrates an MCP interface, local backend adapters and durable run records. Its fixed ComfyUI examples make the tradeoff between withholding uncertain submissions and completing client operations inspectable. The accepted-response-loss pair retains fewer accepted jobs under the guard, while the pre-send pair exposes a false block. Equal simple-stop and parser controls constrain the contribution to a software integration and bounded characterization. The source distribution and derived checks enable inspection, with explicit limits on backend execution reproduction and unsupported platform claims.

## Code and data availability

The source repository is publicly accessible at https://github.com/ChevalGrand520/local-gpu-imagegen under the MIT license. Installation and backend setup are described in its README. The package version is 0.9.1; the exact manuscript release revision and permanent software archive remain to be selected. The derived paired record and checker are in paper/evidence/paired-windows-projection-20261001.json and paper/scripts/verify_paired_projection.py. The research exporter is separate source-checkout code. The original paired raw archive and private sanitized prototype are unavailable for third-party recomputation in this candidate.

## Declaration of generative AI assistance

OpenAI Codex assisted with language refinement, experimental code prototyping, and cross-checking of author records. The author reviewed and revised the resulting materials and takes full responsibility for the manuscript.

## References

[1] Birrell AD, Nelson BJ. Implementing Remote Procedure Calls. ACM Transactions on Computer Systems. 1984;2(1):39–59. https://www.cs.cmu.edu/~15712/papers/birrell84.pdf

[2] Featonby M. Making retries safe with idempotent APIs. Amazon Builders' Library. https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/

[3] Li J. Where Does Exactly-Once Live? Model, Harness, and Tool-Contract Effects on Duplicate Side Effects in LLM Agents. arXiv:2609.29095v1. 2026. https://arxiv.org/abs/2609.29095v1
