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
reviewed_on: '2026-11-18'
coverage: fixed source delta and actual consumer review; historical pins retained; no HCU runtime validation
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
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/config.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: fca097a18062d74b23785fe30782d507df32bb1e89816112e377cb70b284a261
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/train.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: a438b252612cbe51cced1193f917333dc08cdae445f3c9497517d34ca7781638
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/pretrain.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: 6534422c772f10bb8927f3c13e981d40a7758c1d63b458cc5b8372cfa1190c3c
retrieved_on: '2026-11-18'
---

# Bridge：DP/TP/PP/CP/EP 重叠、Graph 与显存取舍

## 从暴露瓶颈进入

communication overlap隐藏的是关键路径上尚未被计算覆盖的通信。多stream同时存在、通信总耗时大或flag已开都不能证明可获收益。先保留无overlap可信基线，观测真实TP/DP/PP/CP/EP组的代表rank，区分通信固有时长、rank不均和暴露等待。

## 不同并行域的调用与限制

`CommOverlapConfig`经setup传播model/DDP/optimizer字段，再由Core/TE执行。DP 的 grad reduce-scatter/param all-gather 依赖 Megatron DDP 和实际 optimizer 分布；新 `uses_distributed_optimizer` 同时识别普通 DistOpt 与 LayerWise，不能只读 DDP 的同名 bool。FSDP 自己的机制不能直接套。TP要求sequence parallel、TP>=2与受支持TE路径；PP依schedule/VPP的P2P；CP依chosen communication algorithm，不能统一叫“一个开关全开”。

EP的`overlap_moe_expert_parallel_comm`当前早期检查EP>1、experts>1、alltoall/flex、BF16/FP16与Torch>=2.6；PP>1需VPP。不能搭full recompute，相关method/num_layers和moe重算模块有限制；shared-expert overlap互斥，MTP层数也受条件限制。DeepEP/HybridEP走flex还需真实底层安装/版本和容量/同步条件。

`delay_wgrad_compute`依EP overlap，不是通用GEMM加速；graph、gradient reduction/accumulation、bias/shared expert和TE版本又有额外条件。正式开启前读当前`comm_overlap.py`全部validate/setup分支，而非凭参数名推断支持。MindSpeed共享专家策略不同，不能交叉套用。

当前 `11d8b349` 已删除 `dist.use_megatron_fsdp` 兼容字段；Megatron-FSDP 应读取 `cfg.ddp.use_megatron_fsdp`，Torch FSDP2 仍由 `cfg.dist.use_torch_fsdp2` 选择且与其互斥。不能让旧 dist 字段代替实际 DDP 选择。FSDP 梯度精度由 `megatron_fsdp_main_grads_dtype/grad_comm_dtype` 控制：两者未请求允许的 FP32 组合时，Bridge 清除普通 DDP 的 `grad_reduce_in_fp32`，并不把显式 dtype 升为 FP32。需要 FP32 累加就核对 main-grads 字段和真实 buffer；precision recipe 的旧 bool 不足为证。确定性仍交由固定 Core 的 `apply_determinism_to_args` 校验，不能把旧内嵌环境断言写成 HCU 模板。

`ConfigContainer` 在 recipe/runtime 修改后先 finalize optimizer，再为 Bridge 或直接 Core DDP config 应用精度策略并调用 Core.finalize；不再手工调用 Core.__post_init__。MFSDP V2 的普通 overlap/DistOpt 禁用条件仍在，但 Bridge 不再强写其 `data_parallel_sharding_strategy`，须检查选定 Core 的最终结果。该 Bridge 父锁与独立 Core 当前 HEAD 不同，不能跨版本拼接字段和默认值。

flex/ncclep 的 `apply_ncclep_one_gpu_per_rank` 必须在 CUDA 初始化前运行：按 LOCAL_RANK/SLURM_LOCALID 选择原可见列表中的设备，并让 trainer 选设备0；已经单设备可见时只设置 external mapping。非 ncclep、无 local rank、CUDA 已初始化或 rank 越界时不改列表，后两类告警。这是 NCCL EP 特定映射/主机开销路径，不能当 HCU 通用环境变量，也不能把源码中的 Grace/Blackwell 数字当本机实测。

