# Author-side response to the v0.11 independent model review

No new GPU experiment. Original review and old packages are preserved.

| Finding | v0.12 action | Remaining boundary |
|---|---|---|
| F-MAJ-1 source hashes | Reconstructed separate v1/v2 snapshots from commits 6c2219e and a8e58eb, applying LF-to-CRLF translation. All 9 hashes per campaign match retained receipts. Delivered snapshots, provenance and verify_execution_sources.py. | Reconstruction establishes byte correspondence, not execution attestation or original file custody. Current caller is not the execution snapshot. |
| F-MAJ-2 runtime | README declares Python >=3.10, explicitly uses python3.13; clean extraction checked with 3.13.15. Runtime/command receipts included. | Minimum version follows language/library requirements; 3.10 itself was not tested. |
| F-MAJ-3 partial recovery | normalization-v4 maps partial run to unknown recovery. Extended test supplies otherwise sufficient independent evidence and confirms composite verification stays false. | Historical Table I fixture vocabulary is explicitly distinguished from exporter enumeration. Original data unchanged. |
| F-MAJ-4 private directories | Named author and anonymous ZIPs exclude delivery/private-same-run*, raw logs, images and private maps. Author ZIP includes explicit exclusion metadata. Distribution instruction says to send ZIPs only. | Local private captures remain preserved with restricted permissions; distributing the entire author directory would violate this scope. |
| F-MAJ-5 test/runtime receipts | Removed unsupported historical 40/7-test runtime/timing paragraph. Included fresh offline receipt, clearly dated/current, not a reconstruction of historical execution. | Historical test worktree attestation is unavailable. |

Minor corrections: progress means messages whose type is literally progress;
F02 has zero such messages but one progress_state message. Controls also contain
cache events. F02 cached-node list contains nodes 3--9; lifecycle evidence is
not physical GPU-work evidence. The one POST is scoped to the F02 case. Four
synthetic variants are explicitly enumerated. Synthetic CPU prompts remain
included; only captured Windows prompts are excluded. Earlier README notes
are labeled historical. Both run reports now enter the package file list before
manifest construction; metadata files explicitly do not self-hash.

The proposed paired-key, cache-invalidation and successful-retry experiments
are not performed here. They would require a separate frozen protocol. This
revision claims one fixed-case submission rejection, not generic duplication
prevention, physical execution savings or independent runtime attestation.

The v0.11 review does not certify revised v0.12. An external review of the revised
package remains pending; no editorial or human peer-review status is implied.
