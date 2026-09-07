cmake_minimum_required(VERSION 3.20)

add_executable(stencil_barrier_bug host.c)
target_link_libraries(stencil_barrier_bug PRIVATE OpenCL::OpenCL)
target_compile_definitions(stencil_barrier_bug PRIVATE CL_TARGET_OPENCL_VERSION=300)

add_custom_command(
    TARGET stencil_barrier_bug POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_CURRENT_SOURCE_DIR}/stencil_barrier_bug.cl
        $<TARGET_FILE_DIR:stencil_barrier_bug>/stencil_barrier_bug.cl
)
