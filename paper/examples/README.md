# Offline tool demonstration

Requires Python >=3.10; tested with Python 3.13.15. System Python 3.9 is unsupported.
From the extracted reviewer bundle root, run:

```sh
python3.13 paper/scripts/verify_reviewer_demo.py
```

The two inputs are **synthetic** and differ only in the original run's reported
state. Both supply successful backend and artifact-validation assertions. The
tool retains those assertions, but keeps the unresolved run's recovery obligation
visible and does not set its composite `execution_verified` flag. Neither input
contains real image bytes or authenticated oracle provenance; the flag is a
versioned interpretation of supplied records, not certification of their origin.

The same command also checks the retained derived Windows and CPU records offline.
Those records support the tables in the paper. The command cannot replay the
Windows campaign, rehash private PNGs or reconstruct omitted WebSocket payloads.
It uses only Python's standard library and does not contact a backend.

For the newer paired batch, run `python3.13 paper/scripts/verify_paired_projection.py`.
This checks derived rows and totals only. Private raw event replay requires
the separately retained private archive and research audit entry; the public
projection is not a new exporter-normalization experiment.
