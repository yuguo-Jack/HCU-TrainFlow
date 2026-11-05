---
id: doc-pytorch-torchtitan-ab8ade6da5cee7392ba9
title: pytorch/torchtitan / torchtitan_recipes/decision/README.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
path: torchtitan_recipes/decision/README.md
raw_sha256: f1dffdb44198a10924e84625272bd7cd65a07b5d528b23c12beba17dd83c5707
sources: []
generated_body_sha256: 5c08e26d0a4f79fae9c23642c4cc5b0911d5a0cf9dfb2353363db2e8ec73cab3
source_state: current-scan
---

# pytorch/torchtitan / torchtitan_recipes/decision/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/decision/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Typed-decision (Jev-style) fine-tuning

Fine-tune Qwen3-1.7B-Base to answer typed questions about a state without
generating text, following TypeSafe's Jev: `choice` (categorical), `noul`
(yes/no), and `score` (ordered scale). Each question gets one probability per
option from a single forward pass, read at the answer slot:

```text
Context:
<state>

Question (choice): Which team should handle this ticket?
Options:
A) Payments and refunds
B) Login and account access
C) Something else
Answer:  --one forward pass--> next-token logits
                               keep only " A", " B", " C"
                               softmax(logits / temperature)
                               -> {payments: 0.91, account: 0.06, other: 0.03}
```

Training supervises only the answer-letter token. Each question is packed as
a separate document, so questions cannot attend to each other.

## Run

```bash
python scripts/download_hf_assets.py --repo_id Qwen/Qwen3-1.7B-Base --assets tokenizer safetensors config
python -m torchtitan_recipes.decision.prepare_data
python -m torchtitan_recipes.decision.evaluate --hf-assets ./assets/hf/Qwen3-1.7B-Base
NGPU=2 MODULE=torchtitan_recipes.decision.qwen3 CONFIG=qwen3_1_7b_decision ./run_train.sh --output-dir outputs/decision
python -m torchtitan_recipes.decision.evaluate --hf-assets ./assets/hf/Qwen3-1.7B-Base --checkpoint outputs/decision/checkpoint/exports/step-600
```

`prepare_data` downloads [`avbiswas/bev-decision-150K`](https://huggingface.co/datasets/avbiswas/bev-decision-150K)
and writes one prompt per question to `./assets/hf/bev-decision-150K/`
(about 247K training questions). A seeded shuffle randomizes `choice` options
and `noul` Yes/No order in every split; `score` levels stay ordered. Training
is a 600-step full fine-tune.

Supported parallelism: FSDP by default; pass a `ParallelismConfig` to
`qwen3_1_7b_decision` from your own config function for tensor parallelism
(with loss parallel) or context parallelism (Ulysses varlen attention). Pipeline
parallelism is unsupported because Qwen3-1.7B ties its embedding and output
weights.

Rows average ~180 tokens with one supervised token. `AnswerTokenLoss` applies
`lm_head` only at supervised positions; the recipe also uses a single data
reader, prefetches 16 microbatches, disables activation recomputation, and
caps documents per microbatch at 256. On one GB300 these raise throughput
from 68.7K to 105.5K tokens/s (mean of steps 21-80 of an 80-step run) over the
same recipe with `ChunkedLossWrapper`, default recompute and data loading, and
512 documents per microbatch.

## Results

1,500 test questions; temperature fitted on questions from 250 other test
states. Training, calibration, and evaluation share no states. Pairs are
base -> fine-tuned.

| type | n | accuracy (higher is better) | Brier (lower is better) | ECE (lower is better) | answered at 5% error (higher is better) |
|---|---|---|---|---|---|
| all | 1500 | 0.611 -> 0.873 | 0.491 -> 0.177 | 0.062 -> 0.016 | 0.10 -> 0.79 |
| choice | 576 | 0.552 -> 0.889 | 0.528 -> 0.158 | 0.053 -> 0.019 | 0.25 -> 0.86 |
| noul | 609 | 0.783 -> 0.933 | 0.352 -> 0.097 | 0.103 -> 0.015 | 0.00 -> 0.96 |
| score | 315 | 0.384 -> 0.727 | 0.690 -> 0.369 | 0.086 -> 0.065 | 0.00 -> 0.34 |

"Answered" is the largest fraction of questions, taken most-confident first,
whose error rate stays at or below 5%. These are in-distribution results: test
questions come from the same source datasets as training.
