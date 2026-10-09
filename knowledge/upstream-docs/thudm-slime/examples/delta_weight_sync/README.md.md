---
id: doc-thudm-slime-570fe7a2fe8147dfeda1
title: THUDM/slime / examples/delta_weight_sync/README.md
engine: slime
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: THUDM/slime
commit: 0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e
path: examples/delta_weight_sync/README.md
raw_sha256: fae8b1aa499a4b4ff709671e1ebda3a7bd3fe89b623afe9b1ce63896c0cd80aa
sources: []
generated_body_sha256: a4f2b5b41666a9fae39df12a0a6de2e361baa2b98ee4d195b2b95a790ad6fcb2
source_state: current-scan
---

# THUDM/slime / examples/delta_weight_sync/README.md

[Original at fixed commit](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/delta_weight_sync/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Delta Weight Sync

Non-colocated weight sync that ships only the **changed bytes** between two syncs instead of a
full checkpoint, for training/inference disaggregation across clusters or datacenters. The
trainer publishes per-tensor deltas to a shared filesystem as a canonical HF checkpoint
directory; each engine's `/pull_weights` applies them into a host-local checkpoint on every
host it spans, and the engines reload through the ordinary `update_weights_from_disk` path —
slime only ever talks to one endpoint per engine.

See [Delta Weight Sync](https://github.com/THUDM/slime/blob/main/docs/en/advanced/delta-weight-sync.md) for the full mechanism,
encodings, integrity checks, and shared-filesystem visibility hooks.

## Try it

`run-glm4.7-30B-A3B-delta.sh` runs the disk delta path on GLM-4.7-Flash, non-colocated across a
2-node (16-GPU) Ray cluster. See its header for prerequisites.

## Minimal flags

Add to a non-colocated training run (the trainer and engines only need to share the filesystem
at `--update-weight-disk-dir`):

```bash
--update-weight-mode delta \
--update-weight-transport disk \
--update-weight-disk-dir   /shared/fs/delta-updates \
--update-weight-local-checkpoint-dir /local/nvme/rollout-ckpt \
--update-weight-delta-encoding xor \
--update-weight-delta-checksum xxh3-128
```

- `--update-weight-disk-dir` — shared directory the trainer writes deltas to and the hosts read.
- `--update-weight-local-checkpoint-dir` — host-local full HF checkpoint the delta patches in
  place; materialized from the engine's model path on the first `/pull_weights`.
- `--update-weight-delta-encoding` — `xor` (smallest/fastest) or `overwrite` (idempotent).
- `--update-weight-delta-checksum` — `xxh3-128` (default), `blake3`, or `adler32`.

For object-store-backed volumes that need an explicit commit/refresh to make writes visible
across hosts, supply `--custom-update-weight-post-write-path` (trainer side) /
`--sglang-custom-pull-weights-pre-read-hook` (engine side) — no vendor-specific code lives in slime
or sglang; see the doc.