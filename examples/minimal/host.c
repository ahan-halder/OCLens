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

    const char *source = NULL;
    FILE *fp = fopen("minimal.cl", "r");
    if (!fp) {
        fp = fopen("examples/minimal/minimal.cl", "r");
    }
    if (!fp) {
        fprintf(stderr, "could not open minimal.cl\n");
        return 1;
    }
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    char *buf = malloc((size_t)size + 1);
    fread(buf, 1, (size_t)size, fp);
    buf[size] = '\0';
    fclose(fp);
    source = buf;

    cl_program program = clCreateProgramWithSource(context, 1, &source, NULL, &err);
    check(err, "clCreateProgramWithSource");
    check(clBuildProgram(program, 1, &device, "-cl-std=CL3.0", NULL, NULL), "clBuildProgram");

    cl_kernel kernel = clCreateKernel(program, "vector_add", &err);
    check(err, "clCreateKernel");

    const size_t n = 4;
    cl_mem a = clCreateBuffer(context, CL_MEM_READ_ONLY, n * sizeof(float), NULL, &err);
    check(err, "clCreateBuffer(a)");
    cl_mem b = clCreateBuffer(context, CL_MEM_READ_ONLY, n * sizeof(float), NULL, &err);
    check(err, "clCreateBuffer(b)");
    cl_mem c = clCreateBuffer(context, CL_MEM_WRITE_ONLY, n * sizeof(float), NULL, &err);
    check(err, "clCreateBuffer(c)");

    float ha[4] = {1, 2, 3, 4};
    float hb[4] = {10, 20, 30, 40};
    check(clEnqueueWriteBuffer(queue, a, CL_TRUE, 0, n * sizeof(float), ha, 0, NULL, NULL),
          "write a");
    check(clEnqueueWriteBuffer(queue, b, CL_TRUE, 0, n * sizeof(float), hb, 0, NULL, NULL),
          "write b");

    check(clSetKernelArg(kernel, 0, sizeof(cl_mem), &a), "set arg 0");
    check(clSetKernelArg(kernel, 1, sizeof(cl_mem), &b), "set arg 1");
    check(clSetKernelArg(kernel, 2, sizeof(cl_mem), &c), "set arg 2");

    size_t global = n;
    check(clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &global, &global, 0, NULL, NULL),
          "enqueue");

    float hc[4] = {0};
    check(clEnqueueReadBuffer(queue, c, CL_TRUE, 0, n * sizeof(float), hc, 0, NULL, NULL),
          "read c");

    int ok = 1;
    for (size_t i = 0; i < n; ++i) {
        if (hc[i] != ha[i] + hb[i]) {
            ok = 0;
            break;
        }
    }
    printf("minimal kernel: %s\n", ok ? "PASS" : "FAIL");
    free(buf);
    return ok ? 0 : 1;
}
