---
id: official-megatron-wiki/training-and-loss
title: Megatron 训练步：数据、loss 归一化、optimizer与数值诊断
engine: megatron
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-megatron-lm
  path: pretrain_gpt.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 37bff81772b4cff0548d94876e9699a66276af578b3902c5bef13fbb5b7af612
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 1cfba3a404c97febc4c2e40895467372e6ab540006dc6a6e22fbc547087a5b75
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 91ec8ceb30b9af6d1bad58256e965e5b1f6cbf70ef120f450b09e570b2f44cce
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 69c5f81b5ec764d5feb1812d152ff592af5291b6b577061841a8b140798cfdd0
- source: nvidia-megatron-lm
  path: megatron/core/rerun_state_machine.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 0098ceed9a9cedfc0fba53aab75aefad8fe8ea8d10711da70965f55500401c03
- source: nvidia-megatron-lm
  path: megatron/core/full_cuda_graph.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 8859a7946d168298e36af1f0ccb02d99c32e8b69a1055aaf155a5d31e628d78f
- source: nvidia-megatron-lm
  path: tests/unit_tests/transformer/test_full_cuda_graph_validation.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: b76d1cca894d212d29cd4c2791398f8a49a6e060ce0fac881b8c1251a6f4d5e6
- source: nvidia-megatron-lm
  path: megatron/training/config/container.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 4965eeb1ad25b950348a29557799fd920f1c2207544c83992eb22e537a8758b2
- source: nvidia-megatron-lm
  path: megatron/training/config/dataset_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ad183c58c35e91b065577d0f3fdb5ef89fbf6282a4e6de1fad1950926c8b030d
- source: nvidia-megatron-lm
  path: megatron/training/datasets/providers.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: a28174f91d974d5ac17d577ed53da2a71af8df16988edca006cc4ccac2c10938
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/optimizer_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: f83b46a8a901bb7c792076544e2fefda3b76830ef2d971ecb976f0ac557fbc67
- source: nvidia-megatron-lm
  path: megatron/core/transformer/multi_token_prediction.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 567b6e3f2a63d9488fdb02780af47dcd26c81a654701c9a5bad4d9d76a266638
- source: nvidia-megatron-lm
  path: megatron/training/config/training_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: f774afdab3d9ec71159b9f4d3ec6fff1cf6e5d307eaf52447d6d6af81bef451a
retrieved_on: '2026-11-04'
---

# Megatron 训练步：数据、loss 归一化、optimizer与数值诊断

## 从 batch 到参数版本

`pretrain_gpt.get_batch`在TP源rank读数据并广播，按CP/packing处理tokens、labels、mask、position/cu_seqlens；model forward返回loss相关tensor，loss callback返回本微批loss、有效token数和report；Core schedule做forward/backward与缩放，finalize-grad/DDP完成所需归并，`train_step`执行optimizer，再决定LR和日志。

当前入口的`BATCH_KEYS`显式固定返回字段顺序，避免数据wrapper附加字段破坏解包。packed/SFT中某PP stage可能只需要cu_seqlens等元数据；不能因为没有tokens就让不必要的rank另读同一数据或修改采样顺序。

## Backward loss 与 reporting loss 分开

默认`loss_func`将输出转FP32，按loss_mask求和，token count由mask求和；report是loss numerator和token denominator。`forward_step_calc_loss`根据callback返回两个或三个值区分legacy与per-token路径：非`calculate_per_token_loss`路径按有效tokens（至少1）和微批数归一化，legacy还有CP修正；per-token路径交由后续token-aware finalize处理。

报告逻辑位于training `train_step`：两个值合并后跨实际DP/CP（某些扩展域还含GTP-remat）归并再相除；SFT的`microbatch` logging mode可对有效微批mean做平均，token模式则按全局有效token加权，处理完全masked shard。单标量legacy report按微批mean。**两个日志数相近/相差都不能直接推断梯度等价**；比较时声明backward与logging的分母和rank范围。

核对padding、EOD、response-only mask、MTP/aux loss、CP切分与packing边界。所有token被mask的微批不会自动意味着“空数据错误”，需结合预期数据与归一化；仍不能让整个窗口无有效tokens被验收。

## Optimizer、跳步与样本进度

`optimizer.step()`返回update_successful、grad norm等；training在model-parallel域合并成功状态，只有成功时推进param scheduler，失败时记skipped iteration。迭代计数、成功更新次数、consumed samples/tokens和LR progression是不同指标；overflow跳步后步号增长不等于参数版本更新。

保持模型官方optimizer语义。当前 `OptimizerConfig.validate()` 对旧 `dist_muon` 发弃用提示，`finalize_optimizer_config()` 再解析 dtype、转向 `muon`/layer-wise distributed path；emerging optimizers与Adam/DistributedOptimizer不是同一个实现。Muon的TP mode、split-QKV、Newton-Schulz precision、checkpoint/FSDP支持有显式条件，不能为了跑通改Adam后仍称原模型适配。后续深查对应optimizer和依赖实现，flags接受不等于数值方法相同。

