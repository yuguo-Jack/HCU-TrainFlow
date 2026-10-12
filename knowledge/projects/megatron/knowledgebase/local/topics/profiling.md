---
id: official-megatron-wiki/profiling
title: 训练 profiler 采样与 TraceLens 联动
engine: megatron
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
sources:
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: e436206da1fe3ec5b8b5da8a06e1c8d6a7e08f149a0079107d83f1d68284e469
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: eca958faeab77e1df81073998ea07aa3cc8a5884f96f6182782d620942139bd2
- source: nvidia-megatron-lm
  path: megatron/training/config/common_config.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 14cebf41822c0e3fdcb9ea560f35f878bc69659b7b0418452b57b08a791aa159
kind: authored
---

# 训练 profiler 采样与 TraceLens 联动

## 抓取窗口

在训练循环里核对本版本 `cfg.profiling`、`profile_step_start/end`、`profile_ranks`、PyTorch profiler 的启停。不要将历史版本启动 flag 直接套到新版配置。窗口选 warmup 后完整训练步，明确是否包含 optimizer、数据等待、checkpoint 或 evaluation。

保留每 rank 独立 trace 与 metadata：运行快照、step 区间、实际 groups、时钟域、shape/dtype/stride、phase 与 profiler 设置。shape/stack/memory 采集增加开销，只对所需窗口开启；吞吐比较另跑 profiler-off。

## 当前官方 profiler 的具体契约

`ProfilingConfig` 将 `use_pytorch_profiler`、`profile_step_start/end`、`profile_ranks` 和 shapes/callstack/Chakra 设置交给训练循环。空 `profile_ranks=[]` 表示全部 rank；配置校验要求 PyTorch profile 的 end 大于 start，且与 nsys 模式互斥。选 rank 仍应覆盖任务实际并行域，不能只用默认列表解释多域问题。

当前 PyTorch schedule 为 `wait=max(start-1,0)`、`warmup=1 if start>0 else 0`、`active=end-start`、`repeat=1`。迭代中调用 `prof.step()`；恢复 checkpoint 后的 start iteration 和保存/评估等分支也要核对，确认导出的正是目标完整训练窗口，而不是靠参数字面值推断已有完整稳态样本。

Chrome trace 输出为 TensorBoard 目录相邻 `torch_profile/rank-<rank>.json.gz`；启用 ExecutionTraceObserver 时另输出 `chakra/rank-<rank>.json.gz`。二者格式与用途不同，不能把 Chakra ET 直接当作 Kineto kernel 时间线交给同一解析器。先将 logger/profiler 输出根映射到任务范围，避免默认 `../` 写到任务外。每 rank 保存各自文件并核对最终完整写出、大小与窗口。

源码以 PyTorch 的 GPU activities 和设备 API 调用采样；HCU 的支持取决于现用 PyTorch/DTK、补丁与实际 trace。读取进程实际加载的 profiler、HIP runtime/Kernel 事件类别与 shape 关联，缺 kernel 或相关性时明示不完整。上游 nsys/NVTX 开关的存在不表示 HCU 用同一二进制工具。

## 分析顺序

1. 先识别端到端主导开销。空泡占主导时区分 CPU launch、数据读取、同步、PP 等待和内存分配；看到空白不能直接下 CPU 瓶颈结论。
2. 通信或偏斜占主导时，核对同域 rank 的 collective 顺序、消息大小和等待；与同调用基准比较后再选择链路排查、overlap、通算融合或框架负载均衡。
3. 计算占主导时按实际占比排队，核对 NV 参考调用链和已有 HCU 融合实现，再分析真实 shape 对应 kernel 的瓶颈与条件上限。
4. 对累计覆盖端到端墙钟时间至少 90% 的热点集合逐个评估非通信计算项；保留未知项，初步融合后仍需复评效率并衔接 HIP/Triton 迭代。

TrainFlow 的区间扫描将同 rank 重叠区间等份归因，作为可检查的排序代理；不是分布式关键路径证明。未归因/CPU/等待留在分母，覆盖不足显示 incomplete，不能偷偷换成 kernel 总时间。使用 TraceLens 的算子关联/collective/overlap 报告补足细节，跨 rank 对齐另保留校时依据。

## TraceLens 分析接口

官方工具机制见 [TraceLens Wiki](../../../../tracelens/README.md)。HCU 运行版本的命令、Graph、Replay、Roofline、Agent 与 DTK 输入边界统一见 [TrainFlow 分析契约](../../../../../../docs/tracelens-analysis.md)。本页负责 Megatron 的采样与消费关系，不重复维护 HCU fork 的实现知识。更换工具或 profiler 版本时复核接口和真实原件；理论上限、实测 sustained 参考和同 shape 实测分别保留来源。

## 固定源码与更新范围

- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/training.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/arguments.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
