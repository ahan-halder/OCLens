# OCLens development image — pins PoCL v7.2, LLVM, GDB+Python, and build tools.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV POCL_TAG=v7.2
ENV POCL_PREFIX=/opt/pocl
ENV OCLENS_ROOT=/workspace

RUN apt-get update && apt-get install -y \
    build-essential \
    binutils \
    ca-certificates \
    clang \
    clang-18 \
    clinfo \
    cmake \
    curl \
    gdb \
    git \
    libclang-dev \
    libclang-cpp-dev \
    libhwloc-dev \
    libhwloc15 \
    llvm-dev \
    llvm-18-dev \
    ninja-build \
    ocl-icd-opencl-dev \
    pkg-config \
    python3 \
    python3-pip \
    python3-venv \
    spirv-tools \
    spirv-headers \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/ensure_pocl_icd.sh /usr/local/bin/ensure_pocl_icd.sh

WORKDIR /tmp
RUN git clone --depth 1 --branch ${POCL_TAG} https://github.com/pocl/pocl.git pocl-src \
    && cmake -S pocl-src -B pocl-build -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${POCL_PREFIX} \
        -DENABLE_ICD=ON \
        -DINSTALL_ICD=OFF \
        -DENABLE_LLVM=ON \
        -DLLVM_CONFIG=/usr/bin/llvm-config-18 \
    && cmake --build pocl-build -j$(nproc) \
    && cmake --install pocl-build \
    && chmod +x /usr/local/bin/ensure_pocl_icd.sh \
    && ensure_pocl_icd.sh "${POCL_PREFIX}" \
    && for tool in ld clang clang-18; do \
         if [ -x "/usr/bin/${tool}" ]; then \
           ln -sf "/usr/bin/${tool}" "${POCL_PREFIX}/bin/${tool}"; \
         fi; \
       done \
    && rm -rf /tmp/pocl-src /tmp/pocl-build

ENV PATH="/opt/pocl/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ENV LD_LIBRARY_PATH="/opt/pocl/lib:/usr/lib/llvm-18/lib"
ENV OPENCL_VENDOR_PATH=${POCL_PREFIX}/etc/OpenCL/vendors

WORKDIR /workspace
CMD ["/bin/bash"]
