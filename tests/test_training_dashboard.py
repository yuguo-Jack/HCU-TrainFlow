"""Public fixtures are synthetic; real campaign logs stay in the private workspace."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

from hcu_trainflow.core import FlowError
from hcu_trainflow.training_dashboard import _snapshot, render_dashboard


def record(step=1, kind="iteration", **extra):
    value = {"context": "fixture-context", "attempt_id": "fixture-attempt",
             "process_identity": {"pid": 7, "start_ticks": "11", "boot_id": "fixture", "pid_namespace": "fixture"},
             "timestamp": 100 + step, "step": step, "observation_kind": kind,
             "source_record_kind": kind, "metrics": {"lm loss": 6.0 - step / 10, "elapsed time per iteration (ms)": 1250},
             "loss": 99.0, "step_seconds_reported": 99.0,
             "memory_by_rank": {}, "adapter_warnings": [], "fatal_errors": []}
    value.update(extra)
    return value


def write(tmp_path, rows):
    path = tmp_path / "normalized.jsonl"
    path.write_bytes(b"".join((json.dumps(r, allow_nan=False) + "\n").encode() for r in rows))
    return path


def result(tmp_path, rows, **kwargs):
    source = write(tmp_path, rows)
    rendered = render_dashboard(source, tmp_path / "dashboard", **kwargs)
    data = json.loads(Path(rendered["data"]).read_text(encoding="utf8"))
    return source, rendered, data


def test_only_fresh_iterations_and_source_hashes(tmp_path):
    source, rendered, data = result(tmp_path, [record(), record(kind="heartbeat", loss=-100), record(2)])
    values = data["charts"][0]["series"]["lm loss"]
    assert [r["value"] for r in values] == [5.9, 5.8]
    assert data["iterations"] == 2 and data["records"] == 3
    assert data["charts"][1]["series"]["reported duration"][0]["value"] == 1.25
    assert data["source"]["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert (tmp_path / "dashboard/normalized.snapshot.jsonl").read_bytes() == source.read_bytes()
    assert rendered["gate_decision"] == "none"
    for svg in (tmp_path / "dashboard").glob("*.svg"):
        assert ET.parse(svg).getroot().tag.endswith("svg")


@pytest.mark.parametrize("field,value", [("context", "other"), ("attempt_id", "other"),
                                           ("process_identity", {"pid": 8})])
def test_mixed_identity_rejected_by_default(tmp_path, field, value):
    with pytest.raises(FlowError, match="Mixed"):
        result(tmp_path, [record(), record(2, **{field: value})])
    assert not (tmp_path / "dashboard").exists()


def test_explicit_selection_accounts_for_excluded_attempts_and_contexts(tmp_path):
    rows = [record(1, attempt_id="old"), record(1), record(2, context="other-context"), record(2)]
    _, _, data = result(tmp_path, rows, attempt_id="fixture-attempt", context="fixture-context")
    assert data["iterations"] == 2 and data["snapshot_records"] == 4
    assert data["selection"]["excluded_records"] == 2
    assert len(data["selection"]["identities_in_snapshot"]) == 3


@pytest.mark.parametrize("kwargs", [{"attempt_id": "fixture-attempt"}, {"context": "fixture-context"},
                                      {"attempt_id": "absent", "context": "fixture-context"}])
def test_explicit_selection_requires_pair_and_match(tmp_path, kwargs):
    with pytest.raises(FlowError):
        result(tmp_path, [record()], **kwargs)


def test_missing_nonfinite_and_zero_are_distinct_and_svg_breaks(tmp_path):
    rows = [record(1, metrics={"lm loss": 0.0}), record(2, metrics={}),
            record(3, metrics={"lm loss": "nan"}), record(4, metrics={"lm loss": 1.0})]
    _, _, data = result(tmp_path, rows)
    points = data["charts"][0]["series"]["lm loss"]
    assert [p["value"] for p in points] == [0, None, None, 1]
    assert [p["reason"] for p in points] == [None, "missing", "nonfinite-or-nonnumeric", None]
    root = ET.parse(tmp_path / "dashboard/loss.svg").getroot()
    segments = root.findall(".//{http://www.w3.org/2000/svg}polyline")
    assert len(segments) == 2  # Does not bridge the missing/nonfinite gap.
    assert all(len(s.attrib["points"].split()) == 1 for s in segments)


def test_invalid_duration_does_not_reuse_state_duration(tmp_path):
    rows = [record(1), record(2, metrics={"elapsed time per iteration (ms)": 0}), record(3, metrics={})]
    _, _, data = result(tmp_path, rows)
    assert [p["value"] for p in data["charts"][1]["series"]["reported duration"]] == [1.25, None, None]


def test_memory_carried_rank_state_and_missing_fields(tmp_path):
    m0 = {"allocator_allocated_bytes": 0, "allocator_reserved_bytes": 1024**3, "observed_at": 101}
    m1 = {"allocator_allocated_bytes": 2 * 1024**3, "observed_at": 102}
    rows = [record(kind="memory", memory_by_rank={"0": m0}),
            record(kind="heartbeat", memory_by_rank={"0": m0}),
            record(kind="memory", memory_by_rank={"0": m0, "1": m1}),
            record(kind="memory", memory_by_rank={"0": {"allocator_allocated_bytes": 3 * 1024**3, "observed_at": 103}, "1": m1})]
    _, _, data = result(tmp_path, rows)
    series = data["charts"][2]["series"]
    assert [p["value"] for p in series["rank 0: allocator_allocated_bytes"]] == [0, 3]
    assert [p["value"] for p in series["rank 0: allocator_reserved_bytes"]] == [1, None]
    assert [p["value"] for p in series["rank 1: allocator_allocated_bytes"]] == [2]
    assert "device_memory_bytes" not in " ".join(series)


def test_no_inferred_throughput_but_explicit_existing_field_works(tmp_path):
    _, _, data = result(tmp_path, [record(metrics={"tokens per second": 42.5})],
                        throughput_metric="tokens per second", throughput_unit="tokens/s")
    assert data["charts"][3]["series"]["tokens per second"][0]["value"] == 42.5
    assert data["charts"][3]["unit"] == "tokens/s"


def test_single_rank_constant_memory_retains_fresh_observation_points(tmp_path):
    memory = {"0": {"allocator_allocated_bytes": 1024**3, "observed_at": 101}}
    _, _, data = result(tmp_path, [record(kind="memory", memory_by_rank=memory) for _ in range(3)])
    assert [p["value"] for p in data["charts"][2]["series"]["rank 0: allocator_allocated_bytes"]] == [1, 1, 1]


def test_unchanged_multi_rank_memory_does_not_invent_current_rank(tmp_path):
    memory = {"0": {"allocator_allocated_bytes": 1024**3}, "1": {"allocator_allocated_bytes": 2 * 1024**3}}
    _, _, data = result(tmp_path, [record(kind="heartbeat", memory_by_rank=memory), record(kind="memory", memory_by_rank=memory)])
    assert data["charts"][2]["series"] == {}
    assert data["ambiguous_memory_record_lines"] == [2]


def test_unknown_throughput_is_gap_not_derived_from_batch(tmp_path):
    _, _, data = result(tmp_path, [record(metrics={"global batch size": 10})],
                        throughput_metric="tokens per second", throughput_unit="tokens/s")
    assert data["charts"][3]["series"]["tokens per second"][0]["value"] is None


def test_partial_final_line_requires_opt_in_and_preserves_exact_bytes(tmp_path):
    source = write(tmp_path, [record()])
    original = source.read_bytes() + b'{"context":"in-progress'
    source.write_bytes(original)
    with pytest.raises(FlowError, match="Unterminated"):
        render_dashboard(source, tmp_path / "bad")
    render_dashboard(source, tmp_path / "ok", allow_partial_final_line=True)
    data = json.loads((tmp_path / "ok/dashboard.json").read_text())
    assert data["excluded_final_line"]["bytes"] == len(original) - data["parsed_bytes"]
    assert (tmp_path / "ok/normalized.snapshot.jsonl").read_bytes() == original


@pytest.mark.parametrize("bad", [b'{bad json}\n', b'\n', b'{"loss":NaN}\n', b'\xff\n', b'[]\n'])
def test_complete_bad_lines_never_silently_dropped(tmp_path, bad):
    source = write(tmp_path, [record()]); source.write_bytes(source.read_bytes() + bad)
    with pytest.raises(FlowError):
        render_dashboard(source, tmp_path / "out", allow_partial_final_line=True)


def test_raw_reference_hashes_verified_at_byte_offsets(tmp_path):
    raw = tmp_path / "raw.log"; raw.write_bytes(b"ignored\nactual sample\n")
    ref = {"path": "/remote/private/train.log", "offset": 8, "bytes": 14,
           "sha256": hashlib.sha256(b"actual sample\n").hexdigest()}
    source = write(tmp_path, [record(source=ref)])
    render_dashboard(source, tmp_path / "ok", raw_log=raw)
    data = json.loads((tmp_path / "ok/dashboard.json").read_text())
    assert data["raw_references_verified"]
    raw.write_bytes(b"ignored\nwrong content!\n")
    with pytest.raises(FlowError, match="hash mismatch"):
        render_dashboard(source, tmp_path / "wrong", raw_log=raw)


def test_no_html_or_svg_injection(tmp_path):
    attack = '</title><script>alert(1)</script><img src="https://evil.invalid">'
    _, _, data = result(tmp_path, [record(metrics={"lm loss " + attack: 1}, adapter_warnings=[attack], attempt_id=attack)], title=attack)
    for path in (tmp_path / "dashboard").glob("*.html"):
        page = path.read_text()
        assert '<script>' not in page and '<img src="https:' not in page
        assert '&lt;script&gt;' in page
    svg = (tmp_path / "dashboard/loss.svg").read_text()
    assert '<script>' not in svg
    ET.fromstring(svg)


@pytest.mark.parametrize("steps", [[1, 1], [2, 1]])
def test_duplicate_or_regressing_steps_rejected(tmp_path, steps):
    with pytest.raises(FlowError, match="Duplicate or regressing"):
        result(tmp_path, [record(s) for s in steps])


def test_snapshot_detects_concurrent_append_and_keeps_initial_prefix(tmp_path, monkeypatch):
    path = write(tmp_path, [record()]); initial = path.read_bytes()
    original = Path.open
    class GrowingReader:
        def __init__(self, stream): self.stream, self.calls = stream, 0
        def __enter__(self): return self
        def __exit__(self, *args): self.stream.close()
        def fileno(self): return self.stream.fileno()
        def seek(self, *args): return self.stream.seek(*args)
        def read(self, size):
            self.calls += 1
            data = self.stream.read(size)
            if self.calls == 1:
                with original(path, "ab") as writer: writer.write(b'{"unfinished')
            return data
    def opened(self, *args, **kwargs):
        stream = original(self, *args, **kwargs)
        return GrowingReader(stream) if self == path and args == ("rb",) else stream
    monkeypatch.setattr(Path, "open", opened)
    data, metadata = _snapshot(path)
    assert data == initial and metadata["appended_during_read"]
    assert metadata["sha256"] == hashlib.sha256(initial).hexdigest()


def test_output_cannot_overwrite_prior_evidence(tmp_path):
    source, _, _ = result(tmp_path, [record()])
    with pytest.raises(FlowError, match="new or empty"):
        render_dashboard(source, tmp_path / "dashboard")


@pytest.mark.parametrize("change", ["rewrite", "truncate"])
def test_concurrent_prefix_mutation_is_rejected(tmp_path, monkeypatch, change):
    path = write(tmp_path, [record()])
    original = Path.open
    class ChangingReader:
        def __init__(self, stream): self.stream, self.calls = stream, 0
        def __enter__(self): return self
        def __exit__(self, *args): self.stream.close()
        def fileno(self): return self.stream.fileno()
        def seek(self, *args): return self.stream.seek(*args)
        def read(self, size):
            self.calls += 1
            data = self.stream.read(size)
            if self.calls == 1:
                with original(path, "r+b") as writer:
                    if change == "truncate": writer.truncate(0)
                    else: writer.write(b"!")
            return data
    def opened(self, *args, **kwargs):
        stream = original(self, *args, **kwargs)
        return ChangingReader(stream) if self == path and args == ("rb",) else stream
    monkeypatch.setattr(Path, "open", opened)
    with pytest.raises(FlowError, match="captured prefix"):
        _snapshot(path)


def test_heartbeat_only_does_not_fabricate_training_metrics(tmp_path):
    _, _, data = result(tmp_path, [record(kind="heartbeat", completed=True)])
    assert data["iterations"] == 0
    assert data["gate_decision"] == "none"
    assert "No iteration observations" in data["gaps"]
    assert data["charts"][0]["series"] == {}


def test_script_entrypoint_without_optional_plot_dependencies(tmp_path):
    source = write(tmp_path, [record()])
    script = Path(__file__).resolve().parents[1] / "scripts/render_training_dashboard.py"
    run = subprocess.run([sys.executable, "-B", str(script), str(source), "--output-dir", str(tmp_path / "script-output"),
                          "--measurement-mode", "functional"], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)["gate_decision"] == "none"


@pytest.mark.parametrize("values", [
    [-1e308, 1e308],
    [-sys.float_info.max, sys.float_info.max],
    [sys.float_info.max, sys.float_info.max],
    [-sys.float_info.max, -sys.float_info.max],
    [1e308, 1.1e308],
    [-5e-324, 5e-324],
    [5e-324, 5e-324],
    [0.0, 0.0],
])
def test_extreme_finite_values_keep_finite_axes_and_original_values(tmp_path, values):
    _, _, data = result(tmp_path, [record(i + 1, metrics={"lm loss": value}) for i, value in enumerate(values)])
    assert [p["value"] for p in data["charts"][0]["series"]["lm loss"]] == values
    root = ET.parse(tmp_path / "dashboard/loss.svg").getroot()
    circles = root.findall(".//{http://www.w3.org/2000/svg}circle")
    assert len(circles) == len(values)
    for element in root.iter():
        for key in ("x", "y", "cx", "cy", "r"):
            if key in element.attrib:
                assert math.isfinite(float(element.attrib[key]))
        if "points" in element.attrib:
            assert all(math.isfinite(float(value)) for pair in element.attrib["points"].split() for value in pair.split(","))
        if element.tag.endswith("text"):
            try:
                number = float(element.text)
            except (TypeError, ValueError):
                continue
            assert math.isfinite(number), "Numeric tick label must remain finite"
    assert all(80 <= float(c.attrib["cx"]) <= 920 and 70 <= float(c.attrib["cy"]) <= 340 for c in circles)
    if any(values):
        assert "tick ×" in (tmp_path / "dashboard/loss.svg").read_text(encoding="utf8")