clip/QK统计、动态loss scale、梯度累积、low-precision master与cached weights要与更新完成状态对应。仅优化fused Adam不能外推Muon；优化某分支首先从实际profile与调用者确认。

## 配置、进度和 Graph 验证的当前所有者

`validate()` 保持纯校验，初始化时的 `finalize()` 一次性落实运行派生值；迭代/consumed/skipped samples、验证计数和累计 FLOPs 由 `TrainState` 负责。旧 args 字段可能仍供兼容入口解析，但不能用它们代替当前循环的运行状态。初次恢复的 resume_iteration/resume FLOPs 与随后累积值分开，重启后的吞吐分子须扣除本次 resume 基准。

GTP sequence sharding 下的样本数使用实际独立序列域，不能继续乘全部 weight-remat ranks；reporting、scheduler、eval 微批和 data 游标需同步采用同一计数语义。权重复制域和 token 域不能互换。

full_iteration Graph 现保留 loss/gradient 检查：在原验证点 clone tensor，replay 后在主机执行 deferred validations，之后才决定 rerun 或 optimizer 更新。旧教程中强制关闭 NaN 检查的要求已移除。复制必须发生在后续 in-place 修改之前，重放后再次保存验证值避免被下次 replay 覆盖；reset/异常还需清理对应 graph 的验证记录。不能把 CUDA capture 中无法同步解释为应永久关闭质量检查。

当前训练循环实际读取 `cfg.train` 的 batch/horizon、`cfg.optimizer` 和 `cfg.scheduler`；`PretrainConfigContainer` 负责按独立 batch 域验证 train/eval 整除、派生 horizon/scheduler steps。改变旧 args 上同名字段不能保证生效。`is_batch_size_transition` 同时检查微批数与 step schedule 的 global batch；配置了保存时转入保存退出/重启，未配保存则告警后继续，不能把它当作任意在线动态扩 batch。

packing 的 `wrap_data_iterator` 每次 train_step 的 rerun 循环只构造一次，并将同一 packed iterator 交给 rerun；日志采用本次 `scheduled_num_microbatches`，避免用原始微批数缩放 MoE/MTP 指标。新增 `tensor_metric_observer` 包住 forward/backward，并在 optimizer step 前观察 finalized、但未必 unscaled 的梯度，不能将其快照直接解释为更新后参数或已 unscale 梯度。

`mtp_loss_early_backward` 在具备 autograd 图且不处于 graph capture/warmup 时，逐 MTP head 执行投影/loss backward、保留 head-input grad 并用 `_MTPHeadGradInjector` 接回主图，及时释放每头 logits；schedule 在 forward 前设置与主 loss 一致的 scale。图捕获/暖机回退 deferred 路径。现有 per-token MTP 归一化仍用 rolled token 的本地计数，源码明确 packed/DP/CP 不均计数要达到精确全局 parity 仍需 all-reduced counts，不能据“early backward”宣称该差异已解决。默认 FP32 mask-sum、schedule 两/三返回值与更新成功后才推进 LR 的契约经当前消费者复核继续保留。

## 阶段数值验证

初始可信checkpoint/样本和loss基线冻结。保存tokenizer/data指纹、seed/RNG、mask/position、optimizer/LR、precision recipe、全局batch/tokens、拓扑与报告定义。小迭代做局部输出/梯度/dispatch和短性能，阶段候选稳定后做较长loss；无需每次微调长训，但不能省去阶段质量验收。

NV环境可从同state/tokens/拓扑可比配置找第一处分歧，再定位embedding→attention/MoE→loss→grad→optimizer；无NV时用可信HCU baseline、保守高精度/非融合小模块、重复运行/首差probe和roundtrip自查。每次比较记录容差来源与dtype/累积/reduction顺序，不能统一套一个误差阈值。

## 数值异常与 rerun

入口在DP all-reduce前检查local NaN/Inf/spiky loss，调用`rerun_state_machine.validate_result`；训练step可以重跑forward/backward并决定checkpoint/exit。先查看原rank、原batch、local first bad value，不能只分析all-reduce后所有rank相同异常。rerun需要一致恢复数据iterator/RNG与saved状态，不随意新增另一个重试循环。

定位顺序：实际tokens/mask/有效token→model/backend输出→低精度scale/cache→loss归一化与梯度同步→optimizer/masterweights→恢复状态。卡在collective时检查rank最早错误与数据消费是否一致；loss仅恢复后漂移转到[checkpoint](checkpoint.md)。已验证阶段边界和长期收敛分别报告，未执行的窗口不写“loss无影响”。

## 固定源码与维护边界

- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/pretrain_gpt.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/training.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/arguments.py)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/pipeline_parallel/schedules.py)
- [megatron/core/rerun_state_machine.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/rerun_state_machine.py)

2026-11-04按上述固定源码、实际消费者与官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。