__kernel void vector_add_bug(__global const int *a,
                             __global const int *b,
                             __global int *c)
{
    int gid = get_global_id(0);
    int sum = a[gid] + b[gid];
    /* Intentional bug: off-by-one write confuses work-item 3 onward. */
    if (gid > 0) {
        sum -= 1;
    }
    c[gid] = sum;
}
