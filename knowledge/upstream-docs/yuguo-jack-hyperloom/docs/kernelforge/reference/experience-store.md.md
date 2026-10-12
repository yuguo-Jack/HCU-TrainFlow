---
id: doc-yuguo-jack-hyperloom-1cc868b83915a5ec2e17
title: yuguo-Jack/Hyperloom / docs/kernelforge/reference/experience-store.md
engine: hyperloom
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: yuguo-Jack/Hyperloom
commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
path: docs/kernelforge/reference/experience-store.md
raw_sha256: dec3a2129acc11d58c4d7961378f57ed7138d5a29c3788ffdbee8ddd5106945a
sources: []
generated_body_sha256: fdedb416d42eedb301cde2be67699cb71d1070633fe8c9a6e71ad129c217cac8
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/kernelforge/reference/experience-store.md

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/kernelforge/reference/experience-store.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
myst:
  html_meta:
    "description": "Configure KernelForge experience storage for durable local files or remote GBrain."
---

# Knowledge stores

KernelForge persists forge-loop experience pages and `optimizes` links through
one local/remote store contract. This store is separate from the packaged
`local_knowledge` prompt tree; `local_knowledge` stays read-only in its existing
location and is never copied into the experience store.

`kernelforge gemm-tune` has no knowledge base: every run tunes or
authors from scratch and writes only its own output directory.

## Environment contract

| Variable | Default | Meaning |
|:--|:--|:--|
| `KNOWLEDGE_STORE_MODE` | `local` | Exactly `local` or `remote`. Other values fail validation. |
| `KNOWLEDGE_LOCAL_ROOT` | See below | Shared root for local knowledge data. |
| `GBRAIN_BASE_URL` | none | GBrain base URL; required in `remote` mode. |
| `GBRAIN_TOKEN` | none | GBrain bearer token; required in `remote` mode. |

When `KNOWLEDGE_LOCAL_ROOT` is unset, its default is
`$USER_DATA_PATH/knowledge` if `USER_DATA_PATH` is present, otherwise
`~/.cache/hyperloom/knowledge`.

`local` mode never constructs a GBrain client and ignores ambient
`GBRAIN_BASE_URL` and `GBRAIN_TOKEN` values. In `remote` mode, both GBrain values
must be non-empty; validation happens before `forge-loop` starts.

## Local layout

KernelForge stores experiences below:

```text
$KNOWLEDGE_LOCAL_ROOT/
└── kernelforge/
    └── experiences/
        ├── .store.lock
        ├── pages/
        │   └── kernelforge-exp/
        │       ├── <operator>__<framework>__<backend>.md
        │       └── <operator>__<framework>__<backend>/
        │           └── <experience-id>.md
        └── links/
            └── backlinks/
                └── kernelforge-exp/<operator>__<framework>__<backend>.json
```

Page slugs and page content remain the existing
`kernelforge-exp/<op>...` format. Backlink JSON preserves the existing
`solution -> kernel` `optimizes` semantics. Writes use same-directory temporary
files, fsync, atomic replacement, and a process lock, so a persistent root is
safe to reuse across runs and processes.
