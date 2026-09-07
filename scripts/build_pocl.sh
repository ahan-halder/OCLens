#!/usr/bin/env bash
# Build and install PoCL v7.2 into a local prefix (default: ./pocl-install).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POCL_TAG="${POCL_TAG:-v7.2}"
POCL_SRC="${POCL_SRC:-$ROOT/pocl-src}"
POCL_BUILD="${POCL_BUILD:-$ROOT/pocl-build}"
POCL_PREFIX="${POCL_PREFIX:-$ROOT/pocl-install}"
JOBS="${JOBS:-$(nproc)}"

mkdir -p "$POCL_SRC" "$POCL_BUILD"

if [[ ! -d "$POCL_SRC/.git" ]]; then
  git clone --depth 1 --branch "$POCL_TAG" https://github.com/pocl/pocl.git "$POCL_SRC"
else
  git -C "$POCL_SRC" fetch --depth 1 origin "$POCL_TAG"
  git -C "$POCL_SRC" checkout "$POCL_TAG"
fi

cmake -S "$POCL_SRC" -B "$POCL_BUILD" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$POCL_PREFIX" \
  -DENABLE_ICD=ON \
  -DINSTALL_ICD=OFF \
  -DENABLE_LLVM=ON \
  -DLLVM_CONFIG=/usr/bin/llvm-config

cmake --build "$POCL_BUILD" -j"$JOBS"
cmake --install "$POCL_BUILD"

cat <<EOF

PoCL installed to: $POCL_PREFIX

Add to your shell before building/running examples:
  export POCL_INSTALL=$POCL_PREFIX
  export LD_LIBRARY_PATH=$POCL_PREFIX/lib:\${LD_LIBRARY_PATH:-}
  export OPENCL_VENDOR_PATH=$POCL_PREFIX/etc/OpenCL/vendors

Then rebuild examples:
  cmake -S . -B build -G Ninja -DCMAKE_PREFIX_PATH=$POCL_PREFIX
  cmake --build build

EOF
