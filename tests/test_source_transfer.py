"""Source transfer integrity and batching; synthetic local filesystem tests."""
import contextlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

import pytest

from hcu_trainflow import core, execution
from hcu_trainflow.core import FlowError, Store, digest, fingerprint, write_json
from hcu_trainflow.execution import bundle, materialize, receive, snapshot


def source(tmp_path, count=4):
    root = tmp_path / "source"
    root.mkdir()
    for i in range(count):
        (root / f"code{i}.py").write_bytes(f"# source {i}\n".encode())
    return root


def count_connections(monkeypatch, store):
    count = []
    original = store.db
    @contextlib.contextmanager
    def tracked():
        count.append(True)
        with original() as connection:
            yield connection
    monkeypatch.setattr(store, "db", tracked)
    return count


def manifest(files):
    return {"schema_version": 1, "files": {name: {"sha256": digest(data), "size": len(data), "executable": False}
                                          for name, data in files.items()}}


def archive(tmp_path, body, files, *, raw_record=None):
    path = tmp_path / "transfer.zip"
    record = {"snapshot_id": fingerprint(body), "manifest": body}
    with zipfile.ZipFile(path, "w") as output:
        output.writestr("manifest.json", raw_record if raw_record is not None else json.dumps(record))
        for name, data in files.items():
            output.writestr("files/" + name, data)
    return path


def test_batch_put_one_transaction_and_private_visibility(monkeypatch, tmp_path):
    store = Store(tmp_path / "state")
    existing = store.put(b"private")
    connections = count_connections(monkeypatch, store)
    hashes = store.put_many((data for data in [b"private", b"public", b"private"]), "public")
    assert len(connections) == 1 and hashes == [existing, digest(b"public"), existing]
    with store.db() as db:
        rows = {row["id"]: row["visibility"] for row in db.execute("SELECT * FROM artifacts")}
    assert rows == {existing: "private", digest(b"public"): "public"}
    store.put_many([b"public"], "private")
    with store.db() as db:
        assert db.execute("SELECT visibility FROM artifacts WHERE id=?", (digest(b"public"),)).fetchone()[0] == "private"


def test_batch_stream_failure_does_not_register_partial_transaction(tmp_path):
    store = Store(tmp_path / "state")
    def broken():
        yield b"first"
        raise OSError("synthetic interrupted input")
    with pytest.raises(OSError):
        store.put_many(broken())
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM artifacts").fetchone()[0] == 0
    # An orphan is immutable/reusable, not a registered successful transfer.
    assert store.put_many([b"first", b"second"]) == [digest(b"first"), digest(b"second")]


def test_batch_rechecks_corrupt_existing_objects(tmp_path):
    store = Store(tmp_path / "state")
    sha = store.put(b"known")
    (store.root / "objects" / sha[:2] / sha).write_bytes(b"tampered")
    with pytest.raises(FlowError, match="Corrupted existing"):
        store.put_many([b"new", b"known"])
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM artifacts").fetchone()[0] == 1


def test_roundtrip_uses_constant_database_connections(monkeypatch, tmp_path):
    local = Store(tmp_path / "local")
    root = source(tmp_path, 75)
    calls = count_connections(monkeypatch, local)
    snap = snapshot(local, root, [f"code{i}.py" for i in range(75)])
    assert len(calls) == 1
    output = tmp_path / "source.zip"
    calls.clear()
    bundle(local, snap["snapshot_id"], output)
    assert len(calls) == 1 and not output.with_name(output.name + ".partial").exists()
    remote = Store(tmp_path / "remote")
    calls = count_connections(monkeypatch, remote)
    result = receive(remote, output, tmp_path / "received")
    assert len(calls) == 2  # One registration transaction, one streamed read.
    assert result["verified"]
    for name, info in snap["files"].items():
        assert digest((tmp_path / "received" / name).read_bytes()) == info["sha256"]


@pytest.mark.parametrize("name", ["../escaped", "a/../b", "a//b", "./b", "/absolute", "C:/absolute", "a\\b",
                                  "trainflow-snapshot.json", "trainflow-snapshot.json/child"])
