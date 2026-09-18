"""Tests for oclens verify helpers."""

from pathlib import Path

from oclens.verify import (
    run_verify,
    verify_demo_binary_present,
    verify_demo_host_output,
)


def test_verify_demo_binary_missing(tmp_path: Path) -> None:
    step = verify_demo_binary_present(tmp_path)
    assert not step.ok
    assert "missing" in step.detail.lower() or "cmake" in step.detail.lower()


def test_verify_host_output_accepts_intentional_bug(
    tmp_path: Path, monkeypatch
) -> None:
    exe = tmp_path / "build/examples/stencil_barrier_bug/stencil_barrier_bug"
    exe.parent.mkdir(parents=True)
    exe.write_text(
        "#!/bin/sh\necho 'Mismatch at gid=5: expected=24 actual=2'\necho 'Kernel result: FAIL (intentional demo bug)'\nexit 1\n",
        encoding="utf-8",
    )
    exe.chmod(0o755)

    def fake_run(cmd, **kwargs):
        return type(
            "P",
            (),
            {
                "returncode": 1,
                "stdout": (
                    "Mismatch at gid=5: expected=24 actual=2\n"
                    "Kernel result: FAIL (intentional demo bug)\n"
                ),
                "stderr": "",
            },
        )()

    monkeypatch.setattr("oclens.verify.subprocess.run", fake_run)
    step = verify_demo_host_output(tmp_path)
    assert step.ok


def test_run_verify_custom_steps_all_pass() -> None:
    report, code = run_verify(
        steps=[
            lambda: type("S", (), {"name": "a", "ok": True, "detail": ""})(),
            lambda: type("S", (), {"name": "b", "ok": True, "detail": "fine"})(),
        ]
    )
    assert code == 0
    assert "All checks passed" in report


def test_run_verify_custom_steps_fail() -> None:
    report, code = run_verify(
        steps=[lambda: type("S", (), {"name": "x", "ok": False, "detail": "nope"})()]
    )
    assert code == 1
    assert "[FAIL] x" in report
