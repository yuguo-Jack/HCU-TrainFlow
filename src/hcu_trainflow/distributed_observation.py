"""CPU-only member evidence beside (not instead of) designated-progress monitoring.

The caller deploys collectors in each launcher's Linux PID namespace and moves
their immutable observations to an aggregator. No SSH, GPU work or recovery is
performed here. The process under audit is the launch wrapper: worker health is
only visible through its supervision, log and real exit receipt.
"""
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import time

from .core import FlowError, fingerprint, read_json, safe_id, write_json
from .training_logs import observer_lock, parse_megatron_line, process_identity, validate_manifest


def _number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _hash(value):
    return isinstance(value, str) and len(value) == 64 and not set(value) - set('0123456789abcdef')


def validate_group(group):
    required = {'schema_version', 'task', 'context', 'context_epoch', 'group_attempt',
                'progress_member', 'start_step', 'expected_final_step', 'members', 'policy'}
    if not isinstance(group, dict) or set(group) != required or type(group['schema_version']) is not int or group['schema_version'] != 1:
        raise FlowError('Distributed group requires exact version-one fields')
    for name in ('task', 'group_attempt', 'progress_member'):
        safe_id(group[name])
    if not isinstance(group['context'], str) or not group['context']:
        raise FlowError('Nonempty group context required')
    if type(group['context_epoch']) is not int or group['context_epoch'] < 0:
        raise FlowError('Nonnegative context epoch required')
    if (type(group['start_step']) is not int or type(group['expected_final_step']) is not int
            or not 0 <= group['start_step'] < group['expected_final_step']):
        raise FlowError('Expected final step must exceed start/checkpoint step')
    if not isinstance(group['members'], list) or not 2 <= len(group['members']) <= 256:
        raise FlowError('Group requires 2..256 mandatory members')
    ids, nodes, manifests = set(), set(), set()
    for member in group['members']:
        if not isinstance(member, dict) or set(member) != {'id', 'node', 'manifest_sha256'}:
            raise FlowError('Member requires id/node/manifest_sha256')
        safe_id(member['id'])
        if member['id'].casefold() in ids:
            raise FlowError('Duplicate member identity')
        if not isinstance(member['node'], str) or not member['node'].strip() or member['node'] in nodes:
            raise FlowError('Distinct explicit member node required')
        if not _hash(member['manifest_sha256']):
            raise FlowError('Exact attempt.json file SHA256 required')
        if member['manifest_sha256'] in manifests:
            raise FlowError('Each distributed member requires its own distinct launch manifest')
        ids.add(member['id'].casefold()); nodes.add(member['node']); manifests.add(member['manifest_sha256'])
    if group['progress_member'] not in {m['id'] for m in group['members']}:
        raise FlowError('Progress source must be a mandatory member')
    policy = group['policy']
    if not isinstance(policy, dict) or set(policy) != {'heartbeat_max_age_seconds', 'clock_skew_seconds'}:
        raise FlowError('Explicit heartbeat age and clock skew policy required')
    if (not _number(policy['heartbeat_max_age_seconds']) or not 0 < policy['heartbeat_max_age_seconds'] <= 86400
            or not _number(policy['clock_skew_seconds']) or policy['clock_skew_seconds'] > 300):
        raise FlowError('Invalid distributed freshness policy')
    return group


def _json(raw):
    return json.loads(raw.decode('utf-8-sig'), parse_constant=lambda x: (_ for _ in ()).throw(FlowError('Nonfinite JSON: ' + x)))


def _manifest(raw, group, member):
    if hashlib.sha256(raw).hexdigest() != member['manifest_sha256']:
        raise FlowError('Frozen member manifest SHA256 changed')
    value = _json(raw)
    # A Windows controller must validate a Linux source path lexically, not as
    # a Windows filesystem path. All other manifest checks remain shared.
    path = value.get('log_path') if isinstance(value, dict) else None
    if not isinstance(path, str) or not (PurePosixPath(path).is_absolute() or PureWindowsPath(path).is_absolute()):
        raise FlowError('Member log path must be absolute in its source namespace')
    validate_manifest({**value, 'log_path': str(Path.cwd() / 'validation-placeholder')})
    if any(value[name] != group[name] for name in ('context', 'start_step', 'expected_final_step')):
        raise FlowError('Member manifest differs from group context/step contract')
    return value


