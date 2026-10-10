"""Retain direct human chat input without impersonating edits to GUIDANCE.md.

The caller must supply actual human text and a source reference. Attribution is
an audit trail, not authentication or permission; disposition remains explicit.
"""
from .core import FlowError, context_epoch, utc
from .flow import get_flow, retain


def record(store, tid, value):
    if (not isinstance(value, dict) or set(value) != {'text', 'source', 'author'}
            or any(not isinstance(v, str) or not v.strip() for v in value.values())):
        raise FlowError('Chat guidance requires actual text, source reference and author')
    if len(value['text'].encode('utf8')) > 1024 * 1024:
        raise FlowError('Guidance exceeds 1 MiB')
    task = store.task(tid)
    sha = retain(store, {'kind': 'human-chat-guidance', 'context': task['context'],
                         'context_epoch': task['context_epoch'], **value})
    with store.db() as db:
        db.execute('BEGIN IMMEDIATE')
        current = db.execute('SELECT context,state FROM tasks WHERE id=?', (tid,)).fetchone()
        if not get_flow(db, tid) or current['state'] in {'completed', 'cancelled'}:
            raise FlowError('Chat guidance requires an active flow')
        if current['context'] != task['context'] or context_epoch(db, tid) != task['context_epoch']:
            raise FlowError('Task context changed while retaining guidance')
        if db.execute('SELECT 1 FROM flow_guidance WHERE task=? AND id=?', (tid, sha)).fetchone():
            return {'new': 0, 'guidance': sha}
        db.execute('INSERT INTO flow_guidance VALUES(?,?,?,?,?,?)',
                   (tid, sha, task['context'], 'pending', '', utc()))
        db.execute("UPDATE flow_rounds SET status='superseded' WHERE task=? AND status IN ('submitted','accepted')", (tid,))
        event = store.event(db, tid, 'human-guidance-received',
                            {'guidance': sha, 'context': task['context'],
                             'origin': 'chat', 'source': value['source']}, channel='agent')
    return {'new': 1, 'guidance': sha, 'event_id': event}
