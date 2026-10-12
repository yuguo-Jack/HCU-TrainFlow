---
id: doc-ascend-mindspeed-5b281e477faf0945b7e7
title: Ascend/MindSpeed / docs/en/ops/npu_matmul_add.md
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
path: docs/en/ops/npu_matmul_add.md
raw_sha256: 2b643769248643233d850111afa463f19691a19e680edc597df0a71c28a367ce
sources: []
generated_body_sha256: 10e70d885143049830cdcb32acd049a13022696a4a426221d8a4114053eaef7a
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/ops/npu_matmul_add.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/ops/npu_matmul_add.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# npu_matmul_add_fp32 (Forward Only)

Inputs:

- x: Required Input, Data Type float16, bf16
- weight: Required Input, Data Type float16, bf16
- C: Required Input, Data Type float32

Output:

- output: Required output, data type float32

## Example

```python
    import torch
    import torch_npu
    from mindspeed.ops.npu_matmul_add import npu_matmul_add_fp32

    x = torch.rand((4096, 8192),dtype=torch.float16).npu()
    weight = torch.rand((4096, 8192),dtype=torch.float16).npu()
    C = torch.rand((8192, 8192),dtype=torch.float32).npu()
    # Separate operator computation process
    product = torch.mm(x.T, weight)
    result = product + C
    # Fused operator computation process
    npu_matmul_add_fp32(weight, x, C)
```
