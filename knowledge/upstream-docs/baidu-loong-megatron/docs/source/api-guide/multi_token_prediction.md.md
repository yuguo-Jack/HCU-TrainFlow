---
id: doc-baidu-loong-megatron-c5bf641e5c8136ad1586
title: baidu-baige/Loong-Megatron / docs/source/api-guide/multi_token_prediction.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/Loong-Megatron
commit: 64c279afb879229cff12fb293624e3691990403f
path: docs/source/api-guide/multi_token_prediction.md
raw_sha256: 44c1aa980d31b4033087de2d7b86cf5ae7b05da9af1791b86f209964b3453e23
sources: []
generated_body_sha256: 5b1d965b4359c989d40f11f95f9a82646a3cc09976ff53b546c551523119729c
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/multi_token_prediction.md

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/multi_token_prediction.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Multi-Token Prediction (MTP)

Multi-Token Prediction (MTP) extends the prediction scope to multiple future tokens at each position. On the one hand, an MTP objective densifies the training signals and may improve
data efficiency. On the other hand, MTP may enable the model to pre-plan its representations for better prediction of future tokens. In this implementation of MTP, we sequentially predict additional tokens and keep the complete causal chain at each prediction depth. The following figure illustrates our implementation of MTP in [DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3/).

![MTP_implementation](../images/multi_token_prediction/MTP_implementation.png)

The k-th MTP module consists of a shared embedding layer, a projection matrix, a Transformer block, and a shared output head. For the i-th input token at the (k - 1)-th prediction depth, we first combine the representation of the i-th token and the embedding of the (i + K)-th token with the linear projection. The combined serves as the input of the Transformer block at the k-th depth to produce the output representation.

For more information, please refer to [DeepSeek-V3 Technical Report](https://github.com/deepseek-ai/DeepSeek-V3/blob/main/DeepSeek_V3.pdf)

## Related Arguments

We can train GPTModel like models with Multi-Token Prediction (MTP) by setting mtp_num_layers to be a positive integer.

| Item | Description |
| --- | --- |
| mtp_num_layers | Number of Multi-Token Prediction (MTP) Layers. MTP extends the prediction scope to multiple future tokens at each position. This MTP implementation sequentially predict additional tokens by using D sequential modules to predict D additional tokens. Default is None. |
| mtp_loss_scaling_factor | Scaling factor of Multi-Token Prediction (MTP) loss. We compute the average of the MTP losses across all depths, and multiply it the scaling factor to obtain the overall MTP loss, which serves as an additional training objective. Default is 0.1. |

## Precautions

Please do not use Context Parallel (CP), or arbitrary AttnMaskType, or learned absolute position embedding type with MTP. These use cases are not yet supported.
