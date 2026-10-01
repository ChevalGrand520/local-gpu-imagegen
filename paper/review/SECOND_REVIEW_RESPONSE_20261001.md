# Response to second independent review

No new backend experiment; original reports and source snapshots are unchanged.

OPEN-1: The author ZIP is now explicitly PRIVATE in its package manifest,
exclusion metadata, manuscript and README. The metadata lists identifiers that
remain inside exact execution-source snapshots, model-audit JSON and runner
source. Those files are not anonymized because doing so would invalidate their
evidence hashes. This resolves the distribution-scope contradiction, not the
identifiability of the private archive. It must not be used as a public or blind
submission artifact. The separate anonymous demo is unchanged and remains the
external candidate. Actual raw captures stay excluded from both ZIPs.

OPEN-2: The manuscript says the checks were tested on Python 3.13.15 and use
Python 3.10 features; 3.10 compatibility itself has not been tested. A fresh
structured CPU receipt records the exact command, repository-root working
directory convention, interpreter version, start/end UTC times, exit code and
captured output. It is a current offline receipt, not historical Windows proof.

OPEN-3: The author archive now includes artifacts.py, errors.py,
two_stage_layout.py, visual_review.py and the core initializer. Clean-extraction
verification must exercise verify_reviewer_demo.py and the Windows projection
replay in the author ZIP as well as the exact execution-source hash checker.
The package still is not a complete runnable generation engine distribution.

Remaining minor points: abstract bindings are explicitly per historical case;
the v2 preflight summary includes whitelisted check names, booleans and exit
codes and binds the private receipt hash. Neither it nor source correspondence
is independent attestation. Proposed experiments remain unperformed. Final
external review of v0.13 and human submission declarations remain pending.
