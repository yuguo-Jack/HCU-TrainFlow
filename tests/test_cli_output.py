import json
import os
from pathlib import Path
import subprocess
import sys
import gzip
import hashlib

from hcu_trainflow.core import fingerprint


def test_json_output_remains_utf8_under_ascii_console(tmp_path):
    workspace = tmp_path / "训练记录"
    result = subprocess.run(
        [sys.executable, "-B", "-m", "hcu_trainflow", "--workspace", str(workspace), "init"],
        cwd=Path(__file__).parents[1], capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "ascii"},
    )
    assert result.returncode == 0, result.stderr.decode("utf8")
    assert "训练记录" in result.stdout.decode("utf8")
    assert isinstance(json.loads(result.stdout), dict)


def test_compressed_trace_cli_keeps_original_attribution_hash(tmp_path):
    trace = {'rank': 0, 'traceEvents': [{'ph': 'X', 'cat': 'kernel', 'name': 'probe',
             'ts': 1, 'dur': 3, 'pid': 0, 'tid': 1, 'args': {'stream': 1}}]}
    window = {'start_us': 0, 'end_us': 10}
    source = tmp_path / 'trace.json.gz'
    source.write_bytes(gzip.compress(json.dumps(trace).encode()))
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    mapping = {'schema_version': 1, 'source': {'sha256': digest, 'content_hash': fingerprint(trace)},
               'window': window, 'window_hash': fingerprint(window), 'rank': 0,
               'event_count': 1, 'counts': {'unlinked': 1}, 'events': [
                   {'event_index': 0, 'event_hash': fingerprint(trace['traceEvents'][0]),
                    'status': 'unlinked', 'shape': None, 'cpu_op': None, 'phase': 'unknown', 'callsite': []}]}
    window_path, mapping_path = tmp_path / 'window.json', tmp_path / 'attribution.json'
    window_path.write_text(json.dumps(window))
    mapping_path.write_text(json.dumps(mapping))
    command = [sys.executable, '-B', '-m', 'hcu_trainflow', '--workspace', str(tmp_path / 'store'),
               'profile-analyze', str(source), str(window_path), '--attribution', str(mapping_path)]
    result = subprocess.run(command, capture_output=True, cwd=Path(__file__).parents[1])
    # Analysis succeeds but correctly remains incomplete without workload/rank
    # qualification; CLI2 is not a gzip decoding error.
    assert result.returncode == 2, result.stderr.decode('utf8')
    assert json.loads(result.stdout)['status'] == 'incomplete'
    assert json.loads(result.stdout)['ranks']['0']['busy_union_us'] == 3
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    # Equal decoded JSON in different compressed bytes must not impersonate the
    # retained input artifact, even if its semantic content hash is identical.
    source.write_bytes(gzip.compress(json.dumps(trace, indent=2).encode()))
    result = subprocess.run(command, capture_output=True, cwd=Path(__file__).parents[1])
    assert result.returncode != 0
    assert 'Attribution source bytes differ' in (result.stdout + result.stderr).decode('utf8')
