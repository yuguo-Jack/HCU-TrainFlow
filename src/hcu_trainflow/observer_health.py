"""Independent-domain watcher evidence validation, without recovery authority.

Reads immutable identity contracts and file snapshots, never a remote live
SQLite database. A heartbeat proves observation, not training progress.
"""
import hashlib
import json
import math
import os
import ntpath
import posixpath
from pathlib import Path, PurePosixPath, PureWindowsPath
import time
import uuid

from .core import FlowError, fingerprint, safe_id, write_json
from .monitor import check_heartbeat


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def lexical_path(value):
    """Source contracts may be reviewed on a different OS than their reader."""
    if not isinstance(value, str) or not value or '\x00' in value:
        raise FlowError('Invalid source path')
    return (PurePosixPath(posixpath.normpath(value)) if value.startswith('/')
            else PureWindowsPath(ntpath.normpath(value)))


def validate_contract(value):
    fields = {'schema_version', 'observer_id', 'task_id', 'context', 'context_epoch',
              'source_domain', 'observer_domain', 'source_root', 'source_workspace',
              'record_path', 'manifest_path', 'training_exit_path', 'lifecycle_dir',
              'expected', 'policy'}
    if not isinstance(value, dict) or set(value) != fields or type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise FlowError('Observer-health contract has unknown/missing fields or version')
    for name in ('observer_id', 'task_id'):
        safe_id(value[name])
    for name in ('context', 'source_domain', 'observer_domain'):
        if not isinstance(value[name], str) or not value[name].strip():
            raise FlowError('Nonempty ' + name + ' required')
    if type(value['context_epoch']) is not int or value['context_epoch'] < 0:
        raise FlowError('Nonnegative context_epoch required')
    if value['source_domain'] == value['observer_domain']:
        raise FlowError('Observer must be deployed in an explicitly different failure domain')
    for name in ('source_root', 'source_workspace', 'record_path', 'manifest_path', 'training_exit_path', 'lifecycle_dir'):
        if not lexical_path(value[name]).is_absolute():
            raise FlowError('Absolute observer-namespace path required: ' + name)
    # Lexical checks must not stat a possibly hung CFS mount in the sentinel.
    # The separately bounded reader resolves links before opening source files.
    root = lexical_path(value['source_root'])
    for name in ('source_workspace', 'record_path', 'manifest_path', 'training_exit_path', 'lifecycle_dir'):
        if not lexical_path(value[name]).is_relative_to(root):
            raise FlowError('Source path escapes explicit task source_root: ' + name)
    expected = value['expected']
    required = {'launch_id', 'spec_hash', 'observer_process', 'attempt_id', 'manifest_hash',
                'observer_started_at', 'training_process', 'attempt_started_at', 'expected_final_step', 'start_step'}
    if not isinstance(expected, dict) or set(expected) != required:
        raise FlowError('Exact expected watcher and attempt identities required')
    for name in ('launch_id', 'attempt_id'):
        safe_id(expected[name])
    for name in ('spec_hash', 'manifest_hash'):
        sha = expected[name]
        if not isinstance(sha, str) or len(sha) != 64 or set(sha) - set('0123456789abcdef'):
            raise FlowError('Invalid expected hash: ' + name)
    for name in ('observer_process', 'training_process'):
        ident = expected[name]
        if (not isinstance(ident, dict) or type(ident.get('pid')) is not int or ident['pid'] <= 0
                or not isinstance(ident.get('start_ticks'), str) or not ident['start_ticks'].isdecimal()
                or not all(isinstance(ident.get(k), str) and ident[k] for k in ('boot_id', 'pid_namespace'))):
            raise FlowError('Complete process identity required: ' + name)
    if any(not finite(expected[k]) or expected[k] < 0 for k in ('observer_started_at', 'attempt_started_at')):
        raise FlowError('Finite attempt/observer start times required')
    if (type(expected['start_step']) is not int or type(expected['expected_final_step']) is not int
            or not 0 <= expected['start_step'] < expected['expected_final_step']):
        raise FlowError('Expected step must exceed start/checkpoint step')
    policy = value['policy']
    if not isinstance(policy, dict) or set(policy) != {'heartbeat_max_age_seconds', 'startup_timeout_seconds', 'source_read_timeout_seconds'}:
        raise FlowError('Explicit freshness, startup and source-read deadlines required')
    for name, maximum in (('heartbeat_max_age_seconds', 86400), ('startup_timeout_seconds', 86400), ('source_read_timeout_seconds', 60)):
        if not finite(policy[name]) or not 0 < policy[name] <= maximum:
            raise FlowError('Invalid bounded policy: ' + name)
    return value


