# PoCL internals reference (OCLens v0.1)

Pointers for adapter authors:

- PoCL debugging guide: https://portablecl.org/docs/html/debug.html
- Work-item loops transform: `lib/llvmopencl/WorkitemLoops.cc` (PoCL v7.2)
- Work-item handler: `lib/llvmopencl/WorkitemHandler.cc`

OCLens does not vendor PoCL source; these links document the semantics we reverse
engineer through `PoclAdapter`.
