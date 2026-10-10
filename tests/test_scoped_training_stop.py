"""Stop-policy tests; actual Linux pidfd / torchrun qualification is separate."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from hcu_trainflow.core import FlowError, write_json


@pytest.fixture
def case(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('scoped_stop', Path(__file__).parents[1] / 'scripts/stop_torchrun_attempt.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    wrapper = dict(pid=123, start_ticks='10', boot_id='test', pid_namespace='test')
    target = dict(wrapper, pid=456, start_ticks='20')
    write_json(tmp_path / 'attempt.json', dict(schema_version=1, context='ctx', attempt_id='run',
        log_path=str(tmp_path / 'training.log'), expected_final_step=10, start_step=0,
        log_start_offset=0, started_at=1, log_timezone='UTC', process=wrapper))
    write_json(tmp_path / 'child.json', dict(pid=200, wrapper_process=wrapper))
    argv = ['python', '-m', 'torch.distributed.run', 'train.py']
    monkeypatch.setattr(mod, 'parent', lambda pid: 123)
    monkeypatch.setattr(mod, 'find_torchrun', lambda root: (target, argv))
    monkeypatch.setattr(mod, 'command', lambda pid: argv)
    monkeypatch.setattr(mod, 'descendant', lambda pid, root: True)
    identities = {123: dict(status='alive', identity=wrapper), 456: dict(status='alive', identity=target)}
    monkeypatch.setattr(mod, 'process_identity', lambda pid: identities[pid])
    close, send = Mock(), Mock()
    monkeypatch.setattr(mod, 'os', SimpleNamespace(pidfd_open=Mock(return_value=71), close=close))
    monkeypatch.setattr(mod, 'signal', SimpleNamespace(pidfd_send_signal=send, SIGTERM=15))
    clock = iter([0, 0, 2, 3])
    monkeypatch.setattr(mod.time, 'monotonic', lambda: next(clock))
    monkeypatch.setattr(mod.time, 'sleep', lambda _: None)
    return SimpleNamespace(mod=mod, root=tmp_path, wrapper=wrapper, target=target,
                           identities=identities, send=send, close=close)


def terminal(case, **changes):
    write_json(case.root / 'exit.json', dict(context='ctx', attempt_id='run',
               process=case.wrapper, exit_code=1, **changes))


def test_only_verified_target_signaled_and_receipt_required(case):
    def sent(fd, sig):
        assert (fd, sig) == (71, 15)
        terminal(case)
        case.identities[456] = dict(status='exited')
    case.send.side_effect = sent
    result = case.mod.stop(case.root, context='ctx', attempt_id='run', timeout=1)
    assert result['status'] == 'terminal-receipt-observed'
    assert result['exit_code'] == 1
    case.close.assert_called_once_with(71)


def test_context_mismatch_sends_nothing(case):
    with pytest.raises(FlowError, match='mismatch'):
        case.mod.stop(case.root, context='another', attempt_id='run')
    case.send.assert_not_called()


def test_existing_exit_sends_nothing(case):
    terminal(case)
    with pytest.raises(FlowError, match='already'):
        case.mod.stop(case.root, context='ctx', attempt_id='run')
    case.send.assert_not_called()


def test_reparented_target_sends_nothing(case, monkeypatch):
    monkeypatch.setattr(case.mod, 'descendant', lambda *args: False)
    with pytest.raises(FlowError, match='ancestry'):
        case.mod.stop(case.root, context='ctx', attempt_id='run')
    case.send.assert_not_called()
    case.close.assert_called_once_with(71)


def test_unknown_process_is_not_confirmed_exit(case):
    def sent(*args):
        terminal(case)
        case.identities[456] = dict(status='unknown', reason='permission')
    case.send.side_effect = sent
    with pytest.raises(FlowError, match='unconfirmed'):
        case.mod.stop(case.root, context='ctx', attempt_id='run', timeout=1)
    assert not (case.root / 'stop-receipt.json').exists()


def test_other_attempt_receipt_cannot_confirm_stop(case):
    def sent(*args):
        write_json(case.root / 'exit.json', dict(context='ctx', attempt_id='other', process=case.wrapper, exit_code=1))
        case.identities[456] = dict(status='exited')
    case.send.side_effect = sent
    with pytest.raises(FlowError, match='does not match'):
        case.mod.stop(case.root, context='ctx', attempt_id='run', timeout=1)


def test_platform_without_pidfd_does_not_fallback(case, monkeypatch):
    monkeypatch.setattr(case.mod, 'os', SimpleNamespace())
    with pytest.raises(FlowError, match='pidfd'):
        case.mod.stop(case.root, context='ctx', attempt_id='run')
    case.send.assert_not_called()
