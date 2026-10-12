---
id: doc-ascend-mindspeed-238c4001f4bbd7b3cde8
title: Ascend/MindSpeed / docs/zh/features/dist_ckpt.md
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
path: docs/zh/features/dist_ckpt.md
raw_sha256: d8d041e4e2c2daf32687fa0a50dabfc5912a890b7b044c7da5b8a438bf8b5c76
sources: []
generated_body_sha256: 2dac5c2a0d75fd276fc34425b23c1a3cd49f82829f07d019560aa4b7bc48efec
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/dist_ckpt.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/dist_ckpt.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron 分布式权重

## 背景与挑战

在传统的权重保存加载过程中，即训练脚本中指定了`--ckpt-format torch`参数的场景中，每张卡上都会持有完整的优化器状态，在保存阶段，每张卡上都会将完整的优化器状态保存到磁盘中，存在数据冗余。

为了消减优化器状态的数据冗余，尽管可以通过开启分布式优化器，使得每张卡上仅持有分片后的优化器状态，来减小运行时的内存开销和保存的权重文件的磁盘空间占用，但是这种策略会在保存阶段和加载阶段分别引入All-Gather操作和Scatter操作，从而增加通信开销。

## 解决方案

为解决上述问题，引入完全分片策略，将模型参数和优化器状态进行完全分片，在权重保存和加载过程中，每张卡仅保存和加载各自的分片数据，消减数据冗余。和分布式优化器相比，省去了保存阶段的All-Gather操作和加载阶段的Scatter操作。

## 使用场景

支持TP、PP、CP、EP、VPP并行配置场景以及Megatron原生特性启用场景，暂未适配MindSpeed特性启用场景。

## 使用方法

- 在脚本中指定`--ckpt-format torch_dist`和`--save 权重保存路径`即可启用分布式权重保存功能，模型在保存阶段会保存为分布式权重。
- `--auto-detect-ckpt-format`为可选参数，用于自动检测权重格式加载。指定了`--ckpt-format torch_dist`和`--load 权重加载路径`的训练脚本使用此参数后，在加载阶段会自动检测权重属于`--ckpt-format torch_dist`格式或`--ckpt-format torch`格式的权重进行加载。

> [!NOTE]
>
> - `--ckpt-format torch_dist`格式生成的权重，在加载时请指定相同的`--ckpt-format`参数，即使用`--ckpt-format torch_dist`。
> - `--ckpt-format torch_dist`暂未适配MindSpeed特性启用场景。
> - 在CP场景下，`--ckpt-format torch_dist`目前仅支持`--context-parallel-algo`为`megatron_cp_algo`。

## 使用效果

启用分布式权重后，模型和优化器状态在保存时分片存储。相比传统权重格式，节省了权重文件的磁盘空间占用。相比分布式优化器，省去了保存阶段All-Gather操作和加载阶段的Scatter操作。