def _member(group, mid):
    validate_group(group)
    for member in group['members']:
        if member['id'] == mid:
            return member
    raise FlowError('Unknown distributed member')


def _receipt(value, manifest, now):
    if value is None:
        return None
    if (not isinstance(value, dict) or type(value.get('exit_code')) is not int
            or any(value.get(k) != manifest[k] for k in ('context', 'attempt_id', 'process'))
            or not _number(value.get('finished_at')) or not manifest['started_at'] <= value['finished_at'] <= now):
        raise FlowError('Exit receipt identity or time differs from frozen attempt')
    seal = value.get('log_evidence')
    if (not isinstance(seal, dict) or seal.get('path') != manifest['log_path']
            or type(seal.get('bytes')) is not int or seal['bytes'] < manifest['log_start_offset']
            or not _hash(seal.get('sha256'))):
        raise FlowError('Exit receipt requires original complete log seal')
    return value


def _stat(stat):
    return [stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns]


def _check_output(output_path, root, inputs=()):
    if output_path is None:
        return
    output, root = Path(output_path).resolve(), Path(root).resolve()
    protected = {root, root / 'member-state.json', root / 'aggregate-state.json', root / 'observer.lock'}
    protected.update(Path(p).resolve() for p in inputs if p is not None)
    if output in protected or output.is_relative_to(root / 'observations'):
        raise FlowError('Latest output cannot overwrite source, durable state, lock or immutable observations')


