---
id: doc-vllm-project-vllm-4de21f97fa7cea73095f
title: vllm-project/vllm / docs/training/prompt_token_id_logprobs.md
engine: vllm
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: vllm-project/vllm
commit: f0a5f111f205b5c73bb34fbd41f8f0d9936b543f
path: docs/training/prompt_token_id_logprobs.md
raw_sha256: 14a1d07ceb9c9101752b9a2e5f79a7bdaa787422ad1d644051755f9f6e0666c8
sources: []
generated_body_sha256: aad689ee644eb6f3ad02e47c5e6f7d51b2fa82042cd27d89e24d55f34d1ffe5a
source_state: current-scan
---

# vllm-project/vllm / docs/training/prompt_token_id_logprobs.md

[Original at fixed commit](https://github.com/vllm-project/vllm/blob/f0a5f111f205b5c73bb34fbd41f8f0d9936b543f/docs/training/prompt_token_id_logprobs.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Prompt Token ID Logprobs (Teacher Scoring)

In on-policy distillation, the student records its top-K candidate tokens at
every response position, and the teacher provides the log probabilities of
exactly those candidates as the distillation target. The caller passes one
candidate list per scored row as `prompt_logprob_token_ids`; the teacher runs a
single prefill over the prompt plus response and gathers their log
probabilities on the GPU, starting from `prompt_logprob_start` (typically the
prompt length minus one, so only response positions are scored). The result is
a `[rows, K]` matrix whose row `i` scores prompt token
`prompt_logprob_start + i + 1` and whose columns follow that row's candidate
order, so it lines up position by position with the student's top-K.

## Quick start

```python
from vllm import LLM, SamplingParams
from vllm.inputs import TokensPrompt

llm = LLM(model)
output = llm.generate(
    TokensPrompt(prompt_token_ids=prompt_ids + response_ids),
    SamplingParams(
        max_tokens=1,
        prompt_logprob_token_ids=student_topk_ids,  # [len(response_ids), K]
        prompt_logprob_start=len(prompt_ids) - 1,
    ),
)
scores = output[0].prompt_token_id_logprobs
# scores.shape == (len(response_ids), K)
# scores[i, j] = log p(student_topk_ids[i][j] | prompt_ids + response_ids[:i])
```

The same parameters are accepted by the `/inference/v1/generate` HTTP endpoint
(Python and Rust frontends), which returns the matrix as a base64-encoded
`.npy` float32 array:

```python
import base64, io
import numpy as np

scores = np.load(io.BytesIO(base64.b64decode(response["prompt_token_id_logprobs"])))
```

`prompt_logprob_token_ids` is an integer array or a list of lists with exactly
`prompt_len - 1 - prompt_logprob_start` rows; shorter rows are padded with `-1`,
and every `-1` entry scores `-inf`. Pass an `int32` NumPy array, such as the
student's top-K IDs, which is sent to the engine without conversion; nested
lists of Python ints are much slower to copy and serialize. With a logits
`--logprobs-mode`, the matrix holds logits instead of log probabilities.

## Requirements

- The V2 model runner (`VLLM_USE_V2_MODEL_RUNNER=1`).
- The longest row at most `--max-logprobs` candidates.
- No `--kv-sharing-fast-prefill`.

The request skips reading the prefix cache (local and KV connector), since
cached rows have no logits to score.

## Limitations

- Non-streaming only; `stream=true` requests are rejected.
- Not exposed through the OpenAI-compatible endpoints.
- If a prefill starts past the first scored row (e.g. `skip_reading_prefix_cache=False`
  with a cache hit), the result is `None` rather than a partial matrix.