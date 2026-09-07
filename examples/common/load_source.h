#ifndef OCLENS_LOAD_SOURCE_H
#define OCLENS_LOAD_SOURCE_H

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *oclens_join(const char *dir, const char *name)
{
    size_t n = strlen(dir) + 1 + strlen(name) + 1;
    char *out = malloc(n);
    if (!out) {
        return NULL;
    }
    snprintf(out, n, "%s/%s", dir, name);
    return out;
}

static char *oclens_dirname(const char *path)
{
    const char *slash = strrchr(path, '/');
    if (!slash) {
        char *dot = malloc(2);
        if (dot) {
            strcpy(dot, ".");
        }
        return dot;
    }
    size_t n = (size_t)(slash - path);
    if (n == 0) {
        n = 1;
    }
    char *dir = malloc(n + 1);
    if (!dir) {
        return NULL;
    }
    memcpy(dir, path, n);
    dir[n] = '\0';
    return dir;
}

/* Load kernel text. Tries cwd, argv0 directory, then a source-tree fallback. */
static char *oclens_load_source(const char *argv0, const char *filename, const char *tree_rel)
{
    const char *candidates[4];
    char *exe_dir = argv0 ? oclens_dirname(argv0) : NULL;
    char *next_to_exe = (exe_dir && filename) ? oclens_join(exe_dir, filename) : NULL;
    int n = 0;
    if (filename) {
        candidates[n++] = filename;
    }
    if (next_to_exe) {
        candidates[n++] = next_to_exe;
    }
    if (tree_rel) {
        candidates[n++] = tree_rel;
    }

    char *buf = NULL;
    for (int i = 0; i < n; ++i) {
        FILE *fp = fopen(candidates[i], "r");
        if (!fp) {
            continue;
        }
        if (fseek(fp, 0, SEEK_END) != 0) {
            fclose(fp);
            continue;
        }
        long size = ftell(fp);
        if (size < 0) {
            fclose(fp);
            continue;
        }
        rewind(fp);
        buf = malloc((size_t)size + 1);
        if (!buf) {
            fclose(fp);
            break;
        }
        size_t got = fread(buf, 1, (size_t)size, fp);
        buf[got] = '\0';
        fclose(fp);
        break;
    }

    free(exe_dir);
    free(next_to_exe);
    return buf;
}

#endif