def test_invalid_names_rejected_before_registration(tmp_path, name):
    files = {name: b"bad"}
    store = Store(tmp_path / "state")
    with pytest.raises(FlowError):
        receive(store, archive(tmp_path, manifest(files), files), tmp_path / "out")
    assert not (tmp_path / "out").exists() and not (tmp_path / "out.partial").exists()
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM artifacts").fetchone()[0] == 0


def test_parent_file_collision_rejected(tmp_path):
    files = {"a": b"first", "a/b": b"second"}
    with pytest.raises(FlowError, match="parent directory"):
        receive(Store(tmp_path / "state"), archive(tmp_path, manifest(files), files), tmp_path / "out")


@pytest.mark.skipif(os.name != "nt", reason="Windows path semantics")
def test_windows_case_collision_rejected(tmp_path):
    files = {"file.py": b"first", "FILE.py": b"second"}
    with pytest.raises(FlowError, match="collide"):
        receive(Store(tmp_path / "state"), archive(tmp_path, manifest(files), files), tmp_path / "out")


@pytest.mark.parametrize("field,value", [("size", -1), ("size", True), ("sha256", "../bad"), ("executable", 1)])
def test_invalid_manifest_metadata_rejected(tmp_path, field, value):
    files = {"a.py": b"test"}
    body = manifest(files)
    body["files"]["a.py"][field] = value
    with pytest.raises(FlowError):
        receive(Store(tmp_path / "state"), archive(tmp_path, body, files), tmp_path / "out")


def test_tampered_late_file_does_not_register_earlier_files(tmp_path):
    files = {"a": b"correct", "b": b"expected"}
    path = archive(tmp_path, manifest(files), {**files, "b": b"tampered"})
    store = Store(tmp_path / "state")
    with pytest.raises(FlowError, match="hash/size mismatch"):
        receive(store, path, tmp_path / "out")
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM artifacts").fetchone()[0] == 0
    assert not list((store.root / "snapshots").glob("*.json"))


def test_duplicate_zip_member_rejected(tmp_path):
    files = {"a": b"first"}
    path = archive(tmp_path, manifest(files), files)
    with zipfile.ZipFile(path, "a") as output, pytest.warns(UserWarning):
        output.writestr("files/a", b"first")
    with pytest.raises(FlowError, match="Duplicate archive"):
        receive(Store(tmp_path / "state"), path, tmp_path / "out")


def test_duplicate_json_key_rejected(tmp_path):
    files = {"a": b"first"}
    body = manifest(files)
    record = json.dumps({"snapshot_id": fingerprint(body), "manifest": body})
    record = record.replace('"files": {', '"files": {}, "files": {')
    with pytest.raises(FlowError, match="Duplicate manifest"):
        receive(Store(tmp_path / "state"), archive(tmp_path, body, files, raw_record=record), tmp_path / "out")


def test_unexpected_archive_member_rejected(tmp_path):
    files = {"a": b"first"}
    with pytest.raises(FlowError, match="file set"):
        receive(Store(tmp_path / "state"), archive(tmp_path, manifest(files), {**files, "b": b"extra"}), tmp_path / "out")


def test_zip_symlink_metadata_rejected(tmp_path):
    files = {"link": b"target"}
    body = manifest(files)
    path = tmp_path / "symlink.zip"
    with zipfile.ZipFile(path, "w") as output:
        output.writestr("manifest.json", json.dumps({"snapshot_id": fingerprint(body), "manifest": body}))
        info = zipfile.ZipInfo("files/link")
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        output.writestr(info, b"target")
    with pytest.raises(FlowError, match="member type"):
        receive(Store(tmp_path / "state"), path, tmp_path / "out")


def test_partial_materialization_never_publishes_destination(monkeypatch, tmp_path):
    store = Store(tmp_path / "state")
    root = source(tmp_path)
    snap = snapshot(store, root, [f"code{i}.py" for i in range(4)])
    original = execution.atomic_write
    calls = []
    def interrupted(path, content):
        calls.append(path)
        if len(calls) == 2:
            raise OSError("synthetic filesystem interruption")
        original(path, content)
    monkeypatch.setattr(execution, "atomic_write", interrupted)
    with pytest.raises(OSError):
        materialize(store, snap["snapshot_id"], tmp_path / "out")
    assert not (tmp_path / "out").exists() and (tmp_path / "out.partial").exists()
    with pytest.raises(FlowError, match="unfinished transfer"):
        materialize(store, snap["snapshot_id"], tmp_path / "out")


