---
id: official-megatron-wiki/energon
title: Megatron Energon：数据流水线、可恢复加载与训练空泡
engine: energon
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
coverage: selected implementation chain, not all models or backends
sources:
- source: nvidia-megatron-energon
  path: src/megatron/energon/loader.py
  commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
  sha256: aab81de16d65761bf00fc88a16c63c39e4f15118ef9044b4473b5aae913b279b
- source: nvidia-megatron-energon
  path: src/megatron/energon/savable_loader.py
  commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
  sha256: b94cb91f8ae3d99e45c49303d1acbfb2b6a9f286df1974f74ac3b00fcf4b17c2
- source: nvidia-megatron-energon
  path: src/megatron/energon/task_encoder/base.py
  commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
  sha256: d4fce3a940e2a673d3e7a40376f7741799b6c687b1e6ddea7202d66c8e943706
---

# Megatron Energon：数据流水线、可恢复加载与训练空泡

## 定位与组织

Energon 是训练数据加载与处理组件，不是 GPU 训练引擎。`loader.py` 提供普通与可恢复 loader，`savable_loader.py` 管可保存加载状态，`task_encoder/base.py` 负责样本编码和 batch 组织；flavors、wrappers、worker 等目录继续定义数据及并发行为。官方 docs 文档已逐页保留，数据格式和恢复路径要结合它们阅读。

## 普通加载与可恢复加载

`get_loader` 返回 BasicDataLoader；`get_savable_loader` 返回 SavableDataLoader，除了 prefetch/cache/watchdog，还接收内部 checkpoint 间隔、最小样本间隔及保留数量。源码说明内部 checkpoint 频度影响恢复耗时和读取开销，不存在对所有数据通用的最佳值。

当前接口中 worker_config 应附在 dataset；继续给 loader 传入已弃用的 worker_config 不会用它重配 dataset，不匹配还会报错。更新 Skill 示例时必须检查这类“参数仍存在但语义已弃用”的情况。

## TaskEncoder 与数据语义

TaskEncoder 对样本进行编码、batch 和需要的处理。要记录 tokenizer/encoder revision、数据 split、混合比例、shuffle/seed、packing 与过滤规则，并把训练实际消耗位置与模型 checkpoint 关联。仅保存 global step 不能证明数据能无重复、无遗漏续跑。

恢复验证应比较连续运行和中断恢复后的样本序列/ID、batch 内容、随机状态及有效 token 数。涉及 worker 数或 DP 变化时另做验证，不能假定一个进程布局下保存的状态可任意迁移。PR #301 涉及 loader close 后 dataset 是否仍能使用，提示对象所有权与资源关闭也是恢复契约。

## 运行、测试与性能

先用目标数据配方验证读取/编码/批处理，再接训练；采集数据读取吞吐、CPU 使用、解码耗时、队列水位、host 内存和 H2D。若 trace 显示 GPU 空泡，先对齐 batch ready 时间而不是立即改 kernel。增加 worker/prefetch 可能缓解等待，也可能造成主存、存储带宽或 pinned memory 压力。

合成数据可以隔离模型计算上限，但必须标记，不能代替真实数据管道验收。加载器测试至少覆盖正常迭代、保存恢复、提前退出、资源关闭和异常样本；大规模共享存储行为仍待实际环境。

## Watchdog 与故障边界

loader 暴露 watchdog timeout、首次 timeout 和 fail_on_timeout。打印栈或停止加载器不等同于集群容错完成；训练侧仍应观察 step 是否推进并衔接唯一恢复 owner。处理数据卡住先查 worker 栈、I/O、损坏样本、队列和共享内存，再决定是否重启。经验库保留输入管线身份与故障位置，公开 Cookbook 只发布方法和可公开示例。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [src/megatron/energon/loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/src/megatron/energon/loader.py) | `get_savable_loader`, `get_loader` |
| [src/megatron/energon/savable_loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/src/megatron/energon/savable_loader.py) | `SimpleSavableDatasetWrapper`, `SavableDatasetState`, `SavableCheckpoint`, `SavableDatasetCheckpoint`, `SavableDatasetWrapper`, `SavableDataLoaderState`, `SavableDataLoader`, `BasicDataLoader` |
| [src/megatron/energon/task_encoder/base.py](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/src/megatron/energon/task_encoder/base.py) | `generic_batch`, `batch_stack`, `batch_pad_stack`, `batch_list`, `stateless`, `stateless`, `stateless`, `get_stateless` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/nvidia-megatron-energon.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/nvidia-megatron-energon/)：保留来源内容，链接相对位置以原站为准。
- [PR #301：Keep datasets usable after closing a loader](../prs/NVIDIA--Megatron-Energon/PR-301.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine energon`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine energon`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT nvidia-megatron-energon` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