def source_paths(contract):
    run = Path(contract['lifecycle_dir'])
    return {'record': Path(contract['record_path']), 'manifest': Path(contract['manifest_path']),
            'training_exit': Path(contract['training_exit_path']),
            **{name: run / filename for name, filename in (
                ('request', 'request.json'), ('identity', 'identity.json'),
                ('heartbeat', 'heartbeat.json'), ('observer_exit', 'observer-exit.json'))}}


def capture_sources(contract, max_bytes=2 * 1024**2):
    """Call only in a separately bounded reader: a broken network FS can block open."""
    validate_contract(contract)
    result = {'schema_version': 1, 'files': {}, 'captured_at': time.time()}
    for name, path in source_paths(contract).items():
        try:
            if not path.resolve().is_relative_to(Path(contract['source_root']).resolve()):
                raise ValueError('source link escapes task source_root')
            with path.open('rb') as stream:
                raw = stream.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise ValueError('source exceeds bounded JSON size')
            text = raw.decode('utf-8')
            def invalid_constant(token):
                raise ValueError('Nonfinite JSON token: ' + token)
            value = json.loads(text, parse_constant=invalid_constant)
            if not isinstance(value, dict):
                raise ValueError('JSON source must be an object')
            result['files'][name] = {'status': 'ok', 'value': value, 'utf8': text,
                                     'sha256': hashlib.sha256(raw).hexdigest()}
        except FileNotFoundError:
            result['files'][name] = {'status': 'missing'}
        except (OSError, UnicodeError, ValueError) as exc:
            result['files'][name] = {'status': 'error', 'detail': type(exc).__name__ + ': ' + str(exc)}
    return result


