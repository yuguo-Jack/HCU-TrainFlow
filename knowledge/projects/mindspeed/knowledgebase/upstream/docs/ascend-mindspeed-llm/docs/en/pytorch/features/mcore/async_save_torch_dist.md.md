---
id: doc-ascend-mindspeed-llm-085655ae647a857f6208
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/async_save_torch_dist.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
path: docs/en/pytorch/features/mcore/async_save_torch_dist.md
raw_sha256: a3f41ceaa3efcd515379dbfb8ceabbd8845dbdb8fa254edef41379a9f052c994
sources: []
generated_body_sha256: f64b3068d7fe930364b83bfabaef286340ec28cd84c111f8136608ae86c62cbf
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/async_save_torch_dist.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/pytorch/features/mcore/async_save_torch_dist.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Async Save Torch Dist

## Use Cases

### Issue Description

In large-scale training, saving a checkpoint often causes a noticeable training pause.
If every save blocks the main training flow, throughput suffers.

MindSpeed LLM builds on the distributed checkpoint semantics of Megatron and provides asynchronous saving for the `torch_dist` format. The main flow only submits the saving request, while the backend writes the shards to the drive. Therefore, training can continue.

### Feature Overview

\[Core Capability\]

This feature provides asynchronous saving for `torch_dist` checkpoints:

- The main training flow only builds and submits the saving request.
- Sharded writes run in the background.
- Training can continue, which reduces checkpoint-related pauses.

\[Saving Format and Saving Mode\]

Currently, checkpoints support only `torch` and `torch_dist`.
Only the `torch_dist` format supports asynchronous saving. The `torch` format supports only synchronous saving, which blocks the main training flow. The `torch_dist` format also supports synchronous saving.
Therefore, the `torch_dist` format supports two save modes:

- Asynchronous saving: The main flow only builds and submits the saving request, and it does not block the main training flow.
- Synchronous saving: The main flow continues with later training steps only after the save completes.

Asynchronous saving increases CPU usage. For LLMs and frequent saves, synchronous saving is recommended.

\[Asynchronous Saving Flow\]

After you enable `--async-save`:

- The save phase submits asynchronous requests through `schedule_async_save`.
- The checkpoint tracker update and the `one_logger` success event run in the `finalize` callback.
- When training ends, `maybe_finalize_async_save(blocking=True, terminate=True)` runs once to complete any unfinished requests.

## Usage Constraints

\[Asynchronous Saving Format Constraints\]

- `--async-save` supports only checkpoints whose final format is `torch_dist`.
- If the format is legacy `torch` or any other distributed format, the unsupported-mode check triggers.

\[Usage Scenario Constraints\]
This feature applies only to pretraining:

- It supports asynchronously saving weights in `torch_dist` format.
- You can use the saved weights directly for inference, or load them and continue pretraining.
- It does not yet support LoRA, fine-tuning, SFT, or other downstream tasks.
