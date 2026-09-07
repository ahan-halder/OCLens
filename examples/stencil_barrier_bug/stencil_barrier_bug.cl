/* Intentional bug: '-' instead of '+'. */
/* gid=5: private_value=12, left=10, expected=22. */

__kernel void stencil_barrier_bug(__global const int *in,
                                  __global int *out,
                                  int n)
{
    __local int scratch[8];

    int gid = get_global_id(0);
    int lid = get_local_id(0);

    int private_value = in[gid] + in[(gid + 1) % n];

    scratch[lid] = private_value;
    barrier(CLK_LOCAL_MEM_FENCE);

    int left = 0;
    if (lid > 0) {
        left = scratch[lid - 1];
    }

    int result = private_value - left;  // BUG: should be '+'

    if (gid == 0) {
        result = private_value;
    }

    out[gid] = result;
}
