"""Incremental shared Wiki versions; logical generations do not copy full FTS."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import zlib

from .core import FlowError, atomic_write, child, digest, fingerprint, read_json, utc, write_json

LAYOUT = 'shared-v1'
PIPELINE = 2


def enabled(project):
    from .source_evidence import policy
    return policy(project).get('index_layout') == LAYOUT


def _signature(path):
    # Windows ctime is creation time; copy tools may preserve mtime and size.
    # Hash the now-small selected corpus, while reusing parsing and FTS versions.
    return json.dumps([PIPELINE, digest(path.read_bytes())])


def _paths(root):
    paths = sorted(root.rglob('*.md'))
    if any(not p.resolve().is_relative_to(root) for p in paths):
        raise FlowError('Wiki source link escapes knowledge directory')
    return paths


def _schema(db):
    db.executescript('''
      CREATE TABLE IF NOT EXISTS versions(
        version INTEGER PRIMARY KEY, key TEXT UNIQUE, id TEXT, title TEXT,
        path TEXT, body TEXT, metadata TEXT, sha256 TEXT, original BLOB);
      CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(title,body,content='');
      CREATE TABLE IF NOT EXISTS generations(generation TEXT PRIMARY KEY,root TEXT,created_at TEXT,pages INTEGER);
      CREATE TABLE IF NOT EXISTS members(generation TEXT,id TEXT,version INTEGER,
        PRIMARY KEY(generation,id));
      CREATE INDEX IF NOT EXISTS member_version ON members(version,generation);
      CREATE TABLE IF NOT EXISTS file_cache(root TEXT,path TEXT,signature TEXT,version INTEGER,sha256 TEXT,
        PRIMARY KEY(root,path));
    ''')
    if 'original' not in {r[1] for r in db.execute('PRAGMA table_info(versions)')}:
        db.execute('ALTER TABLE versions ADD COLUMN original BLOB')


def index(store, project):
    from .wiki import parse_text, terms
    root = Path(project).resolve() / 'knowledge'
    if not root.is_dir():
        raise FlowError('Project knowledge directory not found')
    directory = store.root / 'wiki'
    directory.mkdir(parents=True, exist_ok=True)
    database = directory / 'shared.sqlite3'
    # A separate SQLite writer lease spans both database commit and active.json.
    # Readers keep their old committed generation throughout an index build.
    with closing(sqlite3.connect(directory / 'build-lock.sqlite3', timeout=60)) as lease:
        lease.execute('BEGIN IMMEDIATE')
        try:
            with closing(sqlite3.connect(database, timeout=60)) as db:
                db.execute('PRAGMA journal_mode=WAL')
                _schema(db)
                db.execute('BEGIN IMMEDIATE')
                try:
                    paths = _paths(root)
                    stamps = {p.relative_to(root).as_posix(): _signature(p) for p in paths}
                    cached = {r[0]: r[1:] for r in db.execute(
                        'SELECT path,signature,version,sha256 FROM file_cache WHERE root=?', (str(root),))}
                    members = []
                    identities = set()
                    hashes = {}
                    parsed = 0
                    for path in paths:
                        name = path.relative_to(root).as_posix()
                        old = cached.get(name)
                        row = None
                        if old and old[0] == stamps[name]:
                            if old[1] is None:
                                continue
                            row = db.execute('SELECT version,id,sha256 FROM versions WHERE version=?', (old[1],)).fetchone()
                        if row is None:
                            raw = path.read_bytes()
                            sha = digest(raw)
                            if json.dumps([PIPELINE, sha]) != stamps[name]:
                                raise FlowError('Wiki inputs changed during indexing; retry against a stable checkout')
                            meta, body = parse_text(raw.decode('utf-8-sig'))
                            parsed += 1
                            if not isinstance(meta, dict):
                                raise FlowError('Wiki metadata must be a mapping')
                            if meta.get('visibility', 'public') != 'public':
                                db.execute('INSERT OR REPLACE INTO file_cache VALUES(?,?,?,?,?)',
                                           (str(root), name, stamps[name], None, sha))
                                continue
                            pid = meta.get('id', name)
                            title = meta.get('title', next((x[2:] for x in body.splitlines() if x.startswith('# ')), path.stem))
                            key = fingerprint([PIPELINE, name, sha])
                            row = db.execute('SELECT version,id,sha256 FROM versions WHERE key=?', (key,)).fetchone()
                            if row is None:
                                cursor = db.execute('INSERT INTO versions(key,id,title,path,body,metadata,sha256,original) VALUES(?,?,?,?,?,?,?,?)',
                                    (key, pid, title, name, body, json.dumps(meta, ensure_ascii=False), sha, zlib.compress(raw)))
                                version = cursor.lastrowid
                                db.execute('INSERT INTO fts(rowid,title,body) VALUES(?,?,?)',
                                           (version, ' '.join(terms(title)), ' '.join(terms(body))))
                                row = (version, pid, sha)
                            db.execute('INSERT OR REPLACE INTO file_cache VALUES(?,?,?,?,?)',
                                       (str(root), name, stamps[name], row[0], sha))
                        version, pid, sha = row
                        if pid in identities:
                            raise FlowError('Duplicate Wiki page ID')
                        identities.add(pid)
                        members.append((pid, version))
                        hashes[name] = sha
                    generation = fingerprint({'layout': LAYOUT, 'pipeline': PIPELINE, 'root': str(root), 'pages': hashes})
                    if [p.relative_to(root).as_posix() for p in _paths(root)] != list(stamps) or any(
                            _signature(root / name) != stamp for name, stamp in stamps.items()):
                        raise FlowError('Wiki inputs changed during indexing; retry against a stable checkout')
                    prior = db.execute('SELECT created_at,pages FROM generations WHERE generation=?', (generation,)).fetchone()
                    created = prior[0] if prior else utc()
                    if not prior:
                        db.execute('INSERT INTO generations VALUES(?,?,?,?)', (generation, str(root), created, len(members)))
                        db.executemany('INSERT INTO members VALUES(?,?,?)', [(generation, pid, version) for pid, version in members])
                    db.commit()
                except BaseException:
                    db.rollback()
                    raise
            state = {'generation': generation, 'path': str(database), 'root': str(root),
                     'pages': len(members), 'created_at': created, 'index_layout': LAYOUT}
            active_path = directory / 'active.json'
            active = read_json(active_path) if active_path.is_file() else {}
            if active != state:
                write_json(active_path, state)
            return {**state, 'unchanged': active == state, 'pages_parsed': parsed}
        finally:
            lease.rollback()


def _open(store, generation=None, state=None):
    path = Path(state['path']) if state else store.root / 'wiki/shared.sqlite3'
    db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('BEGIN')
    generation = generation or state['generation']
    row = db.execute('SELECT * FROM generations WHERE generation=?', (generation,)).fetchone()
    if row is None:
        db.close()
        raise FlowError('Unknown Wiki generation')
    return db, dict(row)


def _value(row, root, store=None):
    result = dict(row)
    result.pop('version', None)
    result.pop('key', None)
    original = result.pop('original', None)
    result['metadata'] = json.loads(result['metadata'])
    path = child(root, result['path'])
    result['path'] = str(path)
    result['review_state'] = ('indexed-snapshot' if path.is_file() and digest(path.read_bytes()) == result['sha256']
                              else 'local-page-changed; reindex')
    if store and result['review_state'] != 'indexed-snapshot' and original is not None:
        raw = zlib.decompress(original)
        if digest(raw) != result['sha256']:
            raise FlowError('Indexed original SHA-256 mismatch')
        target = child(store.root, f'wiki/views/{result["sha256"]}/{path.name}')
        if target.exists() and digest(target.read_bytes()) != result['sha256']:
            import uuid
            target = target.with_name(uuid.uuid4().hex + '-' + target.name)
        if not target.exists():
            atomic_write(target, raw)
        result.update(path=str(target), original_path=str(path), review_state='indexed-history', original_available=True)
    return result


def search(store, state, query, limit, engine=None, stage=None, kind=None):
    from .wiki import terms
    tokens = terms(query)
    if not tokens:
        return {'results': [], 'generation': state['generation']}
    conditions = ['fts MATCH ?', 'm.generation=?']
    args = [' OR '.join('"' + x.replace('"', '""') + '"' for x in tokens[:50]), state['generation']]
    if engine:
        conditions.append("json_extract(v.metadata,'$.engine')=?")
        args.append(engine)
    if stage:
        conditions.append("EXISTS(SELECT 1 FROM json_each(json_extract(v.metadata,'$.stages')) WHERE value=?)")
        args.append(stage)
    if kind:
        conditions.append("coalesce(json_extract(v.metadata,'$.kind'),'authored')=?")
        args.append(kind)
    db, snapshot = _open(store, state=state)
    with closing(db):
        rows = db.execute("SELECT v.*,bm25(fts,4,1) * CASE json_extract(v.metadata,'$.kind') "
                          "WHEN 'source-map' THEN 0.05 WHEN 'source-document' THEN 0.6 WHEN 'source-pr' THEN 0.8 ELSE 1 END score "
                          'FROM fts JOIN versions v ON v.version=fts.rowid JOIN members m ON m.version=v.version WHERE '
                          + ' AND '.join(conditions) + ' ORDER BY score LIMIT ?', args + [limit]).fetchall()
    results = []
    for row in rows:
        value = _value(row, snapshot['root'])
        value['excerpt'] = value.pop('body')[:1600]
        results.append(value)
    return {'results': results, 'generation': state['generation'],
            'instruction': 'Read the relevant page or original PR URL; inspect fixed code when the conclusion requires it. No source refresh is performed.'}


def read_page(store, identity, generation=None, state=None):
    from .source_evidence import historical_page
    db, snapshot = _open(store, generation, state)
    with closing(db):
        row = db.execute('SELECT v.* FROM versions v JOIN members m ON m.version=v.version WHERE m.generation=? AND m.id=?',
                         (snapshot['generation'], identity)).fetchone()
    if row is None:
        result = historical_page(Path(snapshot['root']).parent, identity)
    else:
        result = _value(row, snapshot['root'], store)
    return {**result, 'generation': snapshot['generation']}
