---
id: doc-ascend-mindspeed-db899941f03551f866ef
title: Ascend/MindSpeed / docs/en/ops/rms_norm.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/ops/rms_norm.md
raw_sha256: 0a528d51dc39ede14ae62a9583617da11c4387e5d80ca9077f5df40f0a7d39aa
sources: []
generated_body_sha256: ebc222161007129cb73bda947ddd4dff7d5a6dc53c610c6c5de45e71ada4adac
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/ops/rms_norm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/ops/rms_norm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# rms_norm

## Forward API

Inputs:

- x: Required Input, data type float16, bfloat16, float32
- gamma: Required Input, data type float16, bfloat16, float32

Outputs:

- rstd: Intermediate variable, data type float32
- out: Required Output, data type float16, bfloat16, float32

Attributes:

- epsilon: Optional attribute, data type float, defaults to 1e-6.

## Backward API

Inputs:

- dy: Required Input, data type float16, bfloat16, float32
- x: Required Input, data type float16, bfloat16, float32
- rstd: Required Input, data type float32
- gamma: Required input, data type float16, bfloat16, float32

Outputs:

- dx: Required output, data type float16, bfloat16, float32
- dgamma: Required output, data type float32

## Example

```python
import os
import torch
import torch_npu
import numpy as np
import math
from mindspeed.op_builder import RmsNormOpBuilder

x = torch.rand([2, 4]).to(torch.float).npu()
gamma = torch.rand([4]).to(torch.float).npu()
# Forward interface example
mindspeed_ops = RmsNormOpBuilder().load()
out = mindspeed_ops.rms_norm(x, gamma)
# Backward interface example
out.backward(torch.ones(out.shape).npu())

```
