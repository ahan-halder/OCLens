#!/usr/bin/env bash
# Thin wrapper around tools/probe_pocl.py
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/tools/probe_pocl.py" "$@"
