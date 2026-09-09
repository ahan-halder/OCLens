function(oclens_add_example target kernel_cl)
    add_executable(${target} host.c)
    target_link_libraries(${target} PRIVATE OpenCL::OpenCL)
    target_compile_definitions(${target} PRIVATE CL_TARGET_OPENCL_VERSION=300)
    add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${kernel_cl}
        COMMAND ${CMAKE_COMMAND} -E copy
            ${CMAKE_CURRENT_SOURCE_DIR}/${kernel_cl}
            ${CMAKE_CURRENT_BINARY_DIR}/${kernel_cl}
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${kernel_cl}
        VERBATIM
    )
    add_custom_target(${target}_kernel ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${kernel_cl})
    add_dependencies(${target} ${target}_kernel)
endfunction()

add_subdirectory(minimal)
add_subdirectory(vector_add_bug)
add_subdirectory(stencil_barrier_bug)
