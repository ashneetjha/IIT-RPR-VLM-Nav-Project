# Server-readiness check

## Local validation (this workstation)

- OS/runtime: macOS local workspace; Python `3.14.7`.
- GPU visibility: no CUDA-capable PyTorch installation was available (`torch` import failed), so no GPU/CUDA compatibility claim is made.
- Filesystem: Task 2 reports, outputs, and InternVL preparation files were created successfully.
- Checkpoint: no team-provided InternVL checkpoint path is present.
- Launcher: no team-provided distributed launch command, GPU count, or environment has been supplied.

## Server validation pending

Run `internvl/validate_internvl_config.py` after replacing every placeholder in `config_template.yaml`, then run `dry_run_internvl.py` with the server media root. Confirm selected InternVL checkout/version, checkpoint compatibility, PyTorch/CUDA and GPU visibility, release dependencies, writable output directory, and the exact `torchrun`/scheduler launcher. Local macOS validation is not a GPU-server validation.
