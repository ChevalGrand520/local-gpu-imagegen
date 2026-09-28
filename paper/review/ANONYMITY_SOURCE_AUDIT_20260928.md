# DSN Tool draft and offline demo: anonymity/source audit

Date: 2026-09-28. Scope: local `paper/main.pdf`, `paper/main.tex`, references, and `paper/delivery/evidence-tool-reviewer-demo-v0.1.zip`. This is a static author-side audit, not a venue certification or publication decision.

## Findings

| Surface | Observed | Disposition |
|---|---|---|
| PDF identity metadata | The rebuilt six-page PDF reports the paper title, LaTeX creator, xdvipdfmx producer, and no custom metadata stream; `pdfauthor` is empty in source and pypdf reports no author | No direct author identity observed in these fields; repeat on the final upload bytes |
| PDF visible author line | `Anonymous submission draft`; rebuilt page 1 was rendered and visually checked for clipping/overlap | Appropriate as a placeholder; remaining pages and final venue template/author format still need inspection |
| Manuscript prose | The previous opening named the exact public project slug `local-gpu-imagegen`; it is now changed to `Our prototype`. Extracted text from the rebuilt PDF contains the latter and not the former | Removes one direct search key from the paper, without concealing technical architecture |
| Bibliography | Eight works include ordinary external URLs and an arXiv preprint; no author-project URL found | Bibliographic choices and self-citation status require final human review |
| Demo ZIP paths and payload | 17 selected files plus `PACKAGE_MANIFEST.json` (18 ZIP entries); no personal home path, owner handle, GitHub project URL, Windows user path, private-key header, or API-key assignment matched a focused text scan | Static negative scan is limited; filename/module `scripts/local_gpu_imagegen` remains a public-project fingerprint |
| Demo source scope | Runnable exporter and offline derived-record audit; no `engine.py`, backend adapter, live observer, proxy, or guard implementation in this bundle | Do not describe this ZIP as a complete source release or guard demonstration |
| Demo data provenance | Synthetic `complete`/`unresolved` records and retained derived Windows/CPU evidence; raw Windows event/history snapshots and private PNGs absent | Offline verification checks consistency of retained claims, not independent replay or authentication of the original campaign |
| ZIP filesystem metadata | Regular-file mode bits and 2026-09-27/28 per-file timestamps are present; manifest has generated timestamp | Timestamps do not identify an author here, but an eventual anonymous archive should use a normalized build and be scanned again |

## Release gate

**Do not upload the current v0.1 ZIP as a double-blind artifact.** The package module path can identify the public repository through source search, and its scope is narrower than a full implementation. The existing author-review manuscript ZIP is also not anonymous. The rebuilt manuscript PDF is a draft candidate: its text and metadata passed this focused audit, but a final visual review and repeat check on exact upload bytes remain.

Before any reviewer-facing release, choose whether the tool can be disclosed under DSN's double-blind rules. If yes, create a separately named anonymous export from a frozen source commit, retain a private path/hash mapping for authors, remove searchable owner/repository identifiers without altering behavior, normalize archive metadata, validate every file hash after extraction, and rerun the offline demo in a clean directory. Disclose the missing raw events and private artifacts in its README. If identity-preserving source cannot be released without breaking the tool, submit only the paper and describe the access limitation accurately; do not imply reviewer access that does not exist.

This audit does not inspect private Windows originals, external code-host search results, or every possible identifying string. No claim of complete anonymity is made.