def evaluate(contract, bundle, *, now, previous=None, freshness=None):
    """Pure classification. Does not inspect remote PIDs in the local namespace."""
    validate_contract(contract)
    if not finite(now):
        raise FlowError('Finite observer wall clock required')
    expected, policy = contract['expected'], contract['policy']
    previous = previous or {}
    issues = []

    def issue(kind, detail):
        if not any(x['kind'] == kind for x in issues):
            issues.append({'kind': kind, 'severity': 'critical', 'detail': detail})

    watermark = previous.get('clock_watermark', previous.get('checked_at', now))
    if now < watermark:
        issue('observer-health-clock-regressed', 'Independent observer clock moved backwards')
    if now < max(expected['observer_started_at'], expected['attempt_started_at']):
        issue('observer-source-clock-invalid', 'Expected start lies in the future')
    bundle = bundle if isinstance(bundle, dict) else {'error': 'invalid source snapshot'}
    files = bundle.get('files', {})
    if not isinstance(files, dict):
        files = {}
    if bundle.get('error'):
        issue('observer-source-unavailable', bundle['error'])

    def value(name, optional=False):
        row = files.get(name, {})
        if row.get('status') == 'ok' and isinstance(row.get('value'), dict):
            return row['value']
        if not (optional and row.get('status') == 'missing'):
            issue('observer-source-unavailable', name + ': ' + str(row.get('detail', row.get('status', 'not-read'))))
        return None

    record, manifest, request = value('record'), value('manifest'), value('request')
    heartbeat = value('heartbeat', optional=True)
    identity = value('identity', optional=True)
    observer_exit = value('observer_exit', optional=True)
    training_exit = value('training_exit', optional=True)
    binding = {'launch_id': expected['launch_id'], 'spec_hash': expected['spec_hash'],
               'process': expected['observer_process'], 'attempt_id': expected['attempt_id'], 'context': contract['context']}
    if record:
        spec = record.get('spec', {})
        if not isinstance(spec, dict):
            issue('observer-source-invalid', 'Observer spec must be an object')
            spec = {}
        if (record.get('launch_id') != expected['launch_id'] or record.get('spec_hash') != expected['spec_hash']
                or fingerprint(spec) != expected['spec_hash'] or record.get('process') != expected['observer_process']
                or record.get('started_at') != expected['observer_started_at']
                or record.get('run_dir') != contract['lifecycle_dir']
                or any(spec.get(key) != val for key, val in {
                    'workspace': contract['source_workspace'], 'task': contract['task_id'],
                    'context': contract['context'], 'attempt_id': expected['attempt_id'],
                    'manifest': contract['manifest_path'], 'manifest_hash': expected['manifest_hash'],
                    'exit_receipt': contract['training_exit_path']}.items())):
            issue('observer-source-identity-mismatch', 'Current observer record differs from pinned launch/configuration')
    if request and (request.get('launch_id') != expected['launch_id'] or fingerprint(request.get('spec', {})) != expected['spec_hash']):
        issue('observer-source-identity-mismatch', 'Lifecycle request differs from pinned configuration')
    if manifest and (fingerprint(manifest) != expected['manifest_hash'] or any(manifest.get(k) != v for k, v in {
            'context': contract['context'], 'attempt_id': expected['attempt_id'], 'process': expected['training_process'],
            'started_at': expected['attempt_started_at'], 'start_step': expected['start_step'],
            'expected_final_step': expected['expected_final_step']}.items())):
        issue('observer-source-identity-mismatch', 'Current training manifest differs from pinned attempt')
    for name, item in (('identity', identity), ('heartbeat', heartbeat), ('observer_exit', observer_exit)):
        if item and any(item.get(key) != val for key, val in binding.items()):
            issue('observer-source-identity-mismatch', name + ' launch/process/attempt/context mismatch')

    checked = heartbeat.get('checked_at') if heartbeat else None
    outer = heartbeat.get('result', {}) if heartbeat else {}
    monitor = outer.get('monitor', {}) if isinstance(outer, dict) else {}
    if not isinstance(monitor, dict):
        issue('observer-source-invalid', 'Monitor payload must be an object')
        monitor = {}
    sample = monitor.get('last_observation', {}) or {}
    if not isinstance(sample, dict):
        issue('observer-source-invalid', 'Last observation must be an object')
        sample = {}
    if heartbeat:
        if (monitor.get('status') not in ('healthy-observed', 'attention')
                or not isinstance(monitor.get('issues'), list)
                or type(monitor.get('completion_verified')) is not bool):
            issue('observer-source-invalid', 'Monitor status/issues/completion fields are invalid')
        if (not finite(checked) or not expected['observer_started_at'] <= checked <= now
                or (previous.get('source_checked_at') is not None and checked < previous['source_checked_at'])):
            issue('observer-source-clock-invalid', 'Heartbeat is future, pre-start or regressed')
        if (not isinstance(monitor, dict) or monitor.get('task_id') != contract['task_id']
                or monitor.get('context') != contract['context']
                or type(monitor.get('context_epoch')) is not int or monitor['context_epoch'] != contract['context_epoch']):
            issue('observer-source-identity-mismatch', 'Monitor task/context/epoch mismatch')
        if (not finite(monitor.get('checked_at')) or not finite(checked)
                or not expected['observer_started_at'] <= monitor['checked_at'] <= checked):
            issue('observer-source-clock-invalid', 'Monitor clock is outside observer lifetime')
        if sample and (sample.get('attempt_id') != expected['attempt_id'] or sample.get('context') != contract['context']):
            issue('observer-source-identity-mismatch', 'Last observation belongs to another attempt/context')

    training_exit_valid = False
    if training_exit:
        finished = training_exit.get('finished_at')
        training_exit_valid = (training_exit.get('attempt_id') == expected['attempt_id']
            and training_exit.get('context') == contract['context'] and training_exit.get('process') == expected['training_process']
            and type(training_exit.get('exit_code')) is int and finite(finished)
            and expected['attempt_started_at'] <= finished <= now)
        if not training_exit_valid:
            issue('observer-training-exit-unverified', 'Training exit identity/clock/type is invalid')
        elif training_exit['exit_code'] != 0:
            issue('observer-training-failed', 'Training exit code ' + str(training_exit['exit_code']))
    completed = False
    if observer_exit:
        finished = observer_exit.get('finished_at')
        if not finite(finished) or not expected['observer_started_at'] <= finished <= now:
            issue('observer-source-clock-invalid', 'Observer exit time invalid')
        completed = bool(identity and heartbeat and training_exit_valid and training_exit['exit_code'] == 0
            and type(observer_exit.get('exit_code')) is int and observer_exit['exit_code'] == 0
            and observer_exit.get('reason') == 'training-completion-verified'
            and monitor.get('completion_verified') is True and monitor.get('status') == 'healthy-observed'
            and monitor.get('issues') == [] and sample.get('phase') == 'finished' and sample.get('completed') is True
            and sample.get('exit_receipt') == training_exit and sample.get('process_identity') == expected['training_process']
            and sample.get('expected_final_step') == expected['expected_final_step']
            and type(sample.get('step')) is int and sample['step'] >= expected['expected_final_step']
            and sample.get('job_alive') is False and not sample.get('fatal_errors')
            and finite(checked) and finite(finished) and finite(monitor.get('checked_at'))
            and finite(sample.get('timestamp')) and training_exit['finished_at'] <= sample['timestamp'] <= monitor['checked_at']
            and training_exit['finished_at'] <= monitor['checked_at'] <= checked <= finished
            and all(sample.get(k) is None or finite(sample[k]) for k in ('loss', 'grad_norm')))
        if not completed:
            issue('observer-exited-without-verified-completion', 'Observer exited/stopped without matching successful training completion proof')
    if not completed:
        if heartbeat:
            age = now - checked if finite(checked) else None
            fresh = freshness if freshness is not None else {
                'status': 'pass' if age is not None and 0 <= age <= policy['heartbeat_max_age_seconds'] else 'fail'}
            if fresh['status'] != 'pass':
                issue('observer-heartbeat-stale', 'No fresh heartbeat from the pinned observer launch')
            if monitor.get('status') == 'attention' or monitor.get('issues'):
                issue('observer-training-attention', 'Fresh observer reports training/collector incidents; inspect source monitor')
            if identity is None:
                issue('observer-source-identity-mismatch', 'Heartbeat exists without matching observer identity')
        elif not any(item['kind'] == 'observer-source-unavailable' for item in issues):
            if previous.get('source_checked_at') is not None:
                issue('observer-heartbeat-missing', 'Previously observed heartbeat disappeared; source cause unverified')
            elif now - expected['observer_started_at'] > policy['startup_timeout_seconds']:
                issue('observer-startup-timeout', 'Observer did not produce a heartbeat before explicit startup deadline')
    status = 'attention' if issues else 'completed' if completed else 'observing' if heartbeat else 'starting'
    return {'schema_version': 1, 'observer_id': contract['observer_id'], 'task_id': contract['task_id'],
            'context': contract['context'], 'context_epoch': contract['context_epoch'],
            'attempt_id': expected['attempt_id'], 'launch_id': expected['launch_id'],
            'checked_at': now, 'clock_watermark': max(now, watermark),
            'source_checked_at': max([x for x in (checked, previous.get('source_checked_at')) if finite(x)], default=None),
            'status': status, 'issues': issues, 'completion_verified': completed and not issues,
            'source_domain': contract['source_domain'], 'observer_domain': contract['observer_domain'],
            'remote_process_liveness': 'not directly probed; evidence-based observation only',
            'recovery_action': 'none', 'notification_delivery': 'not configured'}


