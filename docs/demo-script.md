# Demo script (Stage H)

Target workflow once Stages C–G are implemented:

```bash
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

Expected: stop only for global work-item 5; `private_value=12`, `left=10`, `result=22`
at line 23; after continue, host reports mismatch at gid=5 (buggy `-` stores 2 in `out[5]`).