def test_partial_bundle_never_publishes_final_archive(monkeypatch, tmp_path):
    store = Store(tmp_path / "state")
    root = source(tmp_path)
    snap = snapshot(store, root, ["code0.py", "code1.py"])
    original = store.iter_artifacts
    def interrupted(hashes):
        for index, item in enumerate(original(hashes)):
            if index:
                raise OSError("synthetic object read interruption")
            yield item
    monkeypatch.setattr(store, "iter_artifacts", interrupted)
    with pytest.raises(OSError):
        bundle(store, snap["snapshot_id"], tmp_path / "out.zip")
    assert not (tmp_path / "out.zip").exists() and (tmp_path / "out.zip.partial").exists()
    with pytest.raises(FlowError, match="unfinished transfer"):
        bundle(store, snap["snapshot_id"], tmp_path / "out.zip")


def test_existing_destination_refused_before_object_import(tmp_path):
    files = {"a": b"first"}
    path = archive(tmp_path, manifest(files), files)
    destination = tmp_path / "out"
    destination.mkdir()
    store = Store(tmp_path / "state")
    with pytest.raises(FlowError, match="destination must be new"):
        receive(store, path, destination)
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM artifacts").fetchone()[0] == 0


def test_windows_git_executable_mode_overrides_stat(tmp_path):
    script = tmp_path / "launch.sh"
    script.write_text("#!/bin/sh\n")
    script.chmod(0o600)
    metadata = execution._executable_metadata(script, "launch.sh", {"launch.sh": "100755"}, windows=True)
    assert metadata == {"executable": True, "executable_source": "git-index"}
    executable_suffix = tmp_path / "tool.exe"
    executable_suffix.write_bytes(b"synthetic")
    assert execution._executable_metadata(executable_suffix, "tool.exe", {}, windows=True)["executable"] is False


def test_git_index_modes_roundtrip_and_overlap_selection(tmp_path):
    root = source(tmp_path, 1)
    script = root / "launch.sh"
    script.write_bytes(b"#!/bin/sh\necho synthetic\n")
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "add", "launch.sh"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "update-index", "--chmod=+x", "launch.sh"], check=True, capture_output=True)
    assert execution._git_modes(root)["launch.sh"] == "100755"
    if os.name != "nt":
        script.chmod(0o755)
    store = Store(tmp_path / "state")
    snap = snapshot(store, root, ["launch.sh", "launch.sh"])
    assert len(snap["files"]) == 1 and snap["files"]["launch.sh"]["executable"]


def test_git_symlink_placeholder_refused_on_windows(tmp_path):
    path = tmp_path / "link"
    path.write_text("../target")
    with pytest.raises(FlowError, match="Git symlink"):
        execution._executable_metadata(path, "link", {"link": "120000"}, windows=True)


@pytest.mark.parametrize("selection", [["vendor"], ["vendor/child/alias.sh"]])
def test_nested_checkout_placeholder_uses_child_index(tmp_path, selection):
    root = source(tmp_path, 1)
    child = root / "vendor/child"
    child.mkdir(parents=True)
    for repo in (root, child):
        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    (child / "run.sh").write_bytes(b"#!/bin/sh\necho nested\n")
    (child / "alias.sh").write_bytes(b"run.sh")
    subprocess.run(["git", "-C", str(child), "add", "run.sh"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(child), "update-index", "--chmod=+x", "run.sh"], check=True, capture_output=True)
    blob = subprocess.run(["git", "-C", str(child), "hash-object", "-w", "--stdin"],
                          input=b"run.sh", check=True, capture_output=True).stdout.decode().strip()
    subprocess.run(["git", "-C", str(child), "update-index", "--add", "--cacheinfo",
                    "120000," + blob + ",alias.sh"], check=True, capture_output=True)
    if os.name != "nt":
        (child / "run.sh").chmod(0o755)
    store = Store(tmp_path / "state")
    snap = snapshot(store, root, selection)
    alias = snap["files"]["vendor/child/alias.sh"]
    assert store.artifact(alias["sha256"]) == (child / "run.sh").read_bytes()
    assert alias["executable"] is True
    assert snap["resolved_links"]["vendor/child/alias.sh"]["resolved_source"] == "vendor/child/run.sh"
    assert not any(".git" in name.split("/") for name in snap["files"])


