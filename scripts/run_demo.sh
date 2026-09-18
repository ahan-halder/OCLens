#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x build/examples/stencil_barrier_bug/stencil_barrier_bug ]]; then
  echo "Build examples first: ./scripts/build_examples.sh" >&2
  exit 1
fi

exec oclens demo