## 内存与调度收益

更早发起通信/推迟wgrad可能增buffer、活动microbatch或state寿命，争用HBM/SM/网络。kernel稍慢可换来更快step，也可能本来通信已隐藏而只多付开销。重算/offload减少HBM又可能减少overlap窗口，要联看MB、VPP、rank负载和最坏rank的显存余量。

官方文档明确小EP/少microbatch可能持平或更慢；延迟wgrad相对overlap-only也不是保证提升。launch变量针对具体平台/dispatcher，不能把NV连接数或某一次HCU队列参数写成所有组合默认。

## 验证与归因

按通信域一次改可解释的候选，保存final flags、底层dispatcher/backend、模型shape和有效token。先验证输出/grad/optimizer、合法/非法配置，再比较热身后的相同wall-clock窗口、GPU空泡、暴露collective、buffer/显存与稳态step。重叠区域不相加，最快rank不作全局时间。

graph/capture/fallback分别检查；enable但自动禁用、共享buffer不匹配或库接口fallback必须报告。阶段loss放在局部数值可信且形成优化阶段成果后，不用频繁长训替代机制验证。

退出/重启按所有者清 graph。当前正常 `_delete_cuda_graphs` 同时接收 model 和 optimizer：先无同步清 optimizer-held grad-conversion/full graph 引用，再清实际创建的 TE graph、逐 model 的 CudaGraphManager runner 和 Core local graph。正常 local-runner 清理仍先 synchronize；失败/NVRx 路径只先做无同步的引用释放，不应改成等待所有 CUDA 工作，因为 peer 可能已在 collective 中失败。仅清 TE helper 或全局 wrapper 会漏掉 optimizer/model 各自持有的通信 buffer；代码入口存在仍需通过实际退出/重启验收。

## 排障、回退与维护

卡住查所有rank最后共同事件、组和collective顺序、资源不足/异常；内存风险查活动微批/新增buffer，数值偏差查梯度延迟/累加依赖。退回已验证的分域配置，再决定调参、框架调度、通算融合或底层库优化。修改Core/TE、dispatcher、overlap/graph约束时同步[总览](../overview/bridge.md)、provider和checkpoint专题，不以文档刷新替代实际版本检查。

2026-11-04 复核固定 `41af2dcf0dfd83c8933f588bb871b7f56dbd4368`：`OptimizerConfig.finalize` 已改为别名规范化→Core validate→finalize_optimizer_config。emerging optimizers 使用 LayerWise 分布；compact layout 默认不打开普通 DDP DistOpt 布局，shard-aligned layout 是另一个 opt-in。`CommOverlapConfig.setup` 为这类 optimizer 保留现有 bucket_size 与 overlap_grad_reduce，除非用户显式覆盖，DP=1 也可能因 CP 仍需归约。不能照搬 Adam/SGD preset 或由一个 flag 推算通信/显存。补采的 `normalize_optimizer_config` 将 `dist_` 前缀规范化，拒绝 Adam/SGD 走 LayerWise，并对 emerging optimizer 把普通分布请求转为 LayerWise、清除普通 DistOpt bool；另拒绝 overlap_param_gather_with_optimizer_step。LayerWise 要求 num_distributed_optimizer_instances=1，当前拒绝与 Megatron-FSDP / Torch-FSDP2 拼接；MegatronMIMO 另拒绝 overlap_param_gather 加 MXFP8 复用 grad buffer。现有 EP 早期约束与普通通信文档未变，仍由固定 Core 再校验，不构成已运行证明。

## 2026-11-18 固定消费者

- [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/training/config.py)
- [src/megatron/bridge/training/train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/training/train.py)
- [src/megatron/bridge/training/pretrain.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/training/pretrain.py)

## 固定证据与复核范围

- [docs/training/communication-overlap.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/training/communication-overlap.md)
- [src/megatron/bridge/training/comm_overlap.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/comm_overlap.py)
- [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/config.py)
- [src/megatron/bridge/training/train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/train.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
