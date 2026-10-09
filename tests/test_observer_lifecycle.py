"""Context handoff regression; synthetic local logs, no remote/GPU execution."""
import importlib.util
import json
from pathlib import Path

import pytest

from hcu_trainflow.core import FlowError, Store, write_json
from hcu_trainflow.training_logs import observe_once


def manager():
    path = Path(__file__).parents[1] / "scripts/manage_training_observer.py"
    spec = importlib.util.spec_from_file_location("observer_context_manager", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def manifest(tmp_path, context, attempt):
    log = tmp_path / (attempt + ".log"); log.write_text("")
    value = {"schema_version": 1, "context": context, "attempt_id": attempt, "log_path": str(log),
             "log_start_offset": 0, "start_step": 0, "expected_final_step": 3, "started_at": 100,
             "log_timezone": "UTC", "process": {"pid": 99999999, "start_ticks": "1", "boot_id": "synthetic", "pid_namespace": "synthetic"}}
    path = tmp_path / (attempt + ".json"); write_json(path, value); return path


def setup(tmp_path):
    store = Store(tmp_path / "controller")
    store.create({"schema_version": 1, "task_id": "fixture", "mode": "operate", "objective": "synthetic context handoff",
                  "context": {"source": "a"}, "permissions": ["execute"]})
    policy = tmp_path / "policy.json"
    write_json(policy, {"startup_timeout_seconds": 300, "stall_seconds": 60, "telemetry_seconds": 120,
                        "recovery_seconds": 180, "min_progress_samples": 2})
    return store, policy


def test_both_old_scope_guards_remain_then_fresh_store_succeeds(tmp_path):
    store, policy = setup(tmp_path)
    old = manifest(tmp_path, store.task("fixture")["context"], "old")
    state = store.root / "training-logs/fixture"
    observe_once(store.root, "fixture", old, policy, state)
    with store.db() as db: old_watch = db.execute("SELECT value FROM meta WHERE key='watch:fixture'").fetchone()[0]
    store.change_context("fixture", {"source": "b"})
    new = manifest(tmp_path, store.task("fixture")["context"], "new")
    with pytest.raises(FlowError, match="Observer context changed"):
        observe_once(store.root, "fixture", new, policy, state)
    with pytest.raises(FlowError, match="Watcher context changed"):
        observe_once(store.root, "fixture", new, policy, store.root / "training-logs/fixture-new")
    scope = manager().prepare_context_workspace(store.root, "fixture", tmp_path / "observer-contexts")
    result = observe_once(scope["workspace"], "fixture", new, policy, scope["state_dir"])
    assert result["monitor"]["completion_verified"] is False
    assert Store(scope["workspace"]).task("fixture")["spec"]["permissions"] == []
    with store.db() as db: assert db.execute("SELECT value FROM meta WHERE key='watch:fixture'").fetchone()[0] == old_watch
    assert (state / "training-log.sqlite3").is_file()


def test_context_A_B_A_gets_distinct_epoch_stores(tmp_path):
    store, _ = setup(tmp_path); tool = manager(); root = tmp_path / "observer-contexts"
    first = tool.prepare_context_workspace(store.root, "fixture", root)
    assert tool.prepare_context_workspace(store.root, "fixture", root) == first
    store.change_context("fixture", {"source": "b"})
    second = tool.prepare_context_workspace(store.root, "fixture", root)
    store.change_context("fixture", {"source": "a"})
    third = tool.prepare_context_workspace(store.root, "fixture", root)
    assert first["context"] == third["context"]
    assert len({first["workspace"], second["workspace"], third["workspace"]}) == 3
    assert len({first["event_peer_suffix"], second["event_peer_suffix"], third["event_peer_suffix"]}) == 3


def test_unknown_existing_store_not_overwritten(tmp_path):
    store, _ = setup(tmp_path); tool = manager(); root = tmp_path / "contexts"
    destination = root / "fixture" / (store.task("fixture")["context"] + "-e0")
    destination.mkdir(parents=True); (destination / "keep").write_text("unknown previous state")
    with pytest.raises(FlowError, match="lacks context-scope proof"):
        tool.prepare_context_workspace(store.root, "fixture", root)
    assert (destination / "keep").read_text() == "unknown previous state"


def test_prepared_observer_store_cannot_be_mutated_into_other_scope(tmp_path):
    store, _ = setup(tmp_path); tool = manager(); root = tmp_path / "contexts"
    scope = tool.prepare_context_workspace(store.root, "fixture", root)
    Store(scope["workspace"]).change_context("fixture", {"source": "foreign"})
    with pytest.raises(FlowError, match="was changed"):
        tool.prepare_context_workspace(store.root, "fixture", root)


def test_event_peers_distinguish_tasks_and_destination_stores(tmp_path):
    store, _ = setup(tmp_path); tool = manager()
    one = tool.prepare_context_workspace(store.root, "fixture", tmp_path / "contexts")
    other_root = tool.prepare_context_workspace(store.root, "fixture", tmp_path / "other-contexts")
    spec = store.task("fixture")["spec"]
    store.create({**spec, "task_id": "another-task"})
    other_task = tool.prepare_context_workspace(store.root, "another-task", tmp_path / "contexts")
    assert one["context"] == other_task["context"] == other_root["context"]
    assert len({r["event_peer_suffix"] for r in [one, other_root, other_task]}) == 3
    assert all(len(r["event_peer_suffix"]) == 64 for r in [one, other_root, other_task])


def test_exact_legacy_scope_marker_upgrades_without_resetting_store(tmp_path):
    store, _ = setup(tmp_path); tool = manager(); root = tmp_path / "contexts"
    scope = tool.prepare_context_workspace(store.root, "fixture", root)
    observation = Store(scope["workspace"])
    with observation.db() as db: db.execute("INSERT INTO meta VALUES('synthetic-history','retain')")
    marker = Path(scope["workspace"]) / "observer-scope.json"
    value = json.loads(marker.read_text()); value.pop("observer_workspace"); write_json(marker, value)
    assert tool.prepare_context_workspace(store.root, "fixture", root) == scope
    with observation.db() as db:
        assert db.execute("SELECT value FROM meta WHERE key='synthetic-history'").fetchone()[0] == 'retain'
    assert json.loads(marker.read_text())["observer_workspace"] == scope["workspace"]
