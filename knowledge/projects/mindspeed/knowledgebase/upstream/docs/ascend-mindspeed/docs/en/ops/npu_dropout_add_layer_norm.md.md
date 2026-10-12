---
id: doc-ascend-mindspeed-84260a721afde9c24f08
title: Ascend/MindSpeed / docs/en/ops/npu_dropout_add_layer_norm.md
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
path: docs/en/ops/npu_dropout_add_layer_norm.md
raw_sha256: e8fa11ea9716a4006b085e48a4a2764061f6513fd1f8b31434fe44c7ace35819
sources: []
generated_body_sha256: 6a0b3350eeafa9a32ee3dc2a60754b7f374a261a4d28fff0e63094ff878b6196
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/ops/npu_dropout_add_layer_norm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/ops/npu_dropout_add_layer_norm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# npu_dropout_add_layer_norm

```python
# computation logic
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

# computation logic
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

Inputs:

- x0: required input, shape: (B,S,H).
- residual: Required input, shape: (B,S,H), can be None. Represents the residual.
- weight: Required input, shape: (H,). Represents the weight parameter for normalization.
- bias: Required input, shape: (H,), data type consistent with input weight, can be None. Represents the bias parameter for normalization.
- dropout_p: Required attribute, data type float. Represents the dropout probability, p=0 in eval mode.
- epsilon: Required attribute, data type float. A value added to the denominator during normalization to improve numerical stability.
- rowscale: optional input, shape: (B,S), data type same as input x0, default: None. Represents the row-wise scaling factor of the matrix.
- layerscale: optional input, shape: (H,), data type same as input x0, default: None. Represents the column-wise scaling factor of the matrix.
- prenorm: optional attribute, data type bool, default: False. Whether to return the output pre_norm_result.
- residual_in_fp32: optional attribute, data type bool, default: False. Meaningful only when the input residual is not None.
- return_dropout_mask: optional attribute, data type bool, default: False. Whether to return the output drop_mask.

Supported input data type combinations:

| x0 | residual | weight | rowscale | layerscale |
| ----- | ----- |  ----- | ----- | ----- |
|fp32|fp32|fp32|fp32|fp32 |
|fp16|fp16|fp16|fp16|fp16 |
|bf16|bf16|bf16|bf16|bf16 |

Outputs:

- norm_result: Required output. The data type is the same as that of input x0.
- pre_norm_result: Optional output. The data type is the same as that of input residual.
- mask_result: Optional output, data type is bool.

***

## Example Call 1: npu_dropout_add_layer_norm

- Input x0 and weight
- Only norm_result is returned

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

# Forward interface example
norm_result = npu_dropout_add_layer_norm(x0, residual, weight, bias, dropout_p, epsilon,
                                         rowscale, layerscale, prenorm, residual_in_fp32, return_dropout_mask)

g = torch.randn_like(norm_result)
norm_result.backward(g)
x0_grad = x0.grad
weight_grad = weight.grad

```

## Example Call 2: npu_dropout_add_layer_norm

- Inputs x0, residual, weight, rowscale, layerscale
- Returns norm_result, pre_norm_result, mask_result

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

# Forward interface example
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
