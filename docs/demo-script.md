# Demo script

```bash
source ./scripts/env.sh
source .venv/bin/activate
oclens debug \
  --exe ./build/examples/stencil_barrier_bug/stencil_barrier_bug \
  --kernel stencil_barrier_bug \
  --source ./examples/stencil_barrier_bug/stencil_barrier_bug.cl \
  --local-size 8,1,1
```

Inside GDB:

```text
(oclens) ocl-break 23
(oclens) ocl-wi global 5
(oclens) ocl-run
(oclens) ocl-locals
(oclens) ocl-next
(oclens) ocl-print result
(oclens) ocl-continue
```

Expected (in[i]=i+1, local size 8): stop only for global work-item 5;
`private_value=13`, `left=11`. The breakpoint is *before* the assignment, so
`result` is still 0; after `ocl-next`, `ocl-print result` shows `2` (the `-`
bug). The host then reports a mismatch at gid=5: expected 24 (`13+11`), actual 2.
