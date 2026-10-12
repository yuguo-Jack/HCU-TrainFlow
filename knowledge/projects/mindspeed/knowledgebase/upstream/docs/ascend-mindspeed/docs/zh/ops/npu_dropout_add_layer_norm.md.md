---
id: doc-ascend-mindspeed-f3b83b6e6ef8e18d7431
title: Ascend/MindSpeed / docs/zh/ops/npu_dropout_add_layer_norm.md
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
path: docs/zh/ops/npu_dropout_add_layer_norm.md
raw_sha256: 32abbb1dd67c4edabc3c3d263fdfb96f64928d153f7ae8b2be6a3052101c4501
sources: []
generated_body_sha256: 5ce1bc8e150e6d459f2694b8f1292a2999d1a58de264e82537750719265e850f
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/ops/npu_dropout_add_layer_norm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/ops/npu_dropout_add_layer_norm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# npu_dropout_add_layer_norm 对外接口

```python
# 计算逻辑
# norm_result = LayerNorm(Dropout(x0 x rowscale x layerscale) + residual)
def npu_dropout_add_layer_norm(x0,
                               residual,
                               weight,
                               bias,
                               dropout_p,
                               epsilon,
                               rowscale=None,
                               layerscale=None,
                               prenorm=False,
                               residual_in_fp32=False,
                               return_dropout_mask=False):

# 计算逻辑
# norm_result = RmsNorm(Dropout(x0 * rowscale * layerscale) + residual)   
def npu_dropout_add_rms_norm(x0,
                             residual,
                             weight,
                             bias,
                             dropout_p,
                             epsilon,
                             rowscale=None,
                             layerscale=None,
                             prenorm=False,
                             residual_in_fp32=False,
                             return_dropout_mask=False):         
```

输入：

- x0：必选输入，shape：(B,S,H)。
- residual：必选输入，shape：(B,S,H)，可输入None。表示残差。
- weight：必选输入，shape：(H,)。表示归一化处理时的权重参数。
- bias：必选输入，shape：(H,)，数据类型与输入weight一致，可输入None。表示归一化处理时的偏置参数。
- dropout_p：必选属性，数据类型float。表示Dropout舍弃概率，eval模式下p=0。
- epsilon：必选属性，数据类型float。归一化处理时，添加到分母中的值，以提高数值稳定性。
- rowscale：可选输入，shape：(B,S)，数据类型与输入x0一致，默认值：None。表示矩阵按行缩放比例。
- layerscale：可选输入，shape：(H,)，数据类型与输入x0一致，默认值：None。表示矩阵按列缩放比例。
- prenorm：可选属性，数据类型为bool，默认值：False。表示是否返回输出pre_norm_result。
- residual_in_fp32：可选属性，数据类型为bool，默认值：False。仅在输入residual不为None时有意义。
- return_dropout_mask：可选属性，数据类型为bool，默认值：False。表示是否返回输出drop_mask。

支持的输入数据类型组合：

| x0 | residual | weight | rowscale | layerscale |
| ----- | ----- |  ----- | ----- | ----- |
|fp32|fp32|fp32|fp32|fp32 |
|fp16|fp16|fp16|fp16|fp16 |
|bf16|bf16|bf16|bf16|bf16 |

输出：

- norm_result：必选输出，数据类型与输入x0一致。
- pre_norm_result：可选输出，数据类型与输入residual一致。
- mask_result：可选输出，数据类型为bool。

***

## 案例一：npu_dropout_add_layer_norm 接口的调用方式

- 输入 x0 和 weight
- 结果只返回 norm_result

```python
import torch
import torch_npu

from mindspeed.ops.dropout_add_layer_norm import npu_dropout_add_layer_norm


batch, seq, hidden_size = 6, 60, 1024
x0 = torch.randn((batch, seq, hidden_size), requires_grad=True).to(torch.float).npu()
weight = torch.randn((hidden_size, ), requires_grad=True).to(torch.float).npu()
residual, bias, rowscale, layerscale = None, None, None, None
dropout_p = 0.0
epsilon = 1e-5
prenorm, residual_in_fp32, return_dropout_mask = False, True, False

# 正向接口案例
norm_result = npu_dropout_add_layer_norm(x0, residual, weight, bias, dropout_p, epsilon,
                                         rowscale, layerscale, prenorm, residual_in_fp32, return_dropout_mask)

g = torch.randn_like(norm_result)
norm_result.backward(g)
x0_grad = x0.grad
weight_grad = weight.grad

```

## 案例二：npu_dropout_add_layer_norm 接口的调用方式

- 输入 x0, residual, weight, rowscale, layerscale
- 结果返回 norm_result, pre_norm_result, mask_result

```python
import torch
import torch_npu

from mindspeed.ops.dropout_add_layer_norm import npu_dropout_add_layer_norm


batch, seq, hidden_size = 6, 60, 1024
x0 = torch.randn((batch, seq, hidden_size), requires_grad=True).to(torch.float).npu()
residual = torch.randn((batch, seq, hidden_size), requires_grad=True).to(torch.float).npu()
weight = torch.randn((hidden_size, ), requires_grad=True).to(torch.float).npu()
bias = torch.randn((hidden_size, ), requires_grad=True).to(torch.float).npu()
rowscale = torch.randn((batch, seq, ), requires_grad=True).to(torch.float).npu()
layerscale = torch.randn((hidden_size, ), requires_grad=True).to(torch.float).npu()
dropout_p = 0.0
epsilon = 1e-5
prenorm, residual_in_fp32, return_dropout_mask = True, True, True

# 正向接口案例
norm_result, pre_norm_result, mask_result = npu_dropout_add_layer_norm(x0, residual, weight, 
                                                                       bias, dropout_p, epsilon,
                                                                       rowscale, layerscale, prenorm, 
                                                                       residual_in_fp32, return_dropout_mask)

g = torch.randn_like(norm_result)
norm_result.backward(g)
x0_grad = x0.grad
residual_grad = residual.grad
weight_grad = weight.grad
bias_grad = bias.grad
rowscale_grad = rowscale.grad
layerscale_grad = layerscale.grad
```
