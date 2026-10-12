---
id: doc-ascend-mindspeed-10aa3d642b574116541e
title: Ascend/MindSpeed / docs/zh/features/npu_matmul_add.md
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
path: docs/zh/features/npu_matmul_add.md
raw_sha256: 2c21e180d9aed4bb48aa177cb33e49147df12adf209187adc87bb01e564c8a47
sources: []
generated_body_sha256: 925cc3b00d756382d9a6297189934a2dfd0a99c0e7acf676f901fb7cfb6afd08
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/npu_matmul_add.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/npu_matmul_add.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# matmul_add融合优化

## 背景与挑战

模型训练中开启了梯度累加功能，但累加效率较慢，梯度累加中的 Add 算子占比较高。

## 解决方法

MindSpeed将matmul操作和add操作合并成一个融合算子。算子接口见[npu_matmul_add](../ops/npu_matmul_add.md)。

## 使用场景

LLaMA及GPT大模型均可使用。

## 使用方法

融合算子使能要求安装ATB（Ascend Transformer Boost），请参考[软件安装](../user-guide/install_guide.md)完成安装。

去掉`--no-gradient-accumulation-fusion`即可调用Matmul_Add融合算子。

### 说明

* npu_matmul_add_fp32暂不支持MFU（Model FLOPS Utilization，模型算力利用率）统计。
* 融合算子与小算子之间存在一定的精度差异。
精度差异的根本原因：
小算子matmul操作结束后，会先将得到的结果进行降精度（由fp32到bf16）再升精度（由bf16到fp32）最后进行add操作，这种先降再升的操作会损失一部分精度，而融合算子会跳过这一操作直接进行累加，故精度上存在差异。<br>
具体变化过程如下：
    * 小算子dtype变化过程：`bf16*bf16=fp32->bf16->fp32+fp32=fp32`
    * 融合算子dtype变化过程：`bf16*bf16=fp32+fp32=fp32`

## 使用效果

在内存未占满的情况下，开启Matmul_Add融合算子，模型训练的性能将得到提升，在Llama-2-7b模型下，性能增益约2%。
