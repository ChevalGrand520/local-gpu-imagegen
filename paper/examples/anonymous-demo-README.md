# Anonymous offline demonstration candidate

From the extracted archive root, run:

```sh
python3 paper/scripts/verify_reviewer_demo.py
```

This package contains the read-only evidence exporter, two **synthetic** input
records, retained **derived** Windows and CPU case records, and a consistency
checker. The exporter's local support-module directory and its import statement
were renamed for this candidate; its decision rules were not changed. The
archive manifest hashes the delivered bytes. The authors retain a separate
private source-to-delivery hash map.

The synthetic inputs differ in the original run's reported completion state.
Both supply successful backend and artifact-validation assertions. The tool
keeps those assertions visible but refuses a composite verified-completion
flag for the unresolved original run. These assertions are trusted inputs,
not authenticated evidence. This package cannot replay the Windows campaign,
rehash private images, reconstruct omitted raw WebSocket/history snapshots,
or demonstrate the live same-run guard. It needs only Python's standard library
and does not contact a backend.

This is an author-side candidate. A sanitized package cannot guarantee that
publicly indexed source or data cannot be recognized, and the archive is not
an official DSN artifact-evaluation submission.
