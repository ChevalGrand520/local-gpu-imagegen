# Frozen source layout for SoftwareX inspection

This directory mirrors the 89 tracked files under `scripts/` at product revision
dfc8378cb3d891f7951786bc4544cd971bd56a11, byte for byte. It supplies the
`repo/src` source inspection layout required by the current SoftwareX Guide
for Authors. The mapping and SHA256 inventory are in
`paper-softwarex/submission/source-layout-manifest.json`.

The canonical installation and packaging configuration remains at the repository
root and uses `scripts/`; run `python -m pip install .` from that root, then
`local-gpu-imagegen verify`. This is a frozen submission copy, not a second
development or build tree. Product behavior and experiment results do not change.
Do not edit this copy separately from its declared immutable source revision.

The root README contains installation, backend configuration and usage
instructions. LICENSE.txt, LICENSE and Licence.txt contain the same MIT terms.
