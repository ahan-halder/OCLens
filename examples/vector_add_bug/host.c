#include <CL/cl.h>
#include <stdio.h>
#include <stdlib.h>

static void check(cl_int err, const char *msg)
{
    if (err != CL_SUCCESS) {
        fprintf(stderr, "%s failed: %d\n", msg, err);
        exit(1);
    }
}

int main(void)
{
    cl_int err;
    cl_platform_id platform;
    cl_device_id device;
    check(clGetPlatformIDs(1, &platform, NULL), "clGetPlatformIDs");
    check(clGetDeviceIDs(platform, CL_DEVICE_TYPE_CPU, 1, &device, NULL), "clGetDeviceIDs");

    cl_context context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
    check(err, "clCreateContext");
    cl_command_queue queue = clCreateCommandQueue(context, device, 0, &err);
    check(err, "clCreateCommandQueue");

    FILE *fp = fopen("vector_add_bug.cl", "r");
    if (!fp) {
        fp = fopen("examples/vector_add_bug/vector_add_bug.cl", "r");
    }
    if (!fp) {
        fprintf(stderr, "could not open vector_add_bug.cl\n");
        return 1;
    }
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    char *source = malloc((size_t)size + 1);
    fread(source, 1, (size_t)size, fp);
    source[size] = '\0';
    fclose(fp);

    cl_program program = clCreateProgramWithSource(context, 1, (const char **)&source, NULL, &err);
    check(err, "clCreateProgramWithSource");
    check(clBuildProgram(program, 1, &device, "-cl-std=CL3.0", NULL, NULL), "clBuildProgram");

    cl_kernel kernel = clCreateKernel(program, "vector_add_bug", &err);
    check(err, "clCreateKernel");

    const size_t n = 8;
    cl_mem a = clCreateBuffer(context, CL_MEM_READ_ONLY, n * sizeof(int), NULL, &err);
    check(err, "buffer a");
    cl_mem b = clCreateBuffer(context, CL_MEM_READ_ONLY, n * sizeof(int), NULL, &err);
    check(err, "buffer b");
    cl_mem c = clCreateBuffer(context, CL_MEM_WRITE_ONLY, n * sizeof(int), NULL, &err);
    check(err, "buffer c");

    int ha[8], hb[8], hc[8];
    for (size_t i = 0; i < n; ++i) {
        ha[i] = (int)i;
        hb[i] = (int)(i * 10);
    }

    check(clEnqueueWriteBuffer(queue, a, CL_TRUE, 0, n * sizeof(int), ha, 0, NULL, NULL), "write a");
    check(clEnqueueWriteBuffer(queue, b, CL_TRUE, 0, n * sizeof(int), hb, 0, NULL, NULL), "write b");

    check(clSetKernelArg(kernel, 0, sizeof(cl_mem), &a), "arg 0");
    check(clSetKernelArg(kernel, 1, sizeof(cl_mem), &b), "arg 1");
    check(clSetKernelArg(kernel, 2, sizeof(cl_mem), &c), "arg 2");

    size_t global = n;
    check(clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &global, &global, 0, NULL, NULL), "enqueue");
    check(clEnqueueReadBuffer(queue, c, CL_TRUE, 0, n * sizeof(int), hc, 0, NULL, NULL), "read c");

    int failures = 0;
    for (size_t i = 0; i < n; ++i) {
        int expected = ha[i] + hb[i];
        if (hc[i] != expected) {
            printf("Mismatch at gid=%zu: expected=%d actual=%d\n", i, expected, hc[i]);
            failures++;
        }
    }
    printf("Kernel result: %s\n", failures ? "FAIL (intentional demo bug)" : "PASS");
    free(source);
    return failures ? 1 : 0;
}
