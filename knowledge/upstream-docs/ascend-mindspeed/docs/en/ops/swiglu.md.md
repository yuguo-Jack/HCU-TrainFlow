---
id: doc-ascend-mindspeed-5dbf1cd51166cacb4b17
title: Ascend/MindSpeed / docs/en/ops/swiglu.md
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
path: docs/en/ops/swiglu.md
raw_sha256: b87fd878b4e6e21c2d12f1bfbc81307ad6c13c9946ad16ca2745e23608b8ea20
sources: []
generated_body_sha256: 7ec195677f1e35cd1c61956b60aca956bf0349eca344707e42be3ab5e748f566
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/ops/swiglu.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/ops/swiglu.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# swiglu

## Forward API

Input:

- x: Required input, data type float16, bfloat16, float32

Output:

- y: Required output, data type float16, bfloat16, float32

Attributes:

- dim: Optional attribute, data type int32_t, default -1.

## Backward API

Inputs:

- dy: Required input, data type float16, bfloat16, float32
- x: Required input, data type float16, bfloat16, float32

Outputs:

- dx: Required output, data type float16, bfloat16, float32

Attributes:

- dim: Optional attribute, data type int32_t, default -1.

## Example

```python
    import os
    import torch
    import torch_npu
    import numpy as np
    import math
    from mindspeed.op_builder import SwigluOpBuilder

    x = np.random.uniform(-2, 2, (8192,1,3904))
    x = torch.from_numpy(x).float().npu()
    y_grad = np.random.uniform(-2, 2, (8192,1,1952))
    y_grad = torch.from_numpy(y_grad).float().npu()

    x.requires_grad = True
    # Forward interface example
    mindspeed_ops = SwigluOpBuilder().load()
    result = mindspeed_ops.swiglu(x, dim=-1)
    # Backward interface example
    result.backward(y_grad)
