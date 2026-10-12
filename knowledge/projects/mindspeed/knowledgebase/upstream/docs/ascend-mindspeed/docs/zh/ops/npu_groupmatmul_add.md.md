---
id: doc-ascend-mindspeed-1cf1a960be726f9df154
title: Ascend/MindSpeed / docs/zh/ops/npu_groupmatmul_add.md
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
path: docs/zh/ops/npu_groupmatmul_add.md
raw_sha256: 7610475b0087635675f4eef4b9ddf3f572e28205617d6bbc6bd3b0cf28143f02
sources: []
generated_body_sha256: f478bc672357d1508cbc049440d9f36c876ce2cf64a515fad53de4bdb2d6b365
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/ops/npu_groupmatmul_add.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/ops/npu_groupmatmul_add.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# npu_groupmatmul_add_fp32对外接口(只支持前向)

输入：

- x：必选输入，维度[m,k], 数据类型float16, bf16
- weight：必选输入，维度[k,n], 数据类型float16, bf16
- groupNum：必选输入， 维度[NumGroup], 数据类型int64
- output：必选输入，维度[w1,w2]，数据类型float32

输出：

- output：必选输出，数据类型float32

## 案例

```python
# Copyright (c) 2024, Huawei Technologies Co., Ltd.  All rights reserved.
import pytest
import torch
import mindspeed.megatron_adaptor
import torch_npu
from mindspeed.ops.gmm import GMMFunction
from mindspeed.ops.npu_groupmatmul_add import npu_groupmatmul_add_fp32

x = torch.rand((1024, 4096), dtype=torch.float16).npu()
grads_out = torch.rand((1024, 2048), dtype=torch.float16).npu()
group_list = torch.tensor([500, 1024], dtype=torch.int64).npu()
out = torch.rand((8192, 2048), dtype=torch.float32).npu()
weight = torch.rand((2, 4096, 2048), dtype=torch.float16).npu()
# 分开算子计算结果
_, dy, _ = GMMFunction.builder.load().npu_gmm_backward([grads_out], [x], [weight], group_list, 0)
out_single = out+dy[0].view(*out.shape)
#融合算子计算结果
x = x.clone().detach()
grads_out = grads_out.clone().detach()
group_list = group_list.clone().detach()
out = out.clone().detach()
npu_groupmatmul_add_fp32(x, grads_out, group_list, out)
```
