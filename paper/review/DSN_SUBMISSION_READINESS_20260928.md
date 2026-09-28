# DSN Tool submission readiness, 2026-09-28

Status: technical draft complete; the DSN 2027 submission portal currently says submissions are closed. Author-owned fields are also open. This is an author-side readiness check, not an acceptance prediction.

## Official time and payment evidence

The official [DSN 2027 research-track CFP](https://dsn2027-berlin.github.io/call-for-contributions/) lists abstract deadline **November 25, 2026**, full-paper deadline **December 2, 2026**, early rejection **January 26, 2027**, rebuttal/revision **February 12-26, 2027**, final notification **March 18, 2027**, and camera-ready **April 24, 2027**. All deadlines are AoE. Full-paper deadline to final notification: 106 days, about 15 weeks. The title and authors cannot be changed after the abstract deadline.

The official [DSN 2027 HotCRP site](https://dsn27.hotcrp.com/) displayed **"Submissions are currently closed"** on September 28, 2026. Its opening date is not stated there, so the earliest possible submission date is currently unknown. The earlier claim that no DSN 2027 CFP was available was incorrect; searches of guessed domain names missed the actual Berlin site.

The [DSN 2027 CFP](https://dsn2027-berlin.github.io/call-for-contributions/) requires at least one author of each accepted paper to take a regular registration and present in person. It does not list a submission charge. The 2027 registration price and refund policy have not been verified. The 2026 [registration page](https://dsn2026.github.io/registration.html) required distinct full author registration for accepted papers and made author registration non-refundable. There is no basis in the published 2027 CFP to charge a rejected paper a conference registration fee; verify any new portal terms when submissions open.

## Readiness ledger

| Item | Current evidence | Remaining work | Owner / estimate |
|---|---|---|---|
| Core manuscript | Six-page Tool draft, two figures, two tables, eight references; latest build has a 134-word abstract, embedded fonts, no undefined citations or overfull boxes | Final author read for scientific claims | Writing team and authors |
| Scientific scope | Windows 4 fixed cases; no same-run guard efficacy claim; retained binding and event-count limits named | Check all abstract/table/caption claims against source and retained evidence one last time | Writing team, about 0.5-1 day |
| Tool demonstration | Synthetic complete/unresolved inputs, runnable exporter check, and derived-record audit pass in clean extracted v0.1 and sanitized v0.2 ZIPs | v0.2 is only an offline exporter/audit candidate; decide access route and whether public-source recognition is acceptable | Writing team and authors |
| Anonymous submission | PDF author line anonymous; exact project slug removed; six pages rendered and inspected; [anonymity/source audit](ANONYMITY_SOURCE_AUDIT_20260928.md) records v0.1 and v0.2 | Repeat exact-byte PDF check after final edit; author decision on public code/data linkage and artifact intent | Writing team and authors |
| Declarations | Names, affiliations, contributions, funding and conflicts unconfirmed; the paper now has a distinct AI Tool Usage section | Authors supply truthful values and approve policy-compliant wording; never invent absence of funding/COI | Authors, variable |
| Venue terms | 2027 Tool: seven pages excluding references; double blind; abstract <=150 words; embedded fonts; dates and HotCRP confirmed | Check portal opening; complete abstract title and author list before November 25, 2026 | Authors and writing team |
| Publication cost | 2027 CFP requires accepted-paper regular author registration; no submission charge stated | Check 2027 registration price and travel budget when published | Authors, after acceptance |

The active manuscript is not yet a certified submission PDF. The existing delivery ZIP is an **author-review** bundle and should not be uploaded as an anonymous research artifact. The smaller `evidence-tool-reviewer-demo-v0.1.zip` is a local runnable candidate with a directly identifying support-package path. A separately sanitized v0.2 ZIP exists locally, but is not anonymity-certified or published. The [2027 CFP](https://dsn2027-berlin.github.io/call-for-contributions/) puts artifact evaluation after paper acceptance and does not require uploading the artifact with the initial paper; the submission does ask whether an artifact is intended.

The v0.1 demo contains 17 hash-checked files plus a manifest. In a clean extraction, `python3 paper/scripts/verify_reviewer_demo.py` reproduced both synthetic interpretation states and audited the retained derived records. A focused scan found no user home path, named repository owner, Windows user path, credential key marker or private-key header. The `scripts/local_gpu_imagegen` path remains a searchable identity fingerprint, so v0.1 is **not** an anonymous submission artifact. See the [audit](ANONYMITY_SOURCE_AUDIT_20260928.md). The generated ZIP is excluded from Git; its checksum must be recalculated after any rebuild.

## Estimated work and decision gate

Excluding waiting for the portal to open and author responses, approximately **3-5 focused working days** remain for manuscript and artifact preparation. This is an effort estimate, not a deadline or promise of acceptance. The main research limitation persists: the Windows campaign does not measure same-run guard efficacy and lacks retained raw terminal payloads. No amount of formatting can turn those observations into a stronger mechanism claim; the paper instead discloses this boundary.

Submission gate: HotCRP accepts submissions; paper and optional artifact satisfy the 2027 format/anonymity requirements; title and author list finalized before the abstract deadline; author-owned declarations and release rights confirmed; final PDF/ZIP checksums and clean extraction recorded; authors review the exact final files. Only then submit. No new GPU run or model download is required by this preparation checklist.
