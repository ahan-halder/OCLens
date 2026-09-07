# PoCL v7.2 probe notes

Ground-truth for the adapter. Split into what PoCL's own docs guarantee and
what we still need to record from a live GDB session.

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
| Cached kernel source | `tempfile-*.cl` under `POCL_CACHE_DIR` (DWARF `AT_name` / `AT_comp_dir`) |
| Program source alias | `program.cl` in the program cache directory |
| Kernel function | OpenCL kernel name, e.g. `vector_add` |
| Work-group wrapper | `_pocl_kernel_<name>_workgroup` inside `<name>.so` |
| Work-group .so | `.../<kernel>/<local-size>-.../<kernel>.so` |

`SourceMapper` matches `tempfile-*.cl` / `program.cl` by content hash against
the user's original file. GDB breakpoints must use the tempfile path because
that is what DWARF records.

## Live session (fill in after `./scripts/build_pocl.sh`)

```text
./scripts/build_pocl.sh
cmake -S . -B build -G Ninja
cmake --build build
./tools/probe_pocl.sh \
  --exe ./build/examples/minimal/minimal_host \
  --kernel vector_add \
  --source ./examples/minimal/minimal.cl
```

| Purpose | Observed symbol / expression | Notes |
|---------|------------------------------|-------|
| Work-group entry | _TBD_ | |
| Global ID state | _TBD_ | |
| Local ID state | _TBD_ | |
| Private context array | _TBD_ | needed for value projection |