def _log_poll(manifest, state, receipt, now):
    """Read at most 16 MiB of new lines; no iteration requirement for peers."""
    with Path(manifest['log_path']).open('rb') as stream:
        descriptor = stream.fileno()
        stat = os.fstat(descriptor)
        identity = [stat.st_dev, stat.st_ino]
        old_prefix = state.get('prefix_bytes', 0)
        prefix = stream.read(min(128, stat.st_size))
        if (state.get('file_identity', identity) != identity or stat.st_size < state['offset']
                or (old_prefix and hashlib.sha256(prefix[:old_prefix]).hexdigest() != state['prefix_hash'])):
            raise FlowError('Raw member log replaced, truncated or rewritten; do not reset its cursor')
        state.update(file_identity=identity, prefix_bytes=len(prefix), prefix_hash=hashlib.sha256(prefix).hexdigest())
        stream.seek(state['offset'])
        consumed = 0
        while consumed < 16 * 1024**2:
            position = stream.tell()
            raw = stream.readline(1024**2)
            if not raw:
                break
            if not raw.endswith(b'\n') and not (receipt is not None and len(raw) < 1024**2):
                if len(raw) == 1024**2:
                    state['fatal_errors'].append('member-log-line-exceeds-1MiB')
                break
            consumed += len(raw)
            state['offset'] = stream.tell()
            try:
                parsed = parse_megatron_line(raw.decode('utf-8'), log_timezone=manifest['log_timezone'], observed_at=now)
            except (UnicodeError, ValueError):
                state['fatal_errors'].append('member-log-record-decoding-error')
                continue
            if not parsed:
                continue
            source = {'path': manifest['log_path'], 'offset': position, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            if parsed.get('warning'):
                state['warnings'].append(parsed['warning'])
            if parsed['kind'] == 'fatal':
                state['fatal_errors'].append(parsed['fatal'])
                state['first_error'] = state.get('first_error') or {'source': source, 'message': parsed['fatal']}
            if parsed['kind'] == 'iteration':
                step = parsed['step']
                if (parsed['total_steps'] != manifest['expected_final_step'] or not manifest['start_step'] <= step <= manifest['expected_final_step']
                        or step < state['step']):
                    state['fatal_errors'].append('member-iteration-contract-or-step-regression')
                if parsed.get('nonfinite'):
                    state['fatal_errors'].append('nonfinite-training-numerics-observed')
                timestamp = parsed['timestamp']
                if parsed['timestamp_basis'] == 'source-log-clock':
                    if not manifest['started_at'] <= timestamp <= now + 30 or timestamp < state.get('source_clock', timestamp):
                        state['fatal_errors'].append('member-progress-source-clock-invalid-or-regressed')
                    state['source_clock'] = max(timestamp, state.get('source_clock', timestamp))
                state['iterations'] += 1
                state['step'] = max(state['step'], step)
                state['progress'] = {'step': step, 'timestamp': timestamp, 'timestamp_basis': parsed['timestamp_basis'], 'source': source}
        state['backlog'] = state['offset'] < stat.st_size
        after = os.fstat(descriptor)
        state['log_stat'] = _stat(after)
        if receipt and not state['backlog']:
            if _stat(stat) != _stat(after):
                raise FlowError('Sealed member log changed during parsing')
            seal = receipt['log_evidence']
            if (state.get('progress', {}).get('timestamp_basis') == 'source-log-clock'
                    and state['progress']['timestamp'] > receipt['finished_at']):
                raise FlowError('Final progress source clock lies after the member exit')
            # Exit sealing is verified once for each exact immutable log stat.
            # Raw logs remain retained; this cache is not a substitute for them.
            proof_key = fingerprint({'receipt': receipt, 'stat': _stat(after)})
            if state.get('seal_key') != proof_key:
                stream.seek(0)
                sha = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    sha.update(chunk)
                if _stat(os.fstat(descriptor)) != _stat(after) or after.st_size != seal['bytes'] or sha.hexdigest() != seal['sha256']:
                    raise FlowError('Member exit log seal hash/size changed')
                progress = state.get('progress')
                if progress:
                    source = progress['source']
                    stream.seek(source['offset'])
                    if (source['offset'] + source['bytes'] > seal['bytes']
                            or hashlib.sha256(stream.read(source['bytes'])).hexdigest() != source['sha256']):
                        raise FlowError('Sealed log does not contain the originally observed final progress')
                # Ensure the path still refers to the file we verified.
                if _stat(Path(manifest['log_path']).stat()) != _stat(after):
                    raise FlowError('Member log path changed while verifying seal')
                state['seal_key'] = proof_key
            state['log_seal_verified'] = True


def collect_member(group, mid, manifest_path, state_dir, *, exit_path=None, now=None, process_status=None,
                   collector_identity=None, output_path=None):
    """Node-local CPU collection; process_status is a test/site-adapter seam.

    collector_identity is likewise a CPU test/site-adapter seam. Production
    defaults independently read this collector's boot and PID namespace.
    Use a dedicated state-dir per group context epoch and member. Never share
    this cursor directory with the existing progress-source training watcher.
    """
    member = _member(group, mid)
    now = time.time() if now is None else now
    if not _number(now):
        raise FlowError('Finite collection time required')
    raw = Path(manifest_path).read_bytes()
    manifest = _manifest(raw, group, member)
    scope = {'group_hash': fingerprint(group), 'member': mid, 'manifest_sha256': member['manifest_sha256']}
    root = Path(state_dir)
    _check_output(output_path, root, (manifest_path, manifest['log_path'], exit_path))
    with observer_lock(root):
        path = root / 'member-state.json'
        state = read_json(path) if path.exists() else {'scope': scope, 'sequence': 0, 'offset': manifest['log_start_offset'],
                    'step': manifest['start_step'], 'iterations': 0, 'fatal_errors': [], 'warnings': []}
        if state['scope'] != scope:
            raise FlowError('Member observation scope changed; preserve old state and use a new directory')
        if now < state.get('clock_watermark', now) or now < manifest['started_at']:
            state['fatal_errors'].append('member-observer-clock-regressed-or-before-attempt')
        state['clock_watermark'] = max(now, state.get('clock_watermark', now))
        observed = process_status if process_status is not None else process_identity(manifest['process']['pid'])
        collector = collector_identity if collector_identity is not None else process_identity(os.getpid()).get('identity')
        issues, receipt = [], None
        if not isinstance(collector, dict) or any(collector.get(k) != manifest['process'][k] for k in ('boot_id', 'pid_namespace')):
            issues.append('collector-not-in-frozen-member-boot-or-pid-namespace')
        try:
            receipt = _receipt(read_json(exit_path), manifest, now) if exit_path and Path(exit_path).exists() else None
            if state.get('exit_receipt') and receipt != state['exit_receipt']:
                raise FlowError('Member exit receipt disappeared or changed after verification')
            if receipt:
                state['exit_receipt'] = receipt
        except (OSError, ValueError) as exc:
            issues.append('invalid-exit-receipt: ' + str(exc))
            if state.get('exit_receipt'):
                state['fatal_errors'].append('previously-verified-member-receipt-changed-or-unavailable')
        state['log_seal_verified'] = False
        try:
            _log_poll(manifest, state, receipt, now)
        except (OSError, ValueError) as exc:
            issues.append('member-log-audit-failed: ' + str(exc))
            if isinstance(exc, FlowError):
                state['fatal_errors'].append(str(exc))
        state['fatal_errors'] = list(dict.fromkeys(state['fatal_errors']))
        state['warnings'] = list(dict.fromkeys(state['warnings']))
        if state['fatal_errors']:
            issues.append('member-fatal-errors')
        if receipt and receipt['exit_code'] != 0:
            issues.append('member-exit-nonzero')
        if state.get('backlog'):
            issues.append('member-log-backlog')
        matched = observed.get('identity') == manifest['process']
        alive = observed.get('status') == 'alive' and matched
        if (observed.get('identity') is not None or observed.get('status') == 'alive') and not matched:
            issues.append('member-process-identity-mismatch')
        if observed.get('status') == 'unknown':
            issues.append('member-process-unknown')
        if alive and observed.get('process_state') in {'T', 't'}:
            issues.append('member-process-stopped')
        exit_verified = bool(receipt and state['log_seal_verified'] and not state.get('backlog'))
        if not alive and not exit_verified:
            issues.append('member-exited-without-verified-receipt')
        terminal = exit_verified and receipt['exit_code'] == 0 and not issues
        state['sequence'] += 1
        snapshot = {'schema_version': 1, **scope, 'task': group['task'], 'context': group['context'],
                    'context_epoch': group['context_epoch'], 'group_attempt': group['group_attempt'],
                    'node': member['node'], 'sequence': state['sequence'], 'observed_at': now,
                    'manifest_utf8': raw.decode('utf-8'), 'process_observation': observed, 'collector_identity': collector,
                    'exit_receipt': receipt, 'exit_verified': exit_verified,
                    'log_seal_verified': state['log_seal_verified'], 'log_offset': state['offset'],
                    'backlog': state.get('backlog', False), 'step': state['step'], 'iterations': state['iterations'],
                    'progress': state.get('progress'), 'fatal_errors': state['fatal_errors'],
                    'first_error': state.get('first_error'), 'warnings': state['warnings'], 'issues': issues,
                    'state': 'attention' if issues else ('exited-success' if terminal else 'running'),
                    'audit_scope': 'launcher identity, supervised exit and member log; not every worker PID or device health',
                    'previous_sha256': state.get('last_snapshot_sha256')}
        snapshot['sha256'] = fingerprint(snapshot)
        write_json(root / 'observations' / (str(state['sequence']).zfill(12) + '-' + snapshot['sha256'] + '.json'), snapshot)
        state['last_snapshot_sha256'] = snapshot['sha256']
        write_json(path, state)
        if output_path is not None:
            write_json(output_path, snapshot)
        return snapshot


def _validated_snapshot(group, member, row, now):
    if not isinstance(row, dict) or not _hash(row.get('sha256')):
        raise FlowError('Missing member snapshot')
    if fingerprint({k: v for k, v in row.items() if k != 'sha256'}) != row['sha256']:
        raise FlowError('Member observation digest mismatch')
    expected = {'group_hash': fingerprint(group), 'member': member['id'], 'node': member['node'],
                'manifest_sha256': member['manifest_sha256'], 'task': group['task'], 'context': group['context'],
                'context_epoch': group['context_epoch'], 'group_attempt': group['group_attempt']}
    if any(row.get(k) != v for k, v in expected.items()):
        raise FlowError('Wrong group, epoch, member or frozen manifest')
    if (type(row.get('schema_version')) is not int or row['schema_version'] != 1
            or type(row.get('sequence')) is not int or row['sequence'] <= 0 or not _number(row.get('observed_at'))
            or any(type(row.get(k)) is not bool for k in ('exit_verified', 'log_seal_verified', 'backlog'))
            or any(type(row.get(k)) is not int or row[k] < 0 for k in ('log_offset', 'step', 'iterations'))
            or any(not isinstance(row.get(k), list) or any(not isinstance(x, str) for x in row[k]) for k in ('issues', 'warnings', 'fatal_errors'))
            or not isinstance(row.get('process_observation'), dict)):
        raise FlowError('Invalid member observation fields')
    if not isinstance(row.get('manifest_utf8'), str):
        raise FlowError('Original frozen manifest bytes required')
    manifest = _manifest(row['manifest_utf8'].encode('utf-8'), group, member)
    if row['observed_at'] < manifest['started_at']:
        raise FlowError('Member observed before attempt start')
    if row['observed_at'] > now + group['policy']['clock_skew_seconds']:
        raise FlowError('Member observation clock lies in the future')
    progress = row.get('progress')
    if progress is not None:
        if not isinstance(progress, dict) or type(progress.get('step')) is not int or not isinstance(progress.get('source'), dict):
            raise FlowError('Invalid original member progress evidence')
        source = progress['source']
        if (source.get('path') != manifest['log_path'] or type(source.get('offset')) is not int
                or source['offset'] < manifest['log_start_offset'] or type(source.get('bytes')) is not int
                or source['bytes'] <= 0 or source['offset'] + source['bytes'] > row['log_offset']
                or not _hash(source.get('sha256')) or not _number(progress.get('timestamp'))
                or progress.get('timestamp_basis') not in {'source-log-clock', 'first-observed-no-source-clock'}
                or progress['timestamp'] > row['observed_at'] + 30):
            raise FlowError('Progress source range/hash/time differs from member log')
    return manifest


def aggregate_members(group, observations, state_dir, *, now=None, output_path=None):
    """Durably assess every required member. Never infer peers from the progress source.

    observations maps mandatory member IDs to source snapshots or missing/error
    envelopes. It never reads a remote PID using the controller's namespace.
    """
    validate_group(group)
    now = time.time() if now is None else now
    if not _number(now) or not isinstance(observations, dict):
        raise FlowError('Finite aggregate clock and member snapshot mapping required')
    expected_ids = {m['id'] for m in group['members']}
    if set(observations) - expected_ids:
        raise FlowError('Unexpected observations outside mandatory member contract')
    scope = fingerprint(group)
    root = Path(state_dir)
    _check_output(output_path, root)
    with observer_lock(root):
        path = root / 'aggregate-state.json'
        state = read_json(path) if path.exists() else {'group_hash': scope, 'members': {}, 'sequence': 0, 'sticky_issues': []}
        if state['group_hash'] != scope:
            raise FlowError('Aggregate scope changed; use a new context/epoch/attempt state directory')
        if now < state.get('clock_watermark', now):
            state['sticky_issues'].append('aggregator-clock-regressed')
        state['clock_watermark'] = max(now, state.get('clock_watermark', now))
        summaries, issues = {}, list(dict.fromkeys(state['sticky_issues']))
        for member in group['members']:
            mid, row = member['id'], observations.get(member['id'])
            errors = []
            try:
                manifest = _validated_snapshot(group, member, row, now)
                prior = state['members'].get(mid)
                if prior and (row['sequence'] < prior['sequence'] or row['observed_at'] < prior['observed_at']
                              or (row['sequence'] == prior['sequence'] and row['sha256'] != prior['sha256'])
                              or (row['sequence'] == prior['sequence'] + 1 and row['previous_sha256'] != prior['sha256'])):
                    error = mid + ': member-observation-replayed-or-regressed'
                    state['sticky_issues'].append(error)
                    raise FlowError(error)
                if now - row['observed_at'] > group['policy']['heartbeat_max_age_seconds']:
                    errors.append('member-observation-stale')
                errors.extend(row['issues'])
                if row['fatal_errors']:
                    errors.append('member-fatal-errors')
                if row['backlog']:
                    errors.append('member-log-backlog')
                proc = row['process_observation']
                collector = row.get('collector_identity')
                if not isinstance(collector, dict) or any(collector.get(k) != manifest['process'][k] for k in ('boot_id', 'pid_namespace')):
                    errors.append('collector-not-in-frozen-member-boot-or-pid-namespace')
                alive = proc.get('status') == 'alive' and proc.get('identity') == manifest['process']
                receipt = _receipt(row.get('exit_receipt'), manifest, row['observed_at'])
                if (receipt and row.get('progress', {}) and row['progress'].get('timestamp_basis') == 'source-log-clock'
                        and row['progress']['timestamp'] > receipt['finished_at']):
                    errors.append('member-progress-clock-after-exit')
                verified = bool(receipt and row['exit_verified'] is True and row['log_seal_verified'] is True
                                and row['log_offset'] == receipt['log_evidence']['bytes'] and not row['backlog'])
                if receipt and receipt['exit_code'] != 0:
                    errors.append('member-exit-nonzero')
                if (proc.get('status') not in {'alive', 'exited'} or (proc.get('status') == 'alive' and not alive)
                        or (proc.get('identity') is not None and proc['identity'] != manifest['process'])):
                    errors.append('member-process-unverified')
                if alive and proc.get('process_state') in {'T', 't'}:
                    errors.append('member-process-stopped')
                if not alive and not verified:
                    errors.append('member-exited-without-verified-receipt')
                if receipt and not verified:
                    errors.append('member-exit-proof-incomplete')
                done = verified and receipt['exit_code'] == 0 and not errors
                summaries[mid] = {'node': member['node'], 'state': 'attention' if errors else ('exited-success' if done else 'running'),
                    'alive': alive, 'exit_verified': verified, 'exit_code': receipt['exit_code'] if receipt else None,
                    'step': row['step'], 'iterations': row['iterations'], 'progress': row.get('progress'),
                    'observed_at': row['observed_at'], 'age_seconds': max(0, now - row['observed_at']),
                    'snapshot_sha256': row['sha256'], 'warnings': row['warnings'], 'issues': list(dict.fromkeys(errors))}
                state['members'][mid] = {'sequence': row['sequence'], 'observed_at': row['observed_at'], 'sha256': row['sha256']}
                if row['fatal_errors'] or (receipt and receipt['exit_code'] != 0):
                    state['sticky_issues'].append(mid + ': terminal-or-numerical-failure-observed')
            except (ValueError, TypeError, KeyError) as exc:
                summaries[mid] = {'node': member['node'], 'state': 'attention', 'issues': ['member-proof-invalid: ' + str(exc)]}
            issues.extend(mid + ': ' + error for error in summaries[mid]['issues'])
        progress = summaries[group['progress_member']]
        progress_verified = (progress.get('iterations', 0) > 0 and progress.get('step') == group['expected_final_step']
                             and isinstance(progress.get('progress'), dict)
                             and progress['progress'].get('step') == group['expected_final_step'])
        all_exited = all(row['state'] == 'exited-success' for row in summaries.values())
        if all_exited and not progress_verified:
            issues.append('expected-final-step-not-observed-on-progress-member')
        issues = list(dict.fromkeys(issues + state['sticky_issues']))
        completed = all_exited and progress_verified and not issues
        state['sequence'] += 1
        result = {'schema_version': 1, 'group_hash': scope, 'task': group['task'], 'context': group['context'],
                  'context_epoch': group['context_epoch'], 'group_attempt': group['group_attempt'],
                  'sequence': state['sequence'], 'checked_at': now, 'members': summaries,
                  'progress_member': group['progress_member'], 'progress_step': progress.get('step'),
                  'completion_verified': completed, 'all_members_observed_healthy': not issues,
                  'status': 'attention' if issues else ('completed' if completed else 'observing'), 'issues': issues,
                  'limits': ['designated progress watcher still evaluates startup/stall/loss/performance',
                             'wrapper audit does not enumerate every torchrun worker or assert device health',
                             'completion verifies group exit and final step, not checkpoint correctness or stage loss acceptance',
                             'collector/aggregator scheduling and independent sentinel deployment remain caller responsibilities']}
        result['sha256'] = fingerprint(result)
        write_json(root / 'observations' / (str(state['sequence']).zfill(12) + '-' + result['sha256'] + '.json'), result)
        state['sticky_issues'] = list(dict.fromkeys(state['sticky_issues']))
        write_json(path, state)
        if output_path is not None:
            write_json(output_path, result)
        return result