def record_health(store, contract, bundle, *, now=None):
    """Own Store only. Deduplicate open/resolve events and retain exact source bytes."""
    validate_contract(contract)
    source = Path(os.path.normpath(contract['source_workspace']))
    root = store.root.resolve()
    if root == source or root.is_relative_to(source) or source.is_relative_to(root):
        raise FlowError('Sentinel requires a separate Store outside watched workspace')
    now = time.time() if now is None else now
    contract_hash = fingerprint(contract)
    for row in bundle.get('files', {}).values():
        if row.get('status') == 'ok':
            text = row.get('utf8')
            if (not isinstance(text, str) or hashlib.sha256(text.encode()).hexdigest() != row.get('sha256')
                    or json.loads(text) != row.get('value')):
                raise FlowError('Source snapshot bytes/value/hash differ')
    raw = json.dumps(bundle, ensure_ascii=False, allow_nan=False).encode()
    proof = store.put(raw)
    key = 'observer-health:' + contract['observer_id']
    heartbeat = bundle.get('files', {}).get('heartbeat', {})
    freshness = None
    if heartbeat.get('status') == 'ok' and finite(heartbeat.get('value', {}).get('checked_at')):
        # Reuse the existing primitive on the retained snapshot, never re-read
        # a changing remote file between identity and freshness validation.
        heartbeat_sha = store.put(heartbeat['utf8'].encode())
        with store.db() as db:
            retained = store.root / db.execute('SELECT path FROM artifacts WHERE id=?', (heartbeat_sha,)).fetchone()['path']
        freshness = check_heartbeat(retained, contract['policy']['heartbeat_max_age_seconds'], now=now)
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        found = db.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
        previous = json.loads(found['value']) if found else {}
        if previous and previous.get('contract_hash') != contract_hash:
            raise FlowError('Pinned observer contract changed; register a new observer_id')
        result = evaluate(contract, bundle, now=now, previous=previous.get('result'), freshness=freshness)
        active = previous.get('active', {})
        for issue in result['issues']:
            if issue['kind'] not in active:
                incident = uuid.uuid4().hex
                store.event(db, contract['task_id'], 'incident-opened', {
                    'incident_id': incident, 'origin': 'independent-observer-health', 'observer_id': contract['observer_id'],
                    'context': contract['context'], 'context_epoch': contract['context_epoch'],
                    'attempt_id': contract['expected']['attempt_id'], 'launch_id': contract['expected']['launch_id'],
                    'evidence': [proof], 'recovery_action': 'none', **issue}, channel='agent')
                active[issue['kind']] = incident
        # Loss of the evidence source cannot resolve an existing outage. Only
        # positively observing again or exact terminal proof clears incidents.
        if result['status'] in ('observing', 'completed'):
            for kind, incident in active.items():
                store.event(db, contract['task_id'], 'incident-cleared', {
                    'incident_id': incident, 'origin': 'independent-observer-health', 'observer_id': contract['observer_id'],
                    'context': contract['context'], 'context_epoch': contract['context_epoch'],
                    'attempt_id': contract['expected']['attempt_id'], 'kind': kind, 'evidence': [proof]}, channel='agent')
            active = {}
        result['evidence'] = [proof]
        result['unresolved_incidents'] = sorted(active)
        db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)', (key, json.dumps({
            'contract_hash': contract_hash, 'result': result, 'active': active}, allow_nan=False)))
    write_json(store.root / 'observer-health' / (contract['observer_id'] + '-heartbeat.json'), result)
    return result
