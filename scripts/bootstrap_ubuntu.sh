#!/usr/bin/env bash
# Bootstrap Ubuntu packages for OCLens development (PoCL v7.2 build deps).
set -euo pipefail

if [[ "$(id -u)" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

${SUDO} apt-get update
${SUDO} apt-get install -y \
  build-essential \
  ca-certificates \
  clang \
  clinfo \
  cmake \
  curl \
  gdb \
  git \
  libclang-dev \
  libclang-cpp-dev \
  libhwloc-dev \
  libllvmlibs-ocaml-dev \
  llvm-dev \
  ninja-build \
  ocl-icd-opencl-dev \
  pkg-config \
  python3 \
  python3-pip \
  python3-venv \
  spirv-tools \
  spirv-headers \
  zlib1g-dev

echo "Bootstrap complete. Next: ./scripts/build_pocl.sh"