def test_selected_broken_nested_git_metadata_fails_closed(tmp_path):
    root = source(tmp_path, 1)
    child = root / "nested"
    child.mkdir()
    (child / ".git").write_text("gitdir: missing-index-repository\n")
    (child / "alias").write_text("target")
    with pytest.raises(FlowError, match="Cannot read Git source modes"):
        snapshot(Store(tmp_path / "state"), root, ["nested/alias"])


def test_dangling_child_git_cannot_fall_back_to_parent_index(tmp_path):
    root = source(tmp_path, 1)
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
    child = root / "nested"
    child.mkdir()
    (child / "alias").write_bytes(b"target")
    try:
        (child / ".git").symlink_to("missing-git-metadata", target_is_directory=True)
    except OSError:
        pytest.skip("OS symlink privilege unavailable")
    store = Store(tmp_path / "state")
    with pytest.raises(FlowError, match="dangling Git source metadata"):
        snapshot(store, root, ["nested/alias"])
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM artifacts").fetchone()[0] == 0


@pytest.mark.skipif(os.name != "nt", reason="Case-insensitive Windows selection")
def test_windows_selection_requires_exact_git_path_spelling(tmp_path):
    root = source(tmp_path, 1)
    child = root / "vendor/core"
    child.mkdir(parents=True)
    for repo in (root, child):
        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    (child / "run.sh").write_bytes(b"#!/bin/sh\necho nested\n")
    subprocess.run(["git", "-C", str(child), "add", "run.sh"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(child), "update-index", "--chmod=+x", "run.sh"], check=True, capture_output=True)
    with pytest.raises(FlowError, match="exact filesystem spelling"):
        snapshot(Store(tmp_path / "state"), root, ["VENDOR/CORE/RUN.SH"])


def test_materialize_checks_manifest_size_even_with_valid_object(tmp_path):
    store = Store(tmp_path / "state")
    sha = store.put(b"test")
    body = {"schema_version": 1, "files": {"a": {"sha256": sha, "size": 5, "executable": False}}}
    sid = fingerprint(body)
    write_json(store.root / "snapshots" / (sid + ".json"), body)
    with pytest.raises(FlowError, match="size mismatch"):
        materialize(store, sid, tmp_path / "out")


def placeholders(monkeypatch, modes):
    """Model Windows core.symlinks=false without requiring OS symlink privileges."""
    monkeypatch.setattr(execution, "_git_modes", lambda repo: modes)


def test_git_file_placeholder_is_dereferenced_with_evidence(monkeypatch, tmp_path):
    root = source(tmp_path, 1)
    (root / "alias.py").write_bytes(b"code0.py")
    placeholders(monkeypatch, {"alias.py": "120000", "code0.py": "100755"})
    store = Store(tmp_path / "state")
    snap = snapshot(store, root, ["alias.py"])
    assert snap["files"]["alias.py"]["source_path"] == "code0.py"
    assert store.artifact(snap["files"]["alias.py"]["sha256"]) == (root / "code0.py").read_bytes()
    assert snap["resolved_links"]["alias.py"] == {
        "target": "code0.py", "target_sha256": digest(b"code0.py"), "resolved_source": "code0.py",
        "kind": "file", "representation": "git-index-placeholder"}
    path = tmp_path / "source.zip"
    bundle(store, snap["snapshot_id"], path)
    receive(Store(tmp_path / "remote"), path, tmp_path / "out")
    assert (tmp_path / "out/alias.py").read_bytes() == (root / "code0.py").read_bytes()
    assert not (tmp_path / "out/alias.py").is_symlink()


