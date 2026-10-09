"""Versioned human questions; answering never grants execution authorization."""
import contextlib
import json
import os
import re
import time

from .core import FlowError, atomic_write, child, context_epoch, digest, fingerprint, safe_id, utc

TEMPLATE = '''# 问题与回答

每个问题可用二级标题，或单独一行 Q1：问题；保留不同编号，修改正文会登记为新版本。
Agent 默认每 5 分钟采集，在线后在问题下面回答。请勿修改受管回答块；追问可写在块外或新建问题。
这里用于问答，不自动授权执行命令、修改参数或重启训练；调整工作安排请写 GUIDANCE.md。

在下面另起一行，以 `## Q1：你的问题` 开头即可；下一问用 Q2。
示例仅供参考，不要把问题包在代码块中：

> ## Q1：这里写问题
> 这里可以补充背景、链接或代码。
'''
BEGIN = re.compile(r'<!-- trainflow-answer id=([a-f0-9]{64}) -->\r?\n')
END = '<!-- /trainflow-answer -->'


def paths(store, tid):
    directory = child(store.root, 'collaboration/' + safe_id(tid))
    return directory, child(directory, 'QUESTIONS.md')


@contextlib.contextmanager
def writer_lock(directory):
    """Serialize cooperating scanners/answer writers, not arbitrary editors."""
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'questions.lock').open('a+b') as stream:
        if os.name == 'nt':
            import msvcrt
            if stream.seek(0, 2) == 0:
                stream.write(b'0'); stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise FlowError('Questions file has an active scanner/writer; retry without removing its lock') from exc
        else:
            import fcntl
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise FlowError('Questions file has an active scanner/writer; retry without removing its lock') from exc
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0); msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def ensure(store, tid):
    directory, path = paths(store, tid)
    with writer_lock(directory):
        if not path.exists():
            with store.db() as db:
                seen = db.execute('SELECT 1 FROM file_question_scans WHERE task=?', (tid,)).fetchone()
            if seen:
                raise FlowError('QUESTIONS.md is missing; restore it, do not silently recreate user content')
            with path.open('x', encoding='utf-8', newline='') as stream:
                stream.write(TEMPLATE)
    return path


def _read(path):
    if path.is_symlink() or not path.is_file():
        raise FlowError('QUESTIONS.md must be an existing regular file')
    data = path.read_bytes()
    if len(data) > 1024 * 1024:
        raise FlowError('QUESTIONS.md exceeds 1 MiB; retain large material separately')
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise FlowError('QUESTIONS.md must be UTF-8') from exc
    return data, text


