# PoCL v7.2 probe notes (Stage A)

Record ground-truth observations from `tools/probe_pocl` and manual GDB sessions here.

## Environment

- PoCL tag: `v7.2`
- Work-group method: `loops`
- Kernel debug info: enabled
- Optimisation: disabled

## Symbols to capture

| Purpose | Observed symbol / expression | Notes |
|---------|------------------------------|-------|
| Work-group entry | _TBD_ | break here first |
| Global ID state | _TBD_ | |
| Local ID state | _TBD_ | |
| Private context array | _TBD_ | shape for ValueProjector |

## Next steps

1. `./scripts/build_pocl.sh` (or use the Docker image)
2. `cmake -S . -B build -G Ninja && cmake --build build`
3. `./tools/probe_pocl.sh --exe ./build/examples/minimal/minimal_host --kernel vector_add`
4. Attach GDB, explore, fill the table above.
