cmake_minimum_required(VERSION 3.20)

add_executable(vector_add_bug host.c)
target_link_libraries(vector_add_bug PRIVATE OpenCL::OpenCL)
target_compile_definitions(vector_add_bug PRIVATE CL_TARGET_OPENCL_VERSION=300)

add_custom_command(
    TARGET vector_add_bug POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_CURRENT_SOURCE_DIR}/vector_add_bug.cl
        $<TARGET_FILE_DIR:vector_add_bug>/vector_add_bug.cl
)
