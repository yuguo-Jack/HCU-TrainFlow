---
id: doc-ascend-mindspeed-f712d1d7562c500c1bbb
title: Ascend/MindSpeed / docs/en/ops/npu_groupmatmul_add.md
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
path: docs/en/ops/npu_groupmatmul_add.md
raw_sha256: a4ad8c83a9e6b01c9039f6591f91ef2dc031718cd4afec06e21263b333f50755
sources: []
generated_body_sha256: b131977cbb673df76fe45ad54512de7aa5d5323fac255aa07806d6789f8731d5
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/ops/npu_groupmatmul_add.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/ops/npu_groupmatmul_add.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# npu_groupmatmul_add_fp32 (Forward Only)

Inputs:

- x: Required Input, dimensions [m,k], data type float16, bf16
- weight: Required Input, dimensions [k,n], data type float16, bf16
- groupNum: Required Input, dimensions [NumGroup], data type int64
- output: Required Input, dimensions [w1, w2], Data Type float32

Output:

- output: Required Output, Data Type float32

## Example

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
# Separate operator computation result
_, dy, _ = GMMFunction.builder.load().npu_gmm_backward([grads_out], [x], [weight], group_list, 0)
out_single = out+dy[0].view(*out.shape)
#Fused operator computation result
x = x.clone().detach()
grads_out = grads_out.clone().detach()
group_list = group_list.clone().detach()
out = out.clone().detach()
npu_groupmatmul_add_fp32(x, grads_out, group_list, out)
```
