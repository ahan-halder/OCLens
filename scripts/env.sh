# Source this file after `./scripts/build_pocl.sh` (native) or in the Docker image.
#   source ./scripts/env.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -d "$ROOT/pocl-install/lib" && -d "$ROOT/pocl-install/etc/OpenCL/vendors" ]]; then
  export POCL_INSTALL="$ROOT/pocl-install"
elif [[ -z "${POCL_INSTALL:-}" && -d /opt/pocl/lib ]]; then
  export POCL_INSTALL="/opt/pocl"
fi

if [[ -n "${POCL_INSTALL:-}" && -d "${POCL_INSTALL}/lib" ]]; then
  if [[ -x "$ROOT/scripts/ensure_pocl_icd.sh" ]]; then
    # shellcheck source=/dev/null
    "$ROOT/scripts/ensure_pocl_icd.sh" "$POCL_INSTALL" >/dev/null 2>&1 || true
  fi
  export LD_LIBRARY_PATH="${POCL_INSTALL}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  export OPENCL_VENDOR_PATH="${POCL_INSTALL}/etc/OpenCL/vendors"
  export PATH="${POCL_INSTALL}/bin${PATH:+:$PATH}"
  export CMAKE_PREFIX_PATH="${POCL_INSTALL}${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
fi
