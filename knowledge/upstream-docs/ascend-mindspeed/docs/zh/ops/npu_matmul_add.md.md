---
id: doc-ascend-mindspeed-18537b624ded58228c7e
title: Ascend/MindSpeed / docs/zh/ops/npu_matmul_add.md
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
path: docs/zh/ops/npu_matmul_add.md
raw_sha256: 63bd9fcdf32e1642906ec34a4a7ed5b3f3bb2943c9be2662f095d5e3762dd4c6
sources: []
generated_body_sha256: e11bc3f8ead8a2499c0f2d5b7189164a3693e611310f0d61681c944b456fdcc1
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/ops/npu_matmul_add.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/ops/npu_matmul_add.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# npu_matmul_add_fp32对外接口(只支持前向)

输入：

- x：必选输入，数据类型float16, bf16
- weight：必选输入，数据类型float16, bf16
- C：必选输入，数据类型float32

输出：

- output：必选输出，数据类型float32

## 案例

```python
    import torch
    import torch_npu
    from mindspeed.ops.npu_matmul_add import npu_matmul_add_fp32

    x = torch.rand((4096, 8192),dtype=torch.float16).npu()
    weight = torch.rand((4096, 8192),dtype=torch.float16).npu()
    C = torch.rand((8192, 8192),dtype=torch.float32).npu()
    # 分开算子计算过程
    product = torch.mm(x.T, weight)
    result = product + C
    # 融合算子计算过程
    npu_matmul_add_fp32(weight, x, C)
```