def test_git_directory_placeholder_keeps_all_target_content(monkeypatch, tmp_path):
    root = source(tmp_path, 1)
    (root / ".agents").mkdir()
    (root / ".agents/skills").write_bytes(b"../skills")
    (root / "skills/topic").mkdir(parents=True)
    (root / "skills/topic/SKILL.md").write_bytes(b"synthetic content")
    placeholders(monkeypatch, {".agents/skills": "120000"})
    store = Store(tmp_path / "state")
    snap = snapshot(store, root, [".agents", "skills"])
    alias = snap["files"][".agents/skills/topic/SKILL.md"]
    actual = snap["files"]["skills/topic/SKILL.md"]
    assert alias["sha256"] == actual["sha256"] and alias["source_path"] == "skills/topic/SKILL.md"
    assert snap["resolved_links"][".agents/skills"]["kind"] == "directory"


def test_nested_link_chain_is_recorded(monkeypatch, tmp_path):
    root = source(tmp_path, 1)
    (root / "first").write_bytes(b"second")
    (root / "second").write_bytes(b"code0.py")
    placeholders(monkeypatch, {"first": "120000", "second": "120000"})
    snap = snapshot(Store(tmp_path / "state"), root, ["first"])
    assert set(snap["resolved_links"]) == {"first", "second"}
    assert snap["files"]["first"]["source_path"] == "code0.py"


@pytest.mark.parametrize("target", ["../outside", "/etc/passwd", "C:/outside", "missing", "bad\nlink", ".env"])
def test_source_links_reject_escape_absolute_missing_or_private(monkeypatch, tmp_path, target):
    root = source(tmp_path, 1)
    (root / "alias").write_text(target)
    (root / ".env").write_bytes(b"synthetic private bytes")
    placeholders(monkeypatch, {"alias": "120000"})
    store = Store(tmp_path / "state")
    with pytest.raises(FlowError):
        snapshot(store, root, ["alias"])
    with store.db() as db:
        assert db.execute("SELECT count(*) FROM artifacts").fetchone()[0] == 0


def test_source_link_chain_cycle_rejected(monkeypatch, tmp_path):
    root = source(tmp_path, 1)
    (root / "a").write_text("b")
    (root / "b").write_text("a")
    placeholders(monkeypatch, {"a": "120000", "b": "120000"})
    with pytest.raises(FlowError, match="link cycle"):
        snapshot(Store(tmp_path / "state"), root, ["a"])


def test_directory_link_cycle_rejected(monkeypatch, tmp_path):
    root = source(tmp_path, 1)
    (root / "nested").mkdir()
    (root / "nested/back").write_text("..")
    placeholders(monkeypatch, {"nested/back": "120000"})
    with pytest.raises(FlowError, match="directory link cycle"):
        snapshot(Store(tmp_path / "state"), root, ["nested"])


def test_link_dotdot_resolves_after_symlink_not_before(monkeypatch, tmp_path):
    root = source(tmp_path, 1)
    (root / "deep/inner").mkdir(parents=True)
    (root / "deep/actual.py").write_bytes(b"correct resolved sibling")
    (root / "actual.py").write_bytes(b"wrong lexically normalized sibling")
    (root / "dirlink").write_text("deep/inner")
    (root / "alias").write_text("dirlink/../actual.py")
    placeholders(monkeypatch, {"dirlink": "120000", "alias": "120000"})
    store = Store(tmp_path / "state")
    snap = snapshot(store, root, ["alias"])
    assert store.artifact(snap["files"]["alias"]["sha256"]) == b"correct resolved sibling"


def test_symlink_evidence_tampering_rejected(tmp_path):
    files = {"a": b"first"}
    body = manifest(files)
    body["resolved_links"] = {"link": {"target": "a", "target_sha256": digest(b"other"), "resolved_source": "a",
                                        "kind": "file", "representation": "git-index-placeholder"}}
    with pytest.raises(FlowError, match="link evidence"):
        receive(Store(tmp_path / "state"), archive(tmp_path, body, files), tmp_path / "out")


def test_physical_relative_symlink_is_dereferenced(tmp_path):
    root = source(tmp_path, 1)
    try:
        (root / "alias.py").symlink_to("code0.py")
    except OSError:
        pytest.skip("OS symlink privilege unavailable; Git-placeholder tests still execute")
    store = Store(tmp_path / "state")
    snap = snapshot(store, root, ["alias.py"])
    assert snap["resolved_links"]["alias.py"]["representation"] == "filesystem-symlink"
    assert store.artifact(snap["files"]["alias.py"]["sha256"]) == (root / "code0.py").read_bytes()
