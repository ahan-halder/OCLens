"""Tests for locating PoCL-cached copies of kernel sources."""

from pathlib import Path

from oclens_gdb.source_mapper import SourceMapper, find_cached_copy


KERNEL = "__kernel void vector_add(__global float *c) { c[0] = 1; }\n"


def test_find_cached_copy_by_content(tmp_path: Path) -> None:
    original = tmp_path / "user" / "vector_add.cl"
    original.parent.mkdir()
    original.write_text(KERNEL, encoding="utf-8")

    cache = tmp_path / "pocl-cache" / "AB"
    cache.mkdir(parents=True)
    cached = cache / "tempfile-aa-bb.cl"
    cached.write_text(KERNEL, encoding="utf-8")
    (cache / "other.cl").write_text("__kernel void other() {}\n", encoding="utf-8")

    match = find_cached_copy(original, roots=[tmp_path / "pocl-cache"])
    assert match == cached.resolve()


def test_mapper_bind_and_break_location(tmp_path: Path) -> None:
    original = tmp_path / "k.cl"
    original.write_text(KERNEL, encoding="utf-8")
    runtime = tmp_path / "tempfile.cl"
    runtime.write_text(KERNEL, encoding="utf-8")

    mapper = SourceMapper(original)
    assert mapper.gdb_break_location(7) == f"{original.resolve()}:7"
    mapper.bind_runtime(runtime)
    assert mapper.is_bound()
    assert mapper.gdb_break_location(7) == f"{runtime.resolve()}:7"


def test_bind_from_cache(tmp_path: Path) -> None:
    original = tmp_path / "k.cl"
    original.write_text(KERNEL, encoding="utf-8")
    cache = tmp_path / "cache"
    cache.mkdir()
    runtime = cache / "program.cl"
    runtime.write_text(KERNEL, encoding="utf-8")

    mapper = SourceMapper(original)
    assert mapper.bind_from_cache(roots=[cache]) == runtime.resolve()
    assert mapper.runtime == runtime.resolve()
