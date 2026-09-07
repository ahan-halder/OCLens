/*
 * Demo kernel for OCLens: two work-groups, local memory, a barrier, divergence,
 * and an intentional bug at line 23 (`-` instead of `+`).
 *
 * For gid=5 with in[4]=5, in[5]=6: private_value=12, left=10, correct result=22.
 */
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
