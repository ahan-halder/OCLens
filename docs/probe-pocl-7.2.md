# PoCL v7.2 probe notes

Ground-truth for the adapter. Split into what PoCL's own docs guarantee and
what we recorded from a live GDB session against this tree.

## Environment OCLens sets

- PoCL tag: `v7.2`
- `POCL_EXTRA_BUILD_FLAGS=-g -cl-opt-disable`
- `POCL_LEAVE_KERNEL_COMPILER_TEMP_FILES=1`
- `POCL_WORK_GROUP_METHOD=loops`
- `POCL_WILOOPS_MAX_UNROLL_COUNT=0`
- `POCL_CPU_MAX_CU_COUNT=1`
- `POCL_CACHE_DIR` defaults to `$XDG_CACHE_HOME/oclens/pocl` or `~/.cache/oclens/pocl`

## Documented cache / debug layout

From [PoCL debugging](https://portablecl.org/docs/html/debug.html) and
[`pocl_cache.c`](https://github.com/pocl/pocl/blob/v7.2/lib/CL/pocl_cache.c):

| Item | Documented location / name |
|------|----------------------------|
| Cached kernel source | `tempfile-*.cl` / `tempfile_XXXX.cl` under `POCL_CACHE_DIR` |
| Program source alias | `program.cl` in the program cache directory |
| Kernel function (DWARF) | OpenCL kernel name, e.g. `stencil_barrier_bug` |
| Work-group wrapper (exported) | `_pocl_kernel_<name>_workgroup` inside `<name>.so` |
| Work-group .so | `.../<kernel>/<local-size>-.../<kernel>.so` |

`SourceMapper` binds the DWARF tempfile path from the current frame, then
checks that its contents match the user's original `.cl`. GDB breakpoints
must use the tempfile path because that is what DWARF records.

## Live session (PoCL 7.2, LLVM 18.1.3)

```text
./scripts/build_pocl.sh
source ./scripts/env.sh
cmake -S . -B build -G Ninja
cmake --build build
./tools/probe_pocl.sh \
  --exe ./build/examples/minimal/minimal_host \
  --kernel vector_add \
  --source ./examples/minimal/minimal.cl
```

Observed:

| Purpose | Observed symbol / expression | Notes |
|---------|------------------------------|-------|
| Kernel function | `stencil_barrier_bug` / `vector_add` | pending GDB break; DWARF, not exported from the .so |
| Work-group entry | `_pocl_kernel_<name>_workgroup` | only `T` symbol in `nm` of the .so |
| Cached source | `$POCL_CACHE_DIR/tempfile_XXXX.cl` | content-identical to the host-loaded .cl |
| Line 23 stop | `int result = private_value - left;` | `ocl-break 23` then `ocl-run` |
| Private locals | `in`, `out`, `n`; `out` often `<optimized out>` | even with `-cl-opt-disable` |
| Local array | `stencil_barrier_bug.scratch` BSS | from `nm` on the .so |

Work-item IDs (`gid` / `lid`) are the next adapter target: they are compiler
materialized, not ordinary DWARF locals of the original OpenCL names.
