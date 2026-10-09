"""Transport contract tests; all shell execution is local and uses no hardware."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

import pytest

from hcu_trainflow.core import FlowError
from hcu_trainflow.execution import command_plan


def card(**changes):
    return {"schema_version": 1, "backend": "ssh-docker", "ssh_target": "compute",
            "container": "train", "cwd": "/work/source", "argv": ["python", "train.py"],
            "basis": "Test-only transport fixture", **changes}


def command_payload(plan, *, backend, jump=False):
    ssh = plan["argv"]
    if jump:
        nested = shlex.split(ssh[-1])
        assert nested[0] == "exec"
        ssh = nested[1:]
        assert ssh[0] == "ssh"
    remote = shlex.split(ssh[-1])
    if backend == "ssh-docker":
        assert remote[:3] == ["docker", "exec", "train"]
        remote = remote[3:]
    elif backend == "ssh-slurm":
        assert remote[:3] == ["srun", "--jobid", "123"]
        remote = remote[3:]
    assert remote[:2] == ["bash", "-lc"]
    assert len(remote) == 3
    return remote[-1]


@pytest.mark.parametrize("backend", ["ssh", "ssh-docker", "ssh-slurm"])
def test_jump_exec_uses_second_clients_existing_identity(backend):
    plan = command_plan(card(backend=backend, allocation="123",
                             ssh_jump={"mode": "exec", "target": "jump"}))
    outer = plan["argv"]
    inner = shlex.split(outer[-1])[1:]
    assert outer[-2] == "jump" and inner[-2] == "compute"
    for invocation in (outer, inner):
        assert "BatchMode=yes" in invocation
        assert "ForwardAgent=no" in invocation
        assert "StrictHostKeyChecking=yes" in invocation
        assert "ConnectTimeout=15" in invocation
        assert "-J" not in invocation and "-A" not in invocation
    payload = command_payload(plan, backend=backend, jump=True)
    assert payload.startswith("cd -- /work/source && exec env -- python train.py")
    assert plan["cwd"] is None and plan["env"] == {}


@pytest.mark.parametrize("backend", ["ssh", "ssh-docker", "ssh-slurm"])
def test_complex_arguments_survive_all_shell_layers(backend):
    arguments = ["python", "odd 'file'.py", "", "a;b", "$(touch should-not-exist)",
                 "`touch should-not-exist`", 'one"two', "line\nbreak", "--option", "& exit 9"]
    plan = command_plan(card(backend=backend, allocation="123", argv=arguments,
                             cwd="/work/it's here", env={"VALUE": "'quoted'\n$HOME;hi"},
                             activation="/opt/it's dtk/env.sh",
                             ssh_jump={"mode": "exec", "target": "root@jump"}))
    payload = command_payload(plan, backend=backend, jump=True)
    words = shlex.split(payload)
    assert words[:7] == [".", "/opt/it's dtk/env.sh", "&&", "cd", "--", "/work/it's here", "&&"]
    assert words[7:] == ["exec", "env", "--", "VALUE='quoted'\n$HOME;hi", *arguments]


def local_bash():
    binary = shutil.which("bash")
    if binary:
        return binary
    git = shutil.which("git")
    if git:
        candidate = Path(git).resolve().parent.parent / "bin" / "bash.exe"
        if candidate.exists():
            return str(candidate)
    pytest.skip("Local Bash unavailable; shell-layer unit tests still run")


def bash_path(path):
    value = Path(path).as_posix()
    return "/" + value[0].lower() + value[2:] if os.name == "nt" else value


def test_decoded_remote_payload_really_executes_literal_arguments_and_activation(tmp_path):
    # Exercise a real shell, not only assertions mirroring shlex.join. Windows
    # Git Bash works too; no SSH/Docker command is actually executed here.
    directory = tmp_path / "owner's source"
    directory.mkdir()
    activation = tmp_path / "owner's activation.sh"
    activation.write_text("export ACTIVATED=yes\nexport OVERRIDE=from-script\ncd /\n", encoding="utf-8")
    odd = ["", "apostrophe'quote", 'double"quote', "one\ntwo", "$(touch BAD_SUBSTITUTION)",
           "`touch BAD_BACKTICK`", "; touch BAD_SEMICOLON", "& exit 19"]
    program = "import json,os,sys;print(json.dumps({'args':sys.argv[1:],'cwd':os.getcwd(),'activated':os.getenv('ACTIVATED'),'override':os.getenv('OVERRIDE')}))"
    plan = command_plan(card(cwd=bash_path(directory), activation=bash_path(activation),
                             argv=[bash_path(sys.executable), "-c", program, *odd],
                             env={"OVERRIDE": "card value '$HOME'"},
                             ssh_jump={"mode": "exec", "target": "jump"}))
    result = subprocess.run([local_bash(), "-c", command_payload(plan, backend="ssh-docker", jump=True)],
                            capture_output=True, text=True, timeout=15,
                            env={**os.environ, "MSYS2_ARG_CONV_EXCL": "*"})
    assert result.returncode == 0, result.stderr
    observed = json.loads(result.stdout)
    assert observed["args"] == odd
    assert Path(observed["cwd"]).resolve() == directory.resolve()
    assert observed["activated"] == "yes"
    assert observed["override"] == "card value '$HOME'"
    assert list(directory.iterdir()) == []


def test_complete_jump_docker_shell_chain_with_local_transport_stubs(tmp_path):
    # Run every generated shell layer. Only SSH and Docker transport executables
    # are replaced with local stubs; real Bash parsing and Python argv remain.
    executable = local_bash()
    tools = tmp_path / "stub tools"
    tools.mkdir()
    ssh_stub = tools / "ssh"
    ssh_stub.write_text("#!/bin/bash\nset -e\nwhile [[ $1 == -* ]]; do\n"
                        "case $1 in -o) shift 2;; -T) shift;; *) exit 90;; esac\ndone\n"
                        "printf '%s\\n' \"$1\" >> \"$TRANSPORT_LOG\"\nshift\n"
                        "[[ $# == 1 ]] || exit 91\nexec /bin/bash -c \"$1\"\n", encoding="utf-8")
    docker_stub = tools / "docker"
    docker_stub.write_text("#!/bin/bash\n[[ $1 == exec && $2 == train ]] || exit 92\n"
                           "shift 2\nexec \"$@\"\n", encoding="utf-8")
    ssh_stub.chmod(0o755)
    docker_stub.chmod(0o755)
    arguments = ["", "'quoted'", "$(touch BAD)", "`touch BAD`", "line\nbreak", "a;b"]
    plan = command_plan(card(cwd=bash_path(tmp_path),
                             argv=[bash_path(sys.executable), "-c", "import json,sys;print(json.dumps(sys.argv[1:]))", *arguments],
                             ssh_jump={"mode": "exec", "target": "jump"}))
    log = tmp_path / "transport.log"
    # Assign POSIX PATH inside Bash: Windows/MSYS translates an inherited PATH.
    # Refuse to proceed unless the stubs resolve, so this test cannot contact SSH.
    script = ("export PATH=" + shlex.quote(bash_path(tools) + ":/usr/bin:/bin")
              + "; [[ $(command -v ssh) == " + shlex.quote(bash_path(ssh_stub)) + " ]] || exit 94; "
              + "[[ $(command -v docker) == " + shlex.quote(bash_path(docker_stub)) + " ]] || exit 95; "
              + shlex.join(plan["argv"]))
    result = subprocess.run([executable, "-c", script], capture_output=True,
                            text=True, timeout=15, env={**os.environ, "MSYS2_ARG_CONV_EXCL": "*",
                            "TRANSPORT_LOG": bash_path(log)})
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == arguments
    assert log.read_text().splitlines() == ["jump", "compute"]
    assert not (tmp_path / "BAD").exists()


@pytest.mark.parametrize("jump", ["jump", {}, {"target": "jump"}, {"mode": "proxy", "target": "jump"},
                                  {"mode": "exec", "target": "-oEvil=yes"},
                                  {"mode": "exec", "target": "jump;evil"},
                                  {"mode": "exec", "target": "compute"},
                                  {"mode": "exec", "target": "jump", "key": "secret"}])
def test_invalid_jump_card_is_rejected(jump):
    with pytest.raises(FlowError):
        command_plan(card(ssh_jump=jump))


@pytest.mark.parametrize("backend", ["local", "k8s"])
def test_jump_cannot_be_silently_ignored_for_nonssh(backend):
    with pytest.raises(FlowError, match="only valid"):
        command_plan(card(backend=backend, ssh_jump={"mode": "exec", "target": "jump"}))


@pytest.mark.parametrize("changes", [{"cwd": 4}, {"cwd": "x\x00y"}, {"basis": []},
                                      {"env": {1: "bad"}}, {"schema_version": True},
                                      {"ssh_target": None}, {"activation": "relative.sh"},
                                      {"activation": 0}, {"backend": {}}])
def test_malformed_card_fails_as_flow_error(changes):
    with pytest.raises(FlowError):
        command_plan(card(**changes))


def test_jump_path_is_part_of_execution_identity():
    direct = command_plan(card())
    nested = command_plan(card(ssh_jump={"mode": "exec", "target": "jump"}))
    assert direct["card_hash"] != nested["card_hash"]


def test_jump_known_hosts_are_explicit_for_each_client():
    plan = command_plan(card(ssh_known_hosts="/work/owner's task/known_hosts",
                             ssh_jump={"mode": "exec", "target": "jump",
                                       "known_hosts": "D:/private local/known_hosts"}))
    outer = plan["argv"]
    inner = shlex.split(outer[-1])[1:]
    assert 'UserKnownHostsFile="D:/private local/known_hosts"' in outer
    assert 'UserKnownHostsFile="/work/owner\'s task/known_hosts"' in inner
    assert "StrictHostKeyChecking=yes" in inner and "StrictHostKeyChecking=yes" in outer


@pytest.mark.parametrize("value", ["relative", "/dev/null", "/work/%h", "/work/${USER}", "/work/x\nStrictHostKeyChecking=no", True])
def test_known_hosts_cannot_disable_trust_or_expand_unknown_paths(value):
    with pytest.raises(FlowError):
        command_plan(card(ssh_known_hosts=value))


def test_nested_known_hosts_path_belongs_to_jump_not_windows_controller():
    with pytest.raises(FlowError, match="jump host"):
        command_plan(card(ssh_known_hosts="D:/local/known_hosts", ssh_jump={"mode": "exec", "target": "jump"}))


def test_nonssh_known_hosts_is_not_ignored():
    with pytest.raises(FlowError, match="only valid"):
        command_plan(card(backend="local", ssh_known_hosts="/work/known_hosts"))


def test_known_hosts_option_is_accepted_by_real_openssh_config_parser(tmp_path):
    executable = shutil.which("ssh")
    if not executable:
        pytest.skip("OpenSSH unavailable for local -G parser check")
    config = tmp_path / "empty-ssh-config"
    config.write_text("")
    selected = "D:/private owner's task/known_hosts" if os.name == "nt" else "/private/owner's task/known_hosts"
    plan = command_plan(card(ssh_known_hosts=selected))
    option = next(value for value in plan["argv"] if value.startswith("UserKnownHostsFile="))
    # -G prints config and exits without connecting. An empty -F file avoids
    # executing any user-defined Match exec / ProxyCommand configuration.
    result = subprocess.run([executable, "-G", "-F", str(config), "-o", option, "fixture.invalid"],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    line = next(value for value in result.stdout.splitlines() if value.lower().startswith("userknownhostsfile "))
    assert selected in line


def controller_fixture(tmp_path):
    from hcu_trainflow.core import Store
    store = Store(tmp_path / 'store')
    store.create({'schema_version': 1, 'task_id': 't', 'mode': 'optimize', 'objective': 'CPU-only controller exclusion fixture',
                  'permissions': ['execute'], 'context': {'source': 'fixture'},
                  'budget': {'max_operations': 10, 'max_seconds': 120}})
    lease = store.lease('fixture-resource', 'controller', ttl=60)
    (tmp_path/'lease.json').write_text(json.dumps(lease))
    return store, lease


@pytest.mark.parametrize('pause', ['before-child', 'live-child'])
def test_actual_single_controller_excludes_reconciliation_and_duplicate_api_dispatch(tmp_path, pause):
    """A separate controller process holds the OS lock across both race windows."""
    import time
    from hcu_trainflow.coordination import reconcile_operation
    from hcu_trainflow.execution import run_command
    from hcu_trainflow.command_group import run_group
    store, lease = controller_fixture(tmp_path)
    script = tmp_path/'controller.py'
    script.write_text('''import json, pathlib, subprocess, sys, time
from hcu_trainflow.core import Store
from hcu_trainflow.execution import run_command
import hcu_trainflow.execution as execution
root = pathlib.Path(sys.argv[1]); pause = sys.argv[2]
ready, release = root/'ready', root/'release'
real = execution.subprocess.Popen
def delayed(*args, **kwargs):
    if pause == 'before-child':
        ready.write_text('controller before child')
        while not release.exists(): time.sleep(.01)
    return real(*args, **kwargs)
execution.subprocess.Popen = delayed
program = "import pathlib,time; r=pathlib.Path(" + repr(str(root)) + "); (r/'ready').write_text('child running')\\nwhile not (r/'release').exists(): time.sleep(.01)\\nprint('child complete')"
card = {'schema_version': 1, 'backend': 'local', 'argv': [sys.executable, '-c', program], 'cwd': str(root), 'timeout_seconds': 15, 'basis': 'CPU fixture'}
result = run_command(Store(root/'store'), 't', 'operation', card, json.loads((root/'lease.json').read_text()))
print(json.dumps(result))
''', encoding='utf-8')
    controller = subprocess.Popen([sys.executable, '-B', str(script), str(tmp_path), pause], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic()+10
        while not (tmp_path/'ready').exists() and controller.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        assert (tmp_path/'ready').exists(), 'controller did not reach test barrier'
        proof = store.put(b'CPU test: a process observation cannot authorize reconciliation while controller is active')
        with pytest.raises(FlowError, match='controller is active'):
            reconcile_operation(store, 'operation', 'failed', [proof], 'synthetic no-child/live-child observation')
        with pytest.raises(FlowError, match='controller is active'):
            run_command(store, 't', 'operation', {}, lease)
        with pytest.raises(FlowError, match='controller is active'):
            run_group(store, 't', 'operation', {}, [])
        with store.db() as db:
            assert db.execute("SELECT status FROM operations WHERE id='operation'").fetchone()[0] == 'started'
    finally:
        (tmp_path/'release').write_text('release only the CPU test child')
        stdout, stderr = controller.communicate(timeout=20)
    assert controller.returncode == 0, stderr
    result = json.loads(stdout)
    assert result['status'] == 'complete'
    assert (store.root/'runs/t/operation/stdout.log').read_text().strip() == 'child complete'
    with pytest.raises(FlowError, match='Only unresolved'):
        reconcile_operation(store, 'operation', 'failed', [proof], 'terminal state cannot be overwritten')
    with store.db() as db:
        assert json.loads(db.execute("SELECT result FROM operations WHERE id='operation'").fetchone()[0]) == result


def test_controller_process_crash_releases_lock_without_inventing_process_outcome(tmp_path):
    from hcu_trainflow.coordination import reconcile_operation
    store, lease = controller_fixture(tmp_path)
    script = tmp_path/'crashing-controller.py'
    script.write_text('''import json, os, pathlib, sys
from hcu_trainflow.core import Store
from hcu_trainflow.execution import run_command
import hcu_trainflow.execution as execution
root = pathlib.Path(sys.argv[1])
def crash(*args, **kwargs): os._exit(37)
execution.subprocess.Popen = crash
card = {'schema_version': 1, 'backend': 'local', 'argv': [sys.executable, '-c', "raise AssertionError('must not launch')"], 'cwd': str(root), 'timeout_seconds': 10, 'basis': 'CPU crash fixture'}
run_command(Store(root/'store'), 't', 'crash-op', card, json.loads((root/'lease.json').read_text()))
''', encoding='utf-8')
    result = subprocess.run([sys.executable, '-B', str(script), str(tmp_path)], capture_output=True, text=True, timeout=15)
    assert result.returncode == 37, result.stderr
    with store.db() as db:
        row = db.execute("SELECT status,result FROM operations WHERE id='crash-op'").fetchone()
        assert row['status'] == 'started' and row['result'] is None
    proof = store.put(b'CPU fixture controller exited before Popen could create any child; process is reaped')
    terminal = reconcile_operation(store, 'crash-op', 'failed', [proof], 'Actual controller exited; no child was launched in this fixture')
    assert terminal['status'] == 'failed'
