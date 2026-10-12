---
id: official-megatron-wiki/topics/bridge-overlap-memory
title: Bridge：DP/TP/PP/CP/EP 重叠、Graph 与显存取舍
engine: bridge
kind: authored
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: nvidia-nemo-megatron-bridge
  path: docs/training/communication-overlap.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 859943b891cd2eefe537fe433c40e7a7ba0fcca702f6ecf44ccf1f9075e4ddde
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/comm_overlap.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: efabb5d0084f4c5c29b96c6bf6a22307c7a2fb89a72453e22f6d91c4f5afd8dc
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/config.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: f0ddd9f5450e353dad5cdf067ba8b01088e3e29ff35e521fa622141e03fe080d
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/train.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 413a9f26ed5d92a2cc419481897a174c6d11af4d9623a2cc2610b6478c70b561
---

# Bridge：DP/TP/PP/CP/EP 重叠、Graph 与显存取舍

## 从暴露瓶颈进入

communication overlap隐藏的是关键路径上尚未被计算覆盖的通信。多stream同时存在、通信总耗时大或flag已开都不能证明可获收益。先保留无overlap可信基线，观测真实TP/DP/PP/CP/EP组的代表rank，区分通信固有时长、rank不均和暴露等待。

## 不同并行域的调用与限制

`CommOverlapConfig`经setup传播model/DDP/optimizer字段，再由Core/TE执行。DP的grad reduce-scatter/param all-gather依赖distributed optimizer与Megatron DDP，FSDP自己的机制不能直接套。TP要求sequence parallel、TP>=2与受支持TE路径；PP依schedule/VPP的P2P；CP依chosen communication algorithm，不能统一叫“一个开关全开”。

EP的`overlap_moe_expert_parallel_comm`当前早期检查EP>1、experts>1、alltoall/flex、BF16/FP16与Torch>=2.6；PP>1需VPP。不能搭full recompute，相关method/num_layers和moe重算模块有限制；shared-expert overlap互斥，MTP层数也受条件限制。DeepEP/HybridEP走flex还需真实底层安装/版本和容量/同步条件。

`delay_wgrad_compute`依EP overlap，不是通用GEMM加速；graph、gradient reduction/accumulation、bias/shared expert和TE版本又有额外条件。正式开启前读当前`comm_overlap.py`全部validate/setup分支，而非凭参数名推断支持。MindSpeed共享专家策略不同，不能交叉套用。

## 内存与调度收益

更早发起通信/推迟wgrad可能增buffer、活动microbatch或state寿命，争用HBM/SM/网络。kernel稍慢可换来更快step，也可能本来通信已隐藏而只多付开销。重算/offload减少HBM又可能减少overlap窗口，要联看MB、VPP、rank负载和最坏rank的显存余量。

官方文档明确小EP/少microbatch可能持平或更慢；延迟wgrad相对overlap-only也不是保证提升。launch变量针对具体平台/dispatcher，不能把NV连接数或某一次HCU队列参数写成所有组合默认。

## 验证与归因

按通信域一次改可解释的候选，保存final flags、底层dispatcher/backend、模型shape和有效token。先验证输出/grad/optimizer、合法/非法配置，再比较热身后的相同wall-clock窗口、GPU空泡、暴露collective、buffer/显存与稳态step。重叠区域不相加，最快rank不作全局时间。

graph/capture/fallback分别检查；enable但自动禁用、共享buffer不匹配或库接口fallback必须报告。阶段loss放在局部数值可信且形成优化阶段成果后，不用频繁长训替代机制验证。

## 排障、回退与维护

卡住查所有rank最后共同事件、组和collective顺序、资源不足/异常；内存风险查活动微批/新增buffer，数值偏差查梯度延迟/累加依赖。退回已验证的分域配置，再决定调参、框架调度、通算融合或底层库优化。修改Core/TE、dispatcher、overlap/graph约束时同步[总览](../bridge.md)、provider和checkpoint专题，不以文档刷新替代实际版本检查。

## 固定证据与复核范围

- [docs/training/communication-overlap.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/communication-overlap.md)
- [src/megatron/bridge/training/comm_overlap.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/comm_overlap.py)
- [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/config.py)
- [src/megatron/bridge/training/train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/train.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
