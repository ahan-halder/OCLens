# Source this file after `./scripts/build_pocl.sh`.
#   source ./scripts/env.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export POCL_INSTALL="${POCL_INSTALL:-$ROOT/pocl-install}"
export LD_LIBRARY_PATH="${POCL_INSTALL}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export OPENCL_VENDOR_PATH="${POCL_INSTALL}/etc/OpenCL/vendors"
export PATH="${POCL_INSTALL}/bin${PATH:+:$PATH}"
export CMAKE_PREFIX_PATH="${POCL_INSTALL}${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
