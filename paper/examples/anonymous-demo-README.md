# Anonymous offline demonstration candidate

Requires Python >=3.10 (dataclass slots). Clean extraction was tested with
Python 3.13.15; system Python 3.9 is unsupported. Select an installed compatible
interpreter explicitly. From the extracted archive root, run:

```sh
python3.13 paper/scripts/verify_reviewer_demo.py
python3.13 paper/scripts/verify_windows_projection.py
python3.13 -m unittest discover -s tests/research -q
```

This package contains the read-only evidence exporter, two **synthetic** input
records, retained **derived** Windows and CPU case records, and a consistency
checker. Its exporter tests include missing-state and manifest-identity conflict
cases. The exporter's local support-module directory and its import statement
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

The checker also passes twelve retained CPU product manifests and their fixture
oracle records through the exporter. It supplies no independent artifact
validator, so none becomes composite-verified. This is an offline consistency
and mapping check of retained synthetic traces, not a new execution campaign.

This is an author-side candidate. A sanitized package cannot guarantee that
publicly indexed source or data cannot be recognized, and the archive is not
an official DSN artifact-evaluation submission.

The Windows conversion projection includes two retained-case semantic inputs
and four explicitly synthetic stress variants. Only state, submission/job and
artifact-hash fields needed by the exporter are retained; job identities are
consistently pseudonymized. Their interpretation states were checked against
the full private conversions. The original manifests, raw events, captured Windows prompts,
host paths and generated images are excluded. Successful replay verifies the
delivered mapping and checksums, not the private source's authenticity,
completeness, live guard action or physical GPU work. No independent artifact
validator is supplied: both retained cases remain composite-unverified.

Synthetic CPU fixture prompts are included for inspection; they are not
captured Windows user prompts.

## Paired Windows derived projection

```sh
python3.13 paper/scripts/verify_paired_projection.py
```

This checks six derived paired rows, totals and the reported cache-node list.
The projection includes no raw prompts, machine paths or images. Its private
archive hash identifies the retained author archive; the archive is not included.
This command cannot replay raw events or independently verify execution.
The existing Windows conversion examples refer to a different earlier protocol;
they are not exporter conversions of this new paired batch.
