# WDDM process-view gate amendment

The live RTX 5070 Ti WDDM driver lists desktop/browser processes as C+G in
both its process table and compute-app query. An empty compute-app list is
therefore incompatible with the observed desktop baseline. On 2026-10-01 the
user reported training released and explicitly authorized autonomous research.

The gate now accepts an explicit prelaunch baseline of exact PID/path pairs.
Defaults remain empty. New or renamed processes stop acquisition; Python,
ComfyUI, training, CUDA and WSL executable names cannot be baseline entries.
No application is terminated to establish this baseline. Retain the complete
query and baseline in private records. This view and the operator exclusivity
declaration do not authenticate GPU exclusivity or physical computation.
Graphics baseline processes can still use GPU resources and introduce timing
variation; latency describes this desktop environment, not isolated hardware.

Local validation: 22 runner tests PASS; 93 research tests PASS in 9.443s,
`python3.13 -m unittest discover -s tests/research -q`, exit 0.
No historical captures or Tool v0.18 artifacts changed.
