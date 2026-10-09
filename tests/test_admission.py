"""Synthetic occupancy fixtures; none is hardware-validation evidence."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from hcu_trainflow.admission import assess_occupancy
from hcu_trainflow.core import FlowError


NOW = "2026-10-09T12:00:30+00:00"
PROOF = "a" * 64


@pytest.fixture
def contract():
    return {"schema_version": 1, "context": "fixture-context",
            "devices": [{"node": "node-a", "device": "0", "identity": "pci:0000:01:00.0",
                         "idle_memory_bytes": 128, "memory_tolerance_bytes": 32,
                         "max_utilization_pct": 0, "basis": "Synthetic known-idle fixture only"}],
            "max_age_seconds": 30, "min_observations": 2, "quiet_period_seconds": 10,
            "max_sample_gap_seconds": 15, "shared_resources": []}


@pytest.fixture
def samples():
    device = {"node": "node-a", "device": "0", "identity": "pci:0000:01:00.0",
              "memory_used_bytes": 144, "utilization_pct": 0, "pids": [], "reservations": [],
              "coverage": {"device": True, "processes": True, "reservations": True},
              "evidence": [PROOF]}
    return [{"context": "fixture-context", "observed_at": stamp, "devices": [deepcopy(device)]}
            for stamp in ("2026-10-09T12:00:15+00:00", "2026-10-09T12:00:25+00:00")]


def test_fresh_quiet_samples_are_only_observed_idle_not_reservation(contract, samples):
    result = assess_occupancy(contract, samples, now=NOW)
    assert result["status"] == "observed-idle"
    assert result["reservation_acquired"] is False
    assert result["requires_immediate_recheck"] is True
    assert result["evidence"] == [PROOF]
    assert "pass" not in result.values()


@pytest.mark.parametrize("update,reason", [({"pids": [123]}, "process-present"),
                                          ({"pids": [{"pid": 123, "owner": None}]}, "process-present"),
                                          ({"memory_used_bytes": 161}, "memory-above-idle-envelope"),
                                          ({"utilization_pct": 1}, "device-active"),
                                          ({"reservations": ["someone else's job"]}, "reserved-by-site")])
def test_any_occupied_sample_denies_even_if_latest_is_idle(contract, samples, update, reason):
    samples[0]["devices"][0].update(update)
    result = assess_occupancy(contract, samples, now=NOW)
    assert result["status"] == "busy"
    assert reason in result["devices"][0]["reasons"]


@pytest.mark.parametrize("update,reason", [({"pids": None}, "pids-unknown"),
                                          ({"reservations": None}, "reservations-unknown"),
                                          ({"coverage": {"device": True}}, "processes-coverage-unknown"),
                                          ({"coverage": {"device": True, "processes": 1, "reservations": True}}, "processes-coverage-unknown"),
                                          ({"memory_used_bytes": None}, "memory-unknown"),
                                          ({"memory_used_bytes": -1}, "memory-unknown"),
                                          ({"utilization_pct": float("nan")}, "utilization-unknown"),
                                          ({"utilization_pct": True}, "utilization-unknown"),
                                          ({"identity": "different GPU"}, "device-identity-mismatch"),
                                          ({"evidence": []}, "raw-evidence-missing")])
def test_missing_or_ambiguous_evidence_never_means_empty(contract, samples, update, reason):
    samples[1]["devices"][0].update(update)
    result = assess_occupancy(contract, samples, now=NOW)
    assert result["status"] == "incomplete"
    assert reason in result["devices"][0]["reasons"]


@pytest.mark.parametrize("change,reason", [("stale", "stale-observation"), ("future", "observation-from-future"),
                                           ("duplicate", "duplicate-observation-time"), ("gap", "observation-gap-too-large"),
                                           ("short", "quiet-window-too-short"), ("order", "observations-out-of-order"),
                                           ("context", "context-mismatch"), ("missing", "device-not-observed")])
def test_observation_scope_and_time_checks(contract, samples, change, reason):
    if change == "stale": samples[0]["observed_at"] = "2026-10-09T11:59:59+00:00"
    if change == "future": samples[1]["observed_at"] = "2026-10-09T12:00:31+00:00"
    if change == "duplicate": samples[1]["observed_at"] = samples[0]["observed_at"]
    if change == "gap": contract["max_sample_gap_seconds"] = 5
    if change == "short": samples[0]["observed_at"] = "2026-10-09T12:00:20+00:00"
    if change == "order": samples.reverse()
    if change == "context": samples[1]["context"] = "other-context"
    if change == "missing": samples[1]["devices"] = []
    result = assess_occupancy(contract, samples, now=NOW)
    assert result["status"] == "incomplete"
    assert reason in result["devices"][0]["reasons"]


def test_no_samples_and_single_sample_deny(contract, samples):
    for chosen in ([], samples[:1]):
        result = assess_occupancy(contract, chosen, now=NOW)
        assert result["status"] == "incomplete"
        assert "insufficient-observations" in result["devices"][0]["reasons"]


def test_shared_nic_activity_has_independent_coverage(contract, samples):
    contract["shared_resources"] = ["node-a/nic"]
    result = assess_occupancy(contract, samples, now=NOW)
    assert result["status"] == "incomplete"
    for sample in samples:
        sample["shared_resources"] = [{"id": "node-a/nic", "active": False,
                                      "coverage_complete": True, "evidence": [PROOF]}]
    assert assess_occupancy(contract, samples, now=NOW)["status"] == "observed-idle"
    samples[0]["shared_resources"][0]["active"] = True
    assert assess_occupancy(contract, samples, now=NOW)["status"] == "busy"


def test_unrequested_busy_device_is_not_reserved_or_selected(contract, samples):
    for sample in samples:
        sample["devices"].append({"node": "node-b", "device": "1", "pids": [999]})
    result = assess_occupancy(contract, samples, now=NOW)
    assert result["status"] == "observed-idle"
    assert len(result["devices"]) == 1


@pytest.mark.parametrize("change", ["no-basis", "no-identity", "bool-memory", "huge-utilization", "one-sample",
                                  "duplicate-device", "duplicate-shared", "impossible-window"])
def test_invalid_contract_rejected(contract, samples, change):
    if change == "no-basis": contract["devices"][0].pop("basis")
    if change == "no-identity": contract["devices"][0].pop("identity")
    if change == "bool-memory": contract["devices"][0]["idle_memory_bytes"] = True
    if change == "huge-utilization": contract["devices"][0]["max_utilization_pct"] = 101
    if change == "one-sample": contract["min_observations"] = 1
    if change == "duplicate-device": contract["devices"] *= 2
    if change == "duplicate-shared": contract["shared_resources"] = ["nic", "nic"]
    if change == "impossible-window": contract["quiet_period_seconds"] = 40
    with pytest.raises(FlowError):
        assess_occupancy(contract, samples, now=NOW)


def test_duplicate_device_or_naive_timestamp_cannot_count_as_coverage(contract, samples):
    duplicate = deepcopy(samples)
    duplicate[0]["devices"] *= 2
    with pytest.raises(FlowError, match="Duplicate device"):
        assess_occupancy(contract, duplicate, now=NOW)
    samples[0]["observed_at"] = "2026-10-09T12:00:15"
    with pytest.raises(FlowError, match="timezone-aware"):
        assess_occupancy(contract, samples, now=NOW)


@pytest.fixture
def collector():
    spec = importlib.util.spec_from_file_location("occupancy_collector_fixture", Path(__file__).resolve().parents[1] / "scripts/collect_node_occupancy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def host_fixture(tmp_path, monkeypatch, collector):
    sysfs, proc, dev = (tmp_path / x for x in ("sysfs", "proc", "dev"))
    (proc / "1/fd").mkdir(parents=True)
    (dev / "dri").mkdir(parents=True)
    (dev / "kfd").write_text("")
    device = sysfs / "card0/device"
    (device / "drm/card0").mkdir(parents=True)
    (device / "drm/renderD128").mkdir()
    for field, value in {"vendor": "0x1d94", "device": "0x1234", "gpu_busy_percent": "0",
                         "mem_info_vram_used": "144", "mem_info_vram_total": "1024"}.items():
        (device / field).write_text(value)
    (dev / "dri/card0").write_text("")
    (dev / "dri/renderD128").write_text("")
    original_resolve = Path.resolve
    monkeypatch.setattr(Path, "resolve", lambda self, *a, **kw: tmp_path / "0000:01:00.0"
                        if self == device else original_resolve(self, *a, **kw))
    monkeypatch.setattr(collector, "_host_scope", lambda root, confirmed: {"complete": confirmed,
                        "confirmed_host_namespace": confirmed, "effective_uid": 0, "container_indicators": []})
    ids = {str(dev / "kfd"): 1, str(dev / "dri/card0"): 2, str(dev / "dri/renderD128"): 3}

    def char_id(path):
        path = Path(path)
        if str(path) in ids:
            return ids[str(path)]
        if path.parent.name == "fd":
            return int(path.read_text())
        return None

    monkeypatch.setattr(collector, "_char_id", char_id)
    return {"sysfs_root": sysfs, "proc_root": proc, "dev_root": dev, "host_scope_confirmed": True}


def reservation_record():
    return {"schema_version": 1, "context": "fixture", "node": "fixture-node",
            "observed_at": datetime.now(timezone.utc).isoformat(), "coverage_complete": True,
            "basis": "Synthetic explicit reservation view", "evidence": [PROOF], "devices": {"card0": []}}


def test_collector_retains_exact_raw_bytes_and_never_invents_reservations(collector, host_fixture):
    result = collector.collect_occupancy("fixture", "fixture-node", **host_fixture)
    row = result["devices"][0]
    assert row["device"] == "card0" and row["identity"] == "pci:0000:01:00.0"
    assert row["memory_used_bytes"] == 144
    assert row["pids"] == []
    assert row["coverage"] == {"device": True, "processes": True, "reservations": False}
    assert row["reservations"] is None
    raw = result["raw_evidence"]
    assert hashlib.sha256(raw["utf8"].encode("utf-8")).hexdigest() == raw["sha256"]
    assert row["evidence"] == [raw["sha256"]]
    assert json.loads(raw["utf8"])["process_scan"]["complete"] is True


def test_collector_requires_host_scope_and_fresh_explicit_booking(collector, host_fixture):
    result = collector.collect_occupancy("fixture", "fixture-node", reservations=reservation_record(), **host_fixture)
    assert all(result["devices"][0]["coverage"].values())
    host_fixture["host_scope_confirmed"] = False
    assert collector.collect_occupancy("fixture", "fixture-node", **host_fixture)["devices"][0]["coverage"]["processes"] is False
    booking = reservation_record()
    booking["observed_at"] = "2000-01-01T00:00:00+00:00"
    assert collector.collect_occupancy("fixture", "fixture-node", reservations=booking, **host_fixture)["devices"][0]["coverage"]["reservations"] is False


def test_collector_kfd_holder_is_busy_even_zero_utilization(collector, host_fixture):
    process = host_fixture["proc_root"] / "234"
    (process / "fd").mkdir(parents=True)
    (process / "fd/9").write_text("1")
    (process / "status").write_text("Name:\tpython\nUid:\t1000\t1000\t1000\t1000\n")
    (process / "comm").write_text("python")
    result = collector.collect_occupancy("fixture", "fixture-node", **host_fixture)
    row = result["devices"][0]
    assert row["utilization_pct"] == 0
    assert row["pids"][0]["pid"] == 234 and row["pids"][0]["uid"] == 1000
    assert row["coverage"]["processes"] is True


def test_collector_unreadable_fd_or_unknown_owner_makes_coverage_incomplete(collector, host_fixture, monkeypatch):
    process = host_fixture["proc_root"] / "234"
    (process / "fd").mkdir(parents=True)
    (process / "fd/9").write_text("1")
    # Missing status/comm: retain PID but do not claim resolved ownership.
    result = collector.collect_occupancy("fixture", "fixture-node", **host_fixture)
    assert result["devices"][0]["pids"][0]["pid"] == 234
    assert result["devices"][0]["coverage"]["processes"] is False
    original = collector._char_id

    def denied(path):
        if Path(path).parent.name == "fd":
            raise PermissionError("fixture")
        return original(path)

    monkeypatch.setattr(collector, "_char_id", denied)
    assert collector.collect_occupancy("fixture", "fixture-node", **host_fixture)["devices"][0]["coverage"]["processes"] is False


def test_collector_missing_counter_never_becomes_zero(collector, host_fixture):
    (host_fixture["sysfs_root"] / "card0/device/gpu_busy_percent").unlink()
    row = collector.collect_occupancy("fixture", "fixture-node", **host_fixture)["devices"][0]
    assert row["utilization_pct"] is None and row["coverage"]["device"] is False


def test_empty_process_view_cannot_prove_no_owners(collector, tmp_path):
    tmp_path.mkdir(exist_ok=True)
    result = collector._scan_processes(tmp_path, [])
    assert result["complete"] is False and "empty-proc-view" in result["errors"]


def test_busy_counter_without_identified_owner_is_incomplete(collector, host_fixture):
    (host_fixture["sysfs_root"] / "card0/device/gpu_busy_percent").write_text("100")
    result = collector.collect_occupancy("fixture", "fixture-node", **host_fixture)
    row = result["devices"][0]
    assert row["utilization_pct"] == 100 and row["memory_used_bytes"] == 144
    assert row["pids"] == []
    assert row["coverage"]["device"] is True
    assert row["coverage"]["processes"] is False
    raw = json.loads(result["raw_evidence"]["utf8"])
    assert raw["process_scan"]["unattributed_active_devices"] == ["card0"]
    assert hashlib.sha256(result["raw_evidence"]["utf8"].encode()).hexdigest() == result["raw_evidence"]["sha256"]


def test_fd_character_identity_survives_different_mount_inodes(collector, tmp_path, monkeypatch):
    # Real Docker device nodes can have different st_dev/st_ino from the host
    # nodes. Matching those would miss owners even while the GPU is occupied.
    import stat
    from types import SimpleNamespace
    proc = tmp_path / "proc"
    device = tmp_path / "dev/kfd"
    device.parent.mkdir()
    device.touch()
    process = proc / "234"
    (process / "fd").mkdir(parents=True)
    fd = process / "fd/3"
    fd.touch()
    (process / "status").write_text("Uid:\t1000\t1000\t1000\t1000\n")
    (process / "comm").write_text("python")
    original_stat = Path.stat

    def metadata(path, *args, **kwargs):
        if path in (device, fd):
            return SimpleNamespace(st_mode=stat.S_IFCHR | 0o600, st_rdev=60160,
                                   st_dev=5 if path == device else 49,
                                   st_ino=5106 if path == device else 1235)
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", metadata)
    result = collector._scan_processes(proc, [device])
    assert result["complete"] is True
    assert result["holders"] == [{"pid": 234, "uid": 1000, "comm": "python", "handles": [str(device)]}]