def parse(text, known):
    """Keep user bytes untouched; only known exact managed blocks are hidden."""
    headings, blocks, fence = [], [], None
    lines = text.splitlines(keepends=True)
    offset, index = 0, 0
    while index < len(lines):
        line = lines[index]
        match = BEGIN.fullmatch(line)
        if match and fence is None:
            begin = offset
            collected = line
            index += 1; offset += len(line)
            while index < len(lines) and lines[index].rstrip('\r\n') != END:
                collected += lines[index]; offset += len(lines[index]); index += 1
            if index == len(lines):
                raise FlowError('Unclosed managed answer block; preserve and repair it before answering')
            collected += lines[index]; offset += len(lines[index]); index += 1
            if known.get(match[1]) != collected or any(item[2] == match[1] for item in blocks):
                raise FlowError('Unknown or edited managed answer block; retained original answer must be reconciled')
            blocks.append((begin, offset, match[1]))
            continue
        stripped = line.lstrip(' ')
        code = re.match(r'(`{3,}|~{3,})', stripped) if len(line)-len(stripped) <= 3 else None
        if code:
            token = code[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None:
            if 'trainflow-answer' in line:
                raise FlowError('Malformed reserved answer marker')
            match = re.match(r'^##[ \t]+(.+?)\s*$', line.rstrip('\r\n'))
            if match:
                headings.append((offset, match[1]))
            elif re.match(r'^Q[0-9][A-Za-z0-9._-]*[ \t]*[:：][ \t]*\S', line):
                # Plain numbered questions are common in an editable notebook.
                # Recognize only unindented explicit IDs outside fences/quotes;
                # keep the user's bytes and the same version/answer safeguards.
                headings.append((offset, line.rstrip('\r\n')))
        offset += len(line); index += 1
    if fence is not None:
        raise FlowError('Unclosed Markdown code fence; finish it before question collection')
    if blocks and (not headings or blocks[0][0] < headings[0][0]):
        raise FlowError('Managed answer block is outside a question; reconcile its original location')
    result, seen = [], set()
    for number, (start, title) in enumerate(headings):
        end = headings[number+1][0] if number+1 < len(headings) else len(text)
        raw, position, answers = '', start, []
        for begin, finish, aid in blocks:
            if start <= begin < end:
                raw += text[position:begin]; position = finish; answers.append(aid)
        raw += text[position:end]
        explicit = re.match(r'^(Q[0-9][A-Za-z0-9._-]*)(?:\s*[:：]\s*|\s+)', title)
        qid = explicit[1] if explicit else 'q-' + digest(title.encode())[:20]
        if qid in seen:
            raise FlowError('Duplicate question heading/ID; use distinct Q1, Q2 identifiers')
        safe_id(qid); seen.add(qid)
        canonical = raw.strip()
        result.append({'id': qid, 'title': title, 'text': canonical,
                       'version': digest(canonical.encode()), 'start': start, 'end': end, 'answers': answers})
    return result


def _known(store, tid):
    with store.db() as db:
        rows = db.execute("SELECT id,payload FROM file_question_answers WHERE task=? AND status IN ('prepared','applied')", (tid,))
        return {row['id']: json.loads(row['payload'])['block'] for row in rows}


def scan(store, tid, *, force=False):
    task = store.task(tid)
    scope = fingerprint({'context': task['context'], 'epoch': task['context_epoch']})
    with store.db() as db:
        flow = db.execute('SELECT plan FROM flows WHERE task=?', (tid,)).fetchone()
        prior = db.execute('SELECT * FROM file_question_scans WHERE task=?', (tid,)).fetchone()
    if not flow:
        return {'new': 0, 'scan': 'no-flow'}
    now = time.time()
    if not force and prior and prior['scope'] == scope and 0 <= now-prior['checked_at'] < json.loads(flow['plan'])['poll_seconds']:
        return {'new': 0, 'scan': 'not-due'}
    directory, path = paths(store, tid)
    file_hash = None
    try:
        ensure(store, tid)
        with writer_lock(directory):
            data, text = _read(path)
            file_hash = store.put(data)
            questions = parse(text, _known(store, tid))
            with store.db() as db:
                db.execute('BEGIN IMMEDIATE')
                current = db.execute('SELECT context FROM tasks WHERE id=?', (tid,)).fetchone()
                if current['context'] != task['context'] or context_epoch(db, tid) != task['context_epoch']:
                    raise FlowError('Question context changed during scan; retry')
                db.execute("UPDATE file_question_versions SET status='superseded' WHERE task=? AND status='pending'", (tid,))
                db.execute('DELETE FROM file_question_current WHERE task=?', (tid,))
                new = 0
                for question in questions:
                    key = (tid, question['id'], question['version'], scope)
                    old = db.execute('SELECT status FROM file_question_versions WHERE task=? AND id=? AND version=? AND scope=?', key).fetchone()
                    payload = {k: question[k] for k in ('id','title','text','version')}
                    payload.update(context=task['context'], context_epoch=task['context_epoch'], file_hash=file_hash)
                    if not old:
                        db.execute("INSERT INTO file_question_versions VALUES(?,?,?,?,?,'pending',NULL,?)", (*key, json.dumps(payload, ensure_ascii=False), utc()))
                        store.event(db, tid, 'user-file-question-received', {**payload, 'authorization': False}, channel='agent')
                        new += 1
                    elif old['status'] != 'answered':
                        db.execute("UPDATE file_question_versions SET status='pending' WHERE task=? AND id=? AND version=? AND scope=?", key)
                    for aid in question['answers']:
                        saved = db.execute('SELECT payload FROM file_question_answers WHERE task=? AND id=?', (tid, aid)).fetchone()
                        saved = json.loads(saved['payload'])
                        if (saved['question'], saved['version'], saved['scope']) == (question['id'], question['version'], scope):
                            # Recover a crash after the file replacement but
                            # before the completion transaction. Exact blocks
                            # have already been checked against retained data.
                            db.execute("UPDATE file_question_answers SET status='applied' WHERE task=? AND id=?", (tid, aid))
                            db.execute("UPDATE file_question_versions SET status='answered',answer=? WHERE task=? AND id=? AND version=? AND scope=?", (aid, *key))
                            store.event(db, tid, 'user-file-question-answered', {'question': question['id'], 'version': question['version'], 'answer': aid}, event_id=f'file-answer:{tid}:{aid}')
                    db.execute('INSERT INTO file_question_current VALUES(?,?,?,?)', key)
                db.execute('INSERT OR REPLACE INTO file_question_scans VALUES(?,?,?,?,NULL)', (tid, file_hash, now, scope))
            return {'new': new, 'file_hash': file_hash, 'questions': len(questions)}
    except (FlowError, OSError) as exc:
        # An unreadable Q&A file is visible, but never pauses unrelated work.
        error = str(exc)
        try:
            if file_hash is None and path.is_file() and path.stat().st_size <= 1024 * 1024:
                file_hash = store.put(path.read_bytes())
        except OSError:
            pass
        with store.db() as db:
            previous = db.execute('SELECT hash,error FROM file_question_scans WHERE task=?', (tid,)).fetchone()
            if not previous or (previous['hash'], previous['error']) != (file_hash, error):
                store.event(db, tid, 'user-file-question-scan-failed', {'file_hash': file_hash, 'error': error}, channel='agent')
            db.execute('INSERT OR REPLACE INTO file_question_scans VALUES(?,?,?,?,?)', (tid, file_hash, now, scope, error))
        return {'new': 0, 'scan': 'attention', 'error': error, 'file_hash': file_hash}


def state(store, tid):
    task = store.task(tid)
    scope = fingerprint({'context': task['context'], 'epoch': task['context_epoch']})
    with store.db() as db:
        rows = db.execute('SELECT v.* FROM file_question_current c JOIN file_question_versions v USING(task,id,version,scope) WHERE c.task=? AND c.scope=? ORDER BY v.created,v.id', (tid, scope)).fetchall()
        scanned = db.execute('SELECT * FROM file_question_scans WHERE task=?', (tid,)).fetchone()
    values = [{**json.loads(r['payload']), 'status': r['status'], 'answer': r['answer']} for r in rows]
    return {'path': str(paths(store, tid)[1]), 'file_hash': scanned['hash'] if scanned else None,
            'scan_error': scanned['error'] if scanned else None, 'questions': values,
            'pending': sum(q['status'] == 'pending' for q in values), 'authorization': False}


def _replace_checked(path, expected, data):
    # Optimistic concurrency check; arbitrary editors do not obey our lock.
    # Both versions are retained before this call, enabling conflict recovery.
    if digest(path.read_bytes()) != expected:
        raise FlowError('QUESTIONS.md changed while answering; reread it before retrying')
    atomic_write(path, data)
    if path.read_bytes() != data:
        raise FlowError('QUESTIONS.md changed during answer publication; reconcile retained versions')


def answer(store, tid, qid, version, expected_file, body, *, author):
    safe_id(qid)
    if not isinstance(body, str) or not body.strip() or len(body.encode()) > 128*1024 or 'trainflow-answer' in body:
        raise FlowError('Answer must be nonempty Markdown up to 128 KiB without reserved markers')
    if not isinstance(author, str) or not author.strip() or len(author) > 100:
        raise FlowError('Answer needs a named author')
    task = store.task(tid)
    scope = fingerprint({'context': task['context'], 'epoch': task['context_epoch']})
    request = {'question': qid, 'version': version, 'scope': scope, 'context': task['context'], 'context_epoch': task['context_epoch'], 'author': author, 'body': body, 'expected_file': expected_file}
    request_hash = store.put(json.dumps(request, ensure_ascii=False).encode())
    directory, path = paths(store, tid)
    aid = None
    try:
        with writer_lock(directory):
            data, text = _read(path)
            before = store.put(data)
            questions = parse(text, _known(store, tid))
            question = next((q for q in questions if q['id'] == qid), None)
            if not question or question['version'] != version:
                raise FlowError('Question changed or disappeared; answer the current version')
            with store.db() as db:
                row = db.execute('SELECT * FROM file_question_versions WHERE task=? AND id=? AND version=? AND scope=?', (tid, qid, version, scope)).fetchone()
                attempts = db.execute('SELECT id,payload,status FROM file_question_answers WHERE task=?', (tid,)).fetchall()
            if not row:
                raise FlowError('Scan this question version in the current context before answering')
            for old in attempts:
                old_body = json.loads(old['payload'])
                if (old_body['question'], old_body['version'], old_body['scope']) == (qid, version, scope) and old['status'] in {'prepared', 'applied'}:
                    if old['status'] == 'prepared' and old['id'] not in question['answers']:
                        continue  # Never published; an interrupted proposal is not a delivered answer.
                    if old_body['body'] != body or old_body['author'] != author:
                        raise FlowError('This question version already has an answer; use a follow-up question')
                    if old['id'] in question['answers']:
                        _complete(store, tid, row, old['id'], task)
                        return {'status': 'unchanged', 'answer': old['id'], 'file_hash': before, 'path': str(path)}
            if before != expected_file:
                raise FlowError('Stale QUESTIONS.md file hash; reread all human edits before answering')
            answer_data = {**request, 'before': before, 'created': utc()}
            aid = fingerprint(answer_data)
            block = f'<!-- trainflow-answer id={aid} -->\n### Agent 回答 · {qid} · 问题版本 {version[:12]} · 上下文 {task["context"][:12]}\n\n{body.strip()}\n\n{END}\n'
            answer_data['block'] = block
            after = (text[:question['end']] + '\n' + block + '\n' + text[question['end']:]).encode('utf-8')
            after_hash = store.put(after)
            answer_data['after'] = after_hash
            answer_record = store.put(json.dumps(answer_data, ensure_ascii=False).encode())
            with store.db() as db:
                db.execute('BEGIN IMMEDIATE')
                current = db.execute('SELECT context FROM tasks WHERE id=?', (tid,)).fetchone()
                if current['context'] != task['context'] or context_epoch(db, tid) != task['context_epoch']:
                    raise FlowError('Context changed before answering')
                db.execute("INSERT INTO file_question_answers VALUES(?,?,?,'prepared',?)", (tid, aid, json.dumps(answer_data, ensure_ascii=False), utc()))
                store.event(db, tid, 'user-file-answer-prepared', {'answer': aid, 'answer_record': answer_record, 'request': request_hash, 'before': before, 'after': after_hash})
            _replace_checked(path, before, after)
            _complete(store, tid, row, aid, task, file_hash=after_hash)
            return {'status': 'answered', 'answer': aid, 'file_hash': after_hash, 'path': str(path)}
    except (FlowError, OSError) as exc:
        observed = None
        try:
            observed = store.put(_read(path)[0])
        except (FlowError, OSError):
            pass
        with store.db() as db:
            store.event(db, tid, 'user-file-answer-conflict', {'request': request_hash, 'answer': aid, 'observed_file': observed, 'error': str(exc)})
        raise


def _complete(store, tid, row, aid, task, *, file_hash=None):
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        current = db.execute('SELECT context FROM tasks WHERE id=?', (tid,)).fetchone()
        if current['context'] != task['context'] or context_epoch(db, tid) != task['context_epoch']:
            raise FlowError('Context changed after answer publication; original version retained')
        db.execute("UPDATE file_question_answers SET status='applied' WHERE task=? AND id=?", (tid, aid))
        db.execute("UPDATE file_question_versions SET status='answered',answer=? WHERE task=? AND id=? AND version=? AND scope=?", (aid, tid, row['id'], row['version'], row['scope']))
        if file_hash is not None:
            # Our own verified publication updates the file token without
            # restarting the human polling interval or registering new text.
            db.execute('UPDATE file_question_scans SET hash=?,error=NULL WHERE task=? AND scope=?', (file_hash, tid, row['scope']))
        store.event(db, tid, 'user-file-question-answered', {'question': row['id'], 'version': row['version'], 'answer': aid}, event_id=f'file-answer:{tid}:{aid}')
