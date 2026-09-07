cmake_minimum_required(VERSION 3.20)

add_executable(minimal_host host.c)
target_link_libraries(minimal_host PRIVATE OpenCL::OpenCL)
target_compile_definitions(minimal_host PRIVATE CL_TARGET_OPENCL_VERSION=300)

add_custom_command(
    TARGET minimal_host POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_CURRENT_SOURCE_DIR}/minimal.cl
        $<TARGET_FILE_DIR:minimal_host>/minimal.cl
)
