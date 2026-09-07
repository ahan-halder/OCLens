# OCLens architecture notes

This document expands the README's risk-first build order with acceptance criteria
and component boundaries. The README remains the user-facing overview; this file is
for contributors implementing Stages A–H.

## Design principle

GDB owns DWARF parsing and inferior control (`ptrace`). OCLens owns OpenCL semantics:

- work-item identity (global / group / local);
- filtered breakpoints;
- private-variable projection from PoCL's context arrays;
- stepping that stays attached to one work-item.

All PoCL version-specific knowledge lives in `gdb/oclens_gdb/pocl_adapter.py`.

## Stage gates

| Stage | Deliverable | Acceptance |
|-------|-------------|------------|
| A | Docker + `tools/probe_pocl` + `docs/probe-pocl-7.2.md` | GDB stops inside a real PoCL kernel |
| B | `oclens doctor`, `oclens debug`, extension load | `ocl-help` works in GDB |
| C | `SourceMapper` | Unfiltered `ocl-break` hits correct `.cl` line |
| D | `PoclAdapter.read_current_work_item` | IDs match coordinate math at stops |
| E | `WorkItemBreakpoint` | One stop for selected WI, not N |
| F | `ValueProjector` | `ocl-locals` shows source scalars |
| G | `StepController` | Active WI unchanged across `ocl-next` |
| H | `stencil_barrier_bug` demo + integration tests | Host proves bug; pytest markers pass |

## Backend protocol (post-MVP)

Future backends implement a small protocol:

```text
DebugBackend
  load_kernel(...)
  read_current_work_item() -> WorkItemIdentity
  project_variable(name, wi) -> str
  continue / step
```

v0.1 only ships `PoclGdbBackend` (GDB + PoCL CPU).

## Probe methodology

1. Run the example host once with debug-friendly PoCL env vars.
2. Locate PoCL cache `.cl` copy and work-group `.so`.
3. In GDB, break on the work-group function; dump locals and symbol names.
4. Record findings in `docs/probe-pocl-7.2.md` — this becomes the adapter contract.
