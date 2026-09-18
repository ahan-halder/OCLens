# Live demo script

Step-by-step commands for the `stencil_barrier_bug` kernel. Run from the repo root
with PoCL env loaded (`source ./scripts/env.sh`).

## Launch

```bash
source .venv/bin/activate
source ./scripts/env.sh
oclens demo
```

Equivalent: `./scripts/run_demo.sh` or `oclens debug` with paths from `scripts/run_demo.sh`.

## GDB commands (in order)

```text
ocl-break 23
ocl-wi global 5
ocl-run
ocl-locals
ocl-next
ocl-print result
ocl-continue
quit
```

**gid=5:** `private_value=13`, `left=11`, buggy `result=2` (correct sum would be `24`).

Host proof:

```bash
./build/examples/stencil_barrier_bug/stencil_barrier_bug
```

Automated backup: `make test-integration`.
