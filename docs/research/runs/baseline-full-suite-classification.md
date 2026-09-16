# Full Suite Baseline Classification

This is the corrected W2 branch's complete model-free suite log. It is a
baseline/environment classification record, not an experiment result.

## Command And Result

Command:

```text
uv run --isolated --with "setuptools>=68" --with "Pillow>=10" --with "uv==0.11.16" --with "py7zr==1.1.3" python -m unittest discover -s tests -v
```

Exit code: `1`

Result: `1182 tests`, `28 failures`, `6 errors`, `41 skipped`.

The raw output is retained in
`docs/research/runs/baseline-full-suite.log`. The 18 research tests all
passed, including the exporter tests, oracle self-check tests, fault-matrix
semantic tests, and fixture-overlay regression. No research test was skipped,
failed, or errored.

## Classification

The 6 errors are environment/capability failures outside the research package:

- 1 `/proc/self/fd` descriptor-path error in the POSIX run of the portable
  extraction capability test.
- 1 packaging setup error because the isolated environment did not provide
  `pip` to the wheel-build subprocess.
- 4 atomic-report errors because the current macOS environment reported atomic
  report installation as unsupported.

The 28 failures are grouped as follows:

- 8 Windows-portable bootstrap extraction/service expectations observed on the
  current macOS/POSIX environment.
- 1 POSIX promotion capability expectation whose errno differed from the
  platform result.
- 19 installed-release/CLI checks blocked by the same isolated-environment
  `pip` installation failure: 17 installed-check failures and 2 release-
  candidate CLI failures.

These failures are retained and are not converted into research failures or
experimental outcomes. The suite result does not establish Windows behavior,
ComfyUI behavior, GPU execution, or deployment rates. The research package is
reported from its focused tests and deterministic matrix evidence.
