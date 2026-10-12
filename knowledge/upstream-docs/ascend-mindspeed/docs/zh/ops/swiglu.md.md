---
id: doc-ascend-mindspeed-180f1447509973a3eaab
title: Ascend/MindSpeed / docs/zh/ops/swiglu.md
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
path: docs/zh/ops/swiglu.md
raw_sha256: baa2baed1fbd86c3055632965c94ae67edbf11835e03667f891fa53e49741fcc
sources: []
generated_body_sha256: 2075e2f9824b5dc22b6f770cbceeeee932e3c497692ffd7d86d31808f897988e
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/ops/swiglu.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/ops/swiglu.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# swiglu对外接口

## 前向接口

输入：

- x：必选输入，数据类型float16, bfloat16, float32

输出：

- y：必选输出，数据类型float16, bfloat16, float32

属性：

- dim：可选属性，数据类型int32_t，缺省-1。

## 反向接口

输入：

- dy：必选输入，数据类型float16, bfloat16, float32
- x：必选输入，数据类型float16, bfloat16, float32

输出：

- dx：必选输出，数据类型float16, bfloat16, float32

属性：

- dim：可选属性，数据类型int32_t，缺省-1。

## 案例

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
    # 正向接口案例
    mindspeed_ops = SwigluOpBuilder().load()
    result = mindspeed_ops.swiglu(x, dim=-1)
    # 反向接口案例
    result.backward(y_grad)
