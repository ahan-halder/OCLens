#include <CL/cl.h>
#include <stdio.h>
#include <stdlib.h>

#include "../common/load_source.h"

static void check(cl_int err, const char *msg)
{
    if (err != CL_SUCCESS) {
        fprintf(stderr, "%s failed: %d\n", msg, err);
        exit(1);
    }
}

int main(int argc, char **argv)
{
    (void)argc;
    cl_int err;
    cl_platform_id platform;
    cl_device_id device;
    check(clGetPlatformIDs(1, &platform, NULL), "clGetPlatformIDs");
    check(clGetDeviceIDs(platform, CL_DEVICE_TYPE_CPU, 1, &device, NULL), "clGetDeviceIDs");

    cl_context context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
    check(err, "clCreateContext");
    cl_command_queue queue = clCreateCommandQueue(context, device, 0, &err);
    check(err, "clCreateCommandQueue");

    char *source = oclens_load_source(argv[0], "stencil_barrier_bug.cl",
                                      "examples/stencil_barrier_bug/stencil_barrier_bug.cl");
    if (!source) {
        fprintf(stderr, "could not open stencil_barrier_bug.cl\n");
        return 1;
    }

    cl_program program = clCreateProgramWithSource(context, 1, (const char **)&source, NULL, &err);
    check(err, "clCreateProgramWithSource");
    check(clBuildProgram(program, 1, &device, "-cl-std=CL3.0", NULL, NULL), "clBuildProgram");

    cl_kernel kernel = clCreateKernel(program, "stencil_barrier_bug", &err);
    check(err, "clCreateKernel");

    const size_t n = 16;
    const size_t local = 8;

    int *in = calloc(n, sizeof(int));
    int *out = calloc(n, sizeof(int));
    int *ref = calloc(n, sizeof(int));
    for (size_t i = 0; i < n; ++i) {
        in[i] = (int)(i + 1);
    }
    /* Correct kernel: result = private_value + left (gid 0 keeps private_value). */
    for (size_t i = 0; i < n; ++i) {
        int gid = (int)i;
        int lid = (int)(i % local);
        int private_value = in[i] + in[(i + 1) % n];
        int left = 0;
        if (lid > 0) {
            size_t prev = i - 1;
            left = in[prev] + in[(prev + 1) % n];
        }
        int result = private_value + left;
        if (gid == 0) {
            result = private_value;
        }
        ref[i] = result;
    }

    cl_mem d_in = clCreateBuffer(context, CL_MEM_READ_ONLY, n * sizeof(int), NULL, &err);
    check(err, "d_in");
    cl_mem d_out = clCreateBuffer(context, CL_MEM_WRITE_ONLY, n * sizeof(int), NULL, &err);
    check(err, "d_out");

    check(clEnqueueWriteBuffer(queue, d_in, CL_TRUE, 0, n * sizeof(int), in, 0, NULL, NULL), "write in");

    check(clSetKernelArg(kernel, 0, sizeof(cl_mem), &d_in), "arg in");
    check(clSetKernelArg(kernel, 1, sizeof(cl_mem), &d_out), "arg out");
    int n_arg = (int)n;
    check(clSetKernelArg(kernel, 2, sizeof(int), &n_arg), "arg n");

    size_t global[3] = {n, 1, 1};
    size_t local_size[3] = {local, 1, 1};
    check(clEnqueueNDRangeKernel(queue, kernel, 1, NULL, global, local_size, 0, NULL, NULL),
          "enqueue");

    check(clEnqueueReadBuffer(queue, d_out, CL_TRUE, 0, n * sizeof(int), out, 0, NULL, NULL),
          "read out");

    int failures = 0;
    for (size_t i = 0; i < n; ++i) {
        if (out[i] != ref[i]) {
            printf("Mismatch at gid=%zu: expected=%d actual=%d\n", i, ref[i], out[i]);
            failures++;
        }
    }
    printf("Kernel result: %s\n", failures ? "FAIL (intentional demo bug)" : "PASS");
    free(in);
    free(out);
    free(ref);
    free(source);
    return failures ? 1 : 0;
}
