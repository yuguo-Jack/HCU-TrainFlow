"""Portable contract tests and Linux-only real IPC checks; no GPU evidence."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/probe_training_tempdir.py"
SPEC = importlib.util.spec_from_file_location("training_tempdir_probe", SCRIPT)
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)
LINUX = pytest.mark.skipif(sys.platform != "linux", reason="Real Linux AF_UNIX and spawn qualification requires Linux")


def directories(tmp_path):
    target = tmp_path / "ipc"
    target.mkdir()
    return tmp_path, target


def test_non_linux_reports_unsupported_without_writing(tmp_path, monkeypatch):
    root, target = directories(tmp_path)
    monkeypatch.setattr(PROBE.sys, "platform", "win32")
    result = PROBE.probe(root, target)
    assert result["status"] == "unsupported"
    assert result["linux_ipc_verified"] is False
    assert list(target.iterdir()) == []


@pytest.mark.parametrize("seconds", [0, -1, 301, True, float("nan"), float("inf")])
def test_invalid_timeout_rejected(tmp_path, seconds):
    root, target = directories(tmp_path)
    result = PROBE.probe(root, target, seconds)
    assert result["status"] == "failed"
    assert list(target.iterdir()) == []


def test_paths_must_exist_be_absolute_and_stay_under_root(tmp_path):
    root, target = directories(tmp_path)
    assert PROBE.validate_directory(root, target) == (root.resolve(), target.resolve())
    with pytest.raises(ValueError, match="absolute"):
        PROBE.validate_directory(root, Path("relative"))
    with pytest.raises(FileNotFoundError):
        PROBE.validate_directory(root, root / "missing")
    with pytest.raises(ValueError, match="strict descendant"):
        PROBE.validate_directory(root, root)
    with pytest.raises(ValueError, match="strict descendant"):
        PROBE.validate_directory(target, root)


def test_explicit_directory_write_failure_never_falls_back(tmp_path, monkeypatch):
    root, target = directories(tmp_path)
    calls = []
    monkeypatch.setattr(PROBE.sys, "platform", "linux")

    def no_write(*, prefix, dir):
        calls.append((prefix, dir))
        raise PermissionError("read-only fixture filesystem")

    monkeypatch.setattr(PROBE.tempfile, "mkdtemp", no_write)
    result = PROBE.probe(root, target)
    assert result["status"] == "failed"
    assert result["error"]["type"] == "PermissionError"
    assert calls == [("pymp-", str(target.resolve()))]
    assert not result["linux_ipc_verified"]
    assert "worker_pid" not in result
    assert list(target.iterdir()) == []


def test_worker_timeout_fails_and_cleans_only_own_directory(tmp_path, monkeypatch):
    root, target = directories(tmp_path)
    monkeypatch.setattr(PROBE.sys, "platform", "linux")
    calls = []

    class Process:
        pid = 98765
        returncode = None
        reads = 0

        def communicate(self, timeout):
            self.reads += 1
            if self.reads == 1:
                raise subprocess.TimeoutExpired("fixture worker", timeout)
            return b"", b"fixture timeout"

        def poll(self):
            return self.returncode

    process = Process()

    def popen(argv, **kwargs):
        assert kwargs['start_new_session'] is True
        assert kwargs['env']['TMPDIR'] == str(target.resolve())
        assert kwargs['env']['TEMP'] == str(target.resolve())
        assert kwargs['env']['TMP'] == str(target.resolve())
        assert argv[-2] == str(target.resolve())
        return process

    def stop_group(item):
        assert item is process
        calls.append(item.pid)
        item.returncode = -15
        return ['SIGTERM']

    monkeypatch.setattr(PROBE.subprocess, 'Popen', popen)
    monkeypatch.setattr(PROBE, '_stop_group', stop_group)
    result = PROBE.probe(root, target, 1)
    assert result['status'] == 'failed'
    assert result['linux_ipc_verified'] is False
    assert 'bounded timeout' in result['error']
    assert calls == [process.pid]
    assert result['cleanup']['complete']
    assert list(target.iterdir()) == []


def test_unconfirmed_process_termination_retains_probe_directory(tmp_path, monkeypatch):
    root, target = directories(tmp_path)
    monkeypatch.setattr(PROBE.sys, "platform", "linux")

    class StuckProcess:
        pid = 98765
        returncode = None

        def communicate(self, timeout):
            raise subprocess.TimeoutExpired("stuck fixture", timeout)

        def poll(self):
            return None

    monkeypatch.setattr(PROBE.subprocess, 'Popen', lambda *args, **kwargs: StuckProcess())
    monkeypatch.setattr(PROBE, '_stop_group', lambda process: {'worker_reaped': False})
    result = PROBE.probe(root, target, 1)
    assert result['status'] == 'failed'
    assert result['cleanup']['complete'] is False
    assert Path(result['probe_directory']).is_dir()
    assert result['linux_ipc_verified'] is False


def test_cleanup_refuses_unexpected_file_and_preserves_neighbor(tmp_path):
    root, target = directories(tmp_path)
    probe = target / "pymp-fixture"
    probe.mkdir()
    unexpected = probe / "valuable.txt"
    unexpected.write_text("preserve", encoding="utf8")
    neighbor = target / "neighbor.txt"
    neighbor.write_text("preserve", encoding="utf8")
    identity = (probe.stat().st_dev, probe.stat().st_ino)
    result = PROBE._cleanup(probe, identity)
    assert not result["complete"]
    assert unexpected.read_text(encoding="utf8") == "preserve"
    assert neighbor.read_text(encoding="utf8") == "preserve"


def test_cleanup_refuses_changed_identity(tmp_path):
    _, target = directories(tmp_path)
    probe = target / "pymp-fixture"
    probe.mkdir()
    result = PROBE._cleanup(probe, (probe.stat().st_dev, probe.stat().st_ino + 1))
    assert not result["complete"]
    assert probe.exists()


def test_cleanup_removes_only_exact_empty_directory(tmp_path):
    _, target = directories(tmp_path)
    probe = target / "pymp-fixture"
    probe.mkdir()
    sibling = target / "other"
    sibling.mkdir()
    result = PROBE._cleanup(probe, (probe.stat().st_dev, probe.stat().st_ino))
    assert result["complete"]
    assert not probe.exists()
    assert sibling.is_dir()


def test_socket_address_cannot_escape_or_use_another_transport(tmp_path):
    _, target = directories(tmp_path)
    with pytest.raises(RuntimeError, match="escaped"):
        PROBE._inside_socket(str(tmp_path / "elsewhere"), str(target))
    for address in [("127.0.0.1", 1234), "\0abstract"]:
        with pytest.raises(RuntimeError, match="filesystem"):
            PROBE._inside_socket(address, str(target))


def test_socket_length_counts_bytes_not_characters(tmp_path):
    _, target = directories(tmp_path)
    value = str(target / "listener-中文")
    record = PROBE._inside_socket(value, str(target))
    assert record["address_bytes"] == len(os.fsencode(value))
    assert record["address_bytes"] > len(value)


@LINUX
def test_actual_listener_spawn_manager_roundtrip_and_cleanup(tmp_path_factory):
    # Avoid pytest's long per-test-name directory in the success fixture.
    # Create a short explicit fixture; if a runner supplies an excessively long
    # base, skip success qualification rather than silently use system /tmp.
    root, target = directories(tmp_path_factory.mktemp("ipc"))
    if len(os.fsencode(str(target))) + 40 >= 108:
        pytest.skip("Use pytest --basetemp with a short explicit task path for Linux IPC success test")
    neighbor = target / "keep"
    neighbor.write_text("keep", encoding="utf8")
    result = PROBE.probe(root, target, 15)
    assert result["status"] == "passed", result
    assert result["linux_ipc_verified"]
    assert result["worker"]["listener"]["roundtrip"]
    assert result["worker"]["manager"]["queue_roundtrip"]
    assert result["worker"]["manager"]["start_method"] == "spawn"
    assert result["worker"]["manager"]["exit_code"] == 0
    assert not result["worker"]["manager"]["alive_after_shutdown"]
    assert result["worker"]["manager"]["used_tempdir"]["tempfile_tempdir"] == str(target)
    assert result["cleanup"]["complete"]
    assert list(target.iterdir()) == [neighbor]


@LINUX
def test_actual_too_long_path_fails_without_fallback(tmp_path):
    target = tmp_path / ("p" * 120)
    target.mkdir()
    result = PROBE.probe(tmp_path, target, 15)
    assert result["status"] == "failed"
    assert not result["linux_ipc_verified"]
    assert result["worker"]["phase"] == "listener"
    assert "AF_UNIX path too long" in result["worker"]["error"]["message"]
    assert result["worker"]["used_tempdir"]["tempfile_tempdir"] == str(target)
    assert result["cleanup"]["complete"]
    assert list(target.iterdir()) == []


@LINUX
def test_read_only_owner_mode_fails_even_as_root(tmp_path):
    root, target = directories(tmp_path)
    target.chmod(0o500)
    try:
        result = PROBE.probe(root, target)
        assert result["status"] == "failed"
        assert "owner write and search" in result["error"]["message"]
        assert "worker_pid" not in result
    finally:
        target.chmod(0o700)


@LINUX
def test_symlink_outside_root_is_rejected(tmp_path):
    root = tmp_path / "task"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (root / "ipc").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="strict descendant"):
        PROBE.validate_directory(root, root / "ipc")


def test_non_linux_cli_has_nonzero_exit(tmp_path):
    if sys.platform == "linux":
        pytest.skip("Unsupported platform CLI check")
    root, target = directories(tmp_path)
    result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--task-root", str(root), "--tempdir", str(target)],
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 3
    assert json.loads(result.stdout)["status"] == "unsupported"
