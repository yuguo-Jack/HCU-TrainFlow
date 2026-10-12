---
id: doc-ascend-mindspeed-f0fe4471129df8e3b340
title: Ascend/MindSpeed / docs/zh/ops/rms_norm.md
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
path: docs/zh/ops/rms_norm.md
raw_sha256: 46c2e85137232f534dd996cae0e11db1b8b61203166a9e571a5931de50e651df
sources: []
generated_body_sha256: fb2992409957e00997012d85608e3b3ea92d190ac185e51dce920849b675e754
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/ops/rms_norm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/ops/rms_norm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# rms_norm对外接口

## 前向接口

输入：

- x：必选输入，数据类型float16, bfloat16, float32 
- gamma：必选输入，数据类型float16, bfloat16, float32

输出：

- rstd：中间变量，数据类型float32 
- out：必选输出，数据类型float16, bfloat16, float32

属性：

- epsilon：可选属性，数据类型float，缺省1e-6。

## 反向接口

输入：

- dy：必选输入，数据类型float16, bfloat16, float32
- x：必选输入，数据类型float16, bfloat16, float32
- rstd：必选输入，数据类型float32 
- gamma：必选输入，数据类型float16, bfloat16, float32 

输出：

- dx：必选输出，数据类型float16, bfloat16, float32
- dgamma：必选输出，数据类型float32

## 案例

```python
import os
import torch
import torch_npu
import numpy as np
import math
from mindspeed.op_builder import RmsNormOpBuilder

x = torch.rand([2, 4]).to(torch.float).npu()
gamma = torch.rand([4]).to(torch.float).npu()
# 正向接口案例
mindspeed_ops = RmsNormOpBuilder().load()
out = mindspeed_ops.rms_norm(x, gamma)
# 反向接口案例
out.backward(torch.ones(out.shape).npu())

```
