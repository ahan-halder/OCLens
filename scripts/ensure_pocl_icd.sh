#!/usr/bin/env bash
# Ensure PoCL is visible to the OpenCL ICD loader (needed when INSTALL_ICD=OFF).
set -euo pipefail

POCL_PREFIX="${1:-${POCL_PREFIX:-/opt/pocl}}"
VENDORS="${POCL_PREFIX}/etc/OpenCL/vendors"
LIB_DIR="${POCL_PREFIX}/lib"

if [[ ! -d "$LIB_DIR" ]]; then
  echo "ensure_pocl_icd: missing $LIB_DIR" >&2
  exit 1
fi

POCL_LIB="$(find "$LIB_DIR" -maxdepth 1 -name 'libpocl.so*' -print | sort -V | tail -1)"
if [[ -z "$POCL_LIB" ]]; then
  echo "ensure_pocl_icd: no libpocl.so under $LIB_DIR" >&2
  exit 1
fi

mkdir -p "$VENDORS"
ICD_FILE="${VENDORS}/pocl.icd"
if [[ ! -f "$ICD_FILE" ]] || ! grep -qF "$POCL_LIB" "$ICD_FILE"; then
  echo "$POCL_LIB" >"$ICD_FILE"
fi

# Optional smoke (never fail the build: pipefail + grep/clinfo can exit 141/1).
if command -v clinfo >/dev/null 2>&1; then
  if ! clinfo 2>&1 | grep -qi pocl; then
    echo "ensure_pocl_icd: warning: clinfo did not list PoCL (ICD file was written)" >&2
  fi
fi
