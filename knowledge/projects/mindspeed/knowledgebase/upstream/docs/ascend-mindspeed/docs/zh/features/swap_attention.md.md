---
id: doc-ascend-mindspeed-33a4ace4d1fcbda59763
title: Ascend/MindSpeed / docs/zh/features/swap_attention.md
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
path: docs/zh/features/swap_attention.md
raw_sha256: 08e59f1e4609b7a09471ceaab3531bd2b60ab0b1c53f9f845afb7272f8b04902
sources: []
generated_body_sha256: eae2ced271f0f45113b53547e12dd88c4ad662e8a712171356fea0cdc63b554f
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/swap_attention.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/swap_attention.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# swap-attention

## 背景与挑战

大模型训练过程中，使用重计算功能可以大幅度减少内存，但会增加训练过程的计算时长，导致执行效率较低。

## 解决方案

新增swap-attention功能，利用设备内存和CPU内存来存放激活值，在梯度反传的同时从CPU内存预取激活值来减少重计算，充分利用H2D高带宽的优势以网补存、以网强算，提升MFU，加速大模型的训练。

![swap_attention总体流程](../figures/swap_attention.png)

## 使用场景

* 优化性能：在需要开启全重计算的场景下，可以通过开启`--swap-attention`和`--recompute-num-layers [int]`替换全重计算，以达到提升性能的目的。

* 节省内存：对于不需要重计算的场景，只开启`--swap-attention`，可以在几乎不损耗性能的情况下，节省内存，以支持更大的模型的配置。

## 使用方法

* 需要添加参数`--swap-attention`。使用前提是开启flash attention融合算子。

* 可选参数`--swap-modules`：参数类型为string，默认值为"input_norm,self_attention,post_attention_norm"，可根据模型自行配置module，在mcore场景下默认仅预取self_attention module。

以下是仅开启预取功能和开启预取功能并且指定重计算层数的用法和区别。

**仅开启预取功能：`--swap-attention`**

开启后，将对每一层的attention层的激活值进行预取，提高计算效率。

![swap_attention预取](../figures/swap_attention1.png)

**开启预取功能并且指定重计算层数：`--swap-attention`和`--recompute-num-layers [int]`**

开启后，将对每一层的attention层的激活值进行预取，同时，对前[int]层的全连接层进行重计算。

![swap_attention预取+重计算](../figures/swap_attention2.png)

## 使用效果

该方案相比完全重计算具有性能收益；相比不重计算具有内存收益。

> [!NOTE]
>
> * `--recompute-num-layers [int]`中的[int]层数指的是每一个pp stage的层数。[int]的取值应该小于等于num-layers/pipeline-model-parallel-size。
> * 若出现性能波动，可能是跨NUMA内存访问引起，可尝试通过进程绑核缓解 `export CPU_AFFINITY_CONF=1,lazy_bind:0`。
> * `--swap-attention`暂不兼容LoRA微调。
