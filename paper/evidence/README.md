# Retained evidence package

windows-audit.json is a whitelisted, path-redacted read-only extraction from
retained Windows report and JSONL records plus current product-output byte
hash checks. It is not raw WebSocket evidence. No credentials, model paths,
images or private configuration are included. IDs are opaque observation keys.

Run `python3 paper/scripts/audit_retained_evidence.py` at repository root.
The script uses existing records only; no backend, GPU or new experiment.
Its CPU sources are the existing docs/research/runs/paired-v2-*.json files.
It verifies counts from CPU events and consistency of Windows retained bindings.
Hash equality of report and JSONL cases is a consistency check, not independence.
Observer receipt timestamps must not be interpreted as GPU execution durations.

Figures: build_figures.py (reportlab) creates protocol and scope diagrams.
They are schematic; no fabricated timing values or statistical estimates.
