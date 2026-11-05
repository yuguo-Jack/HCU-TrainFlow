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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-nemo-megatron-bridge
  path: docs/training/communication-overlap.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 859943b891cd2eefe537fe433c40e7a7ba0fcca702f6ecf44ccf1f9075e4ddde
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/comm_overlap.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 820c5164aa255f53ae58e525fcf100001759b375f2d4e5f3f726510ba4a1bcee
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/config.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: deeafbdcdbb8738f7ca6d2e0190e159b542d6bc6e1fab919eca9d4f740e4bd93
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/train.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 03f09f7ff1da6cc83f04ea9450280bf33adcd873ced83d50e7c35531910adddf
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/utils/optimizer_utils.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 49210014dbe1df236cfa7b80c368222db033601f209ba0c75a2cf88fa4825da3
retrieved_on: '2026-11-04'
---

# Bridge：DP/TP/PP/CP/EP 重叠、Graph 与显存取舍

## 从暴露瓶颈进入

communication overlap隐藏的是关键路径上尚未被计算覆盖的通信。多stream同时存在、通信总耗时大或flag已开都不能证明可获收益。先保留无overlap可信基线，观测真实TP/DP/PP/CP/EP组的代表rank，区分通信固有时长、rank不均和暴露等待。

## 不同并行域的调用与限制

`CommOverlapConfig`经setup传播model/DDP/optimizer字段，再由Core/TE执行。DP 的 grad reduce-scatter/param all-gather 依赖 Megatron DDP 和实际 optimizer 分布；新 `uses_distributed_optimizer` 同时识别普通 DistOpt 与 LayerWise，不能只读 DDP 的同名 bool。FSDP 自己的机制不能直接套。TP要求sequence parallel、TP>=2与受支持TE路径；PP依schedule/VPP的P2P；CP依chosen communication algorithm，不能统一叫“一个开关全开”。

EP的`overlap_moe_expert_parallel_comm`当前早期检查EP>1、experts>1、alltoall/flex、BF16/FP16与Torch>=2.6；PP>1需VPP。不能搭full recompute，相关method/num_layers和moe重算模块有限制；shared-expert overlap互斥，MTP层数也受条件限制。DeepEP/HybridEP走flex还需真实底层安装/版本和容量/同步条件。

`delay_wgrad_compute`依EP overlap，不是通用GEMM加速；graph、gradient reduction/accumulation、bias/shared expert和TE版本又有额外条件。正式开启前读当前`comm_overlap.py`全部validate/setup分支，而非凭参数名推断支持。MindSpeed共享专家策略不同，不能交叉套用。

当前 Bridge 保留自己的 `dist.use_megatron_fsdp` 兼容字段，并与所选 Megatron-FSDP 版本的 DDP/optimizer 设置联动；不能因新 Core 不再声明同字段就删掉 Bridge 配方，也不能与 Torch FSDP2 混称。确定性模式改为把 cross-entropy、TP overlap、router fusion 等选项交给固定 Core 的 `apply_determinism_to_args` 校验；旧 Bridge 内嵌的环境断言不是当前完整规则，更不直接成为 HCU 环境模板。

## 内存与调度收益

更早发起通信/推迟wgrad可能增buffer、活动microbatch或state寿命，争用HBM/SM/网络。kernel稍慢可换来更快step，也可能本来通信已隐藏而只多付开销。重算/offload减少HBM又可能减少overlap窗口，要联看MB、VPP、rank负载和最坏rank的显存余量。

官方文档明确小EP/少microbatch可能持平或更慢；延迟wgrad相对overlap-only也不是保证提升。launch变量针对具体平台/dispatcher，不能把NV连接数或某一次HCU队列参数写成所有组合默认。

## 验证与归因

按通信域一次改可解释的候选，保存final flags、底层dispatcher/backend、模型shape和有效token。先验证输出/grad/optimizer、合法/非法配置，再比较热身后的相同wall-clock窗口、GPU空泡、暴露collective、buffer/显存与稳态step。重叠区域不相加，最快rank不作全局时间。

graph/capture/fallback分别检查；enable但自动禁用、共享buffer不匹配或库接口fallback必须报告。阶段loss放在局部数值可信且形成优化阶段成果后，不用频繁长训替代机制验证。

退出/重启还要核对 graph 所有者。当前 `_delete_cuda_graphs` 除 full/optimizer graph、实际创建的 TE graph 和 Core 通用 local 清理，还接收 model 遍历每个 `CudaGraphManager`：synchronize 后清空 runner 的 fwd/bwd graph、mempool、runner 列表和 lookup table。新增 `_delete_local_cuda_graph_runners` 处理了仅调通用清理仍可能留下的 model-owned 引用；只清 TE helper 会遗漏另一组持有通信 buffer 的图。验证捕获与未创建图、local/TE 模式及进程组销毁顺序，不能把代码清理入口存在当成实际多 rank 退出无残留。

## 排障、回退与维护

卡住查所有rank最后共同事件、组和collective顺序、资源不足/异常；内存风险查活动微批/新增buffer，数值偏差查梯度延迟/累加依赖。退回已验证的分域配置，再决定调参、框架调度、通算融合或底层库优化。修改Core/TE、dispatcher、overlap/graph约束时同步[总览](../overview/bridge.md)、provider和checkpoint专题，不以文档刷新替代实际版本检查。

2026-11-04 复核固定 `41af2dcf0dfd83c8933f588bb871b7f56dbd4368`：`OptimizerConfig.finalize` 已改为别名规范化→Core validate→finalize_optimizer_config。emerging optimizers 使用 LayerWise 分布；compact layout 默认不打开普通 DDP DistOpt 布局，shard-aligned layout 是另一个 opt-in。`CommOverlapConfig.setup` 为这类 optimizer 保留现有 bucket_size 与 overlap_grad_reduce，除非用户显式覆盖，DP=1 也可能因 CP 仍需归约。不能照搬 Adam/SGD preset 或由一个 flag 推算通信/显存。补采的 `normalize_optimizer_config` 将 `dist_` 前缀规范化，拒绝 Adam/SGD 走 LayerWise，并对 emerging optimizer 把普通分布请求转为 LayerWise、清除普通 DistOpt bool；另拒绝 overlap_param_gather_with_optimizer_step。LayerWise 要求 num_distributed_optimizer_instances=1，当前拒绝与 Megatron-FSDP / Torch-FSDP2 拼接；MegatronMIMO 另拒绝 overlap_param_gather 加 MXFP8 复用 grad buffer。现有 EP 早期约束与普通通信文档未变，仍由固定 Core 再校验，不构成已运行证明。

## 固定证据与复核范围

- [docs/training/communication-overlap.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/training/communication-overlap.md)
- [src/megatron/bridge/training/comm_overlap.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/comm_overlap.py)
- [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/config.py)
- [src/megatron/bridge/training/train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/train.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
