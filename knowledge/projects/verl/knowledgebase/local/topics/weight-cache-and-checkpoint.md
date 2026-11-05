---
id: engines/verl/topics/weight-cache-and-checkpoint
title: verl：权重发布、LoRA、KV 显存与持久化恢复
engine: verl
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-04'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: volcengine-verl
  path: verl/workers/engine_workers.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 23c8053c2b3c555de5b37fbe27b7be664cf5b884e6c64ea7be1cd85402b30dfe
- source: volcengine-verl
  path: verl/trainer/ppo/ray_trainer.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: eb41f99ccc66976eab14ebe35aa1aa5b7318e02469240ef1569ac4c884c94312
- source: volcengine-verl
  path: verl/workers/config/rollout.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 6364128a35597a6c84cb2f93bede7d84cb80ad123df5ccf96904fb7f2d111684
- source: volcengine-verl
  path: verl/utils/checkpoint/checkpoint_manager.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: be4fa702f0fab63dfb1d482716d31bc13a3b8f5129adbbd61872a169b07cbbc6
- source: volcengine-verl
  path: verl/workers/rollout/sglang_rollout/sglang_rollout.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: b6facb4d512ce63067014fbb0436eed7398228cd1c4673dbbe4b7e2c4e3612a1
- source: volcengine-verl
  path: docs/perf/rollout_kv_offload.md
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: a48c054870d0ae8c248fe318de42538e7feb146c1ae3c1c08c62f8acbb758949
- source: volcengine-verl
  path: verl/utils/qat/__init__.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 5f9124b85745540537b87520c923eb2b380e31613e9c9ca137477c795a02a1b5
- source: volcengine-verl
  path: verl/utils/qat/compressed_tensors.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: a59fb2be3b8d6d96b9a573e17d073178a58ba67fd17b9587cbac04ec873edc30
- source: volcengine-verl
  path: verl/workers/engine/base.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 58057882c03110cdcf846fd833085e01e3f517a17dd9400f3c0d0e4bdba6500a
- source: volcengine-verl
  path: verl/workers/engine/megatron/transformer_impl.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 405dcf1962348a774efa006a08fe13176199fd5fcae1cf4e98b3cfb507b62cff
- source: volcengine-verl
  path: verl/utils/sglang/sglang_quant_utils.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: c3cecc121e0f4f595e9d9fa4ecc5d8a90cbcd73d3ac0e7d6c03ad942194164ae
- source: volcengine-verl
  path: verl/workers/engine/fsdp/transformer_impl.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 49bac0d824b5af3cd5f43e939a8f042eddeb002ed94cd721fd6f05c8e52c6bce
- source: volcengine-verl
  path: verl/utils/real_nvfp4/megatron.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: d2c51b072bdfdbcdffa6c8cb77e57f97a4de5f7f867832764c6efc8d45825829
- source: volcengine-verl
  path: verl/utils/megatron/low_precision.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: e2dfe5523dd731f2baddc04d5a8bf60560592e41d977e24f51f33bbab361aa08
- source: volcengine-verl
  path: tests/utils/real_nvfp4/test_nvfp4_per_token_on_cpu.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 87e55711ce33938f42798190271a473c6cecab061f709480b9e1fe083853f322
- source: volcengine-verl
  path: tests/utils/real_nvfp4/test_nvfp4_per_token_refit_on_gpu.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 97333af45cede7aa7d3c6db3af084c9a2ca849a60647a55a831b9aa4bdef3d2e
- source: volcengine-verl
  path: tests/utils/real_nvfp4/test_training_guards_on_cpu.py
  commit: 31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe
  sha256: 3154018aec563be362d2a79b8ad76af13fd38e39cdc345bde36e9149eab0f160
---

# verl：权重发布、LoRA、KV 显存与持久化恢复

## 先分清两类 checkpoint

rollout 的 `checkpoint_engine` 用于把训练策略权重送到生成后端；训练持久化checkpoint用于故障后恢复model/optimizer/进度。两者同含checkpoint名称，状态、完成标记和恢复范围却不同。不能用一次成功update_weights证明磁盘恢复可用。

[`ActorRolloutRefWorker.update_weights`](https://github.com/verl-project/verl/blob/31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe/verl/workers/engine_workers.py)通过mode选协议：auto使用rollout配置backend；naive是同步共进程；其他模式交给`send_weights`。delta_sharded把训练engine交给backend，由其管理seed/steady/snapshot，不能将它解释为普通逐tensor发送。

## naive 路径的显存顺序

调用前rollout应sleep，当前固定代码执行：

1. 暂停expandable segments、清理设备cache。
2. 必要时恢复weights。**SGLang sleep level1保留weights，不应再次resume；vLLM level1仍会unmapweights，需要resume**，这是不能泛化的backend差异。
3. 从训练engine导出HF命名权重/peft配置。未mergeLoRA首次需要base，再更新adapter；merge时发送完整权重且peft配置为空。
4. 等待rollout更新完成；若param offload开启，训练model转CPU（optimizer/grad不随这一调用转移）。
5. 设备synchronize/empty_cache；**free_cache_engine时所有训练rank通过barrier之后才恢复KV cache**，避免leader恢复KV时其他rank尚未卸载导致peerOOM。
6. 设置base_sync_done并恢复expandablesegments。

这个barrier是跨rank内存状态的协调，不等于一般通信overlap。仅local synchronize不能保证其他rank腾空；也不能提前wakeKV换表面更短同步时间。设置base_sync_done只记录本地协议状态，参数实际发送和生成端版本仍需确认。

## 分离式、LoRA与性能账本

非naive模式由backend决定参数迭代/reshard、传输、接收、版本发布和错误处理；sender await完成的含义继续到具体backend查，不能以driver global_steps替代全部receiver就绪。该分支发送后同样可能offload训练model。

LoRA至少记录merge/base/adapter、首轮base_sync_done、sleep level、目标模块/参数命名、推理backend支持。缓存flush、旧prefix/KV和参数版本关联需由所用引擎协议核对。首次base传输、稳态adapter传输和全权重传输是不同性能窗口。

计时拆成trainingexport/gather、host staging、wiretransfer、server reload、cache恢复；显存包括训练参数/optimizer、推理weights、KV和临时转换副本，CPU还含snapshot/压缩和pinnedbuffer。[KV offload教程](https://github.com/verl-project/verl/blob/31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe/docs/perf/rollout_kv_offload.md)提供另一套容量/IO权衡，不能把KV与optimizeroffload混作同一功能。

## 结构化 rollout 量化与 trainer 导出

当前 `rollout.quantization` 已是 `RolloutQuantizationConfig`，按 `linear`、`moe`、`ignore` 或完整 `config_file` 描述 compressed-tensors 方案，不能继续把旧字符串 `fp8` 与 `quantization_config_file` 当相同 schema。显式 override 优先，否则保留模型原有 quantization_config；原始参数、量化权重、scale 与推理 loader 要来自同一契约。

`ActorRolloutRefWorker.init_model` 用 `dispatch_rollout_weight_quantizer` 选择 trainer exporter，再调用 engine 的 `set_rollout_weight_quantizer`。Megatron `get_per_tensor_param` 先按 HF 名称导出，过滤训练 quantizer 内部状态，并在非 adapter-only 时按当前scheme量化；旧 `refresh_input_global_scales` 路径已移除，SGLang adapter 旧的临时 BF16→FP8 helper 已移除，不能在两端重复转换。BaseEngine 默认对未实现的 trainer-side 量化明确拒绝，接口登记不等于所有 backend 都支持。

QAT 训练与 rollout 量化是两层设置：启用 QAT 却没有目标 rollout quantization_config 会报错，QAT mode 与导出 scheme 不匹配也拒绝。原生 FP8 与 compressed-tensors 由不同 exporter 处理，特殊模型已打包布局还可能选择保留原导出。验证要同时比较名称/layout、weight/scales、首轮/重复同步及固定输入 logprob，不只看 receiver dtype。LoRA adapter-only、量化base与缓存版本应分别验收。

源代码可说明新职责，但本轮没有执行量化训练、HCU refit 或全模型数值回归；不把配置解析成功写成可部署。

### NVFP4、派生 scale 与部分 refit 失败

当前 `RolloutQuantizationConfig` 新增 `moe_activation`；`moe=NVFP4`默认并强制 `nvfp4_per_token`，只适用vLLM routed experts。trainer导出gate/up共享的weight_global_scale，input_global_scale固定1，实际activation scale由每token运行计算；不再从QAT observer刷新静态input scale。缺gate/up另一半报错，real NVFP4训练的BF16首尾层也必须与export ignore匹配。DeepSeek-V4的原生混合布局禁止用普通override替换。`delta_sharded`稳态会绕过trainer quantizer，因此当前对量化rollout显式拒绝。

旧FSDP QAT训练/导出接线及公开 `QATConfig/apply_qat` API已删除，不能沿用旧FSDP配方。Megatron ModelOpt QAT与真实TE低精度GEMM不同；QAT+TE FP8拒绝，真实NVFP4的module recipe、BF16 carve-out与runtime attestation也要验证。packed 3D experts的普通FP8_BLOCK/MXFP8/MXFP4导出先整体量化再拆名字，要求高精度CUDA tensor，额外考虑组内padding和FP8 block对齐；源码使用CUDA判定不等于HCU已验。

SGLang的all-MXFP8配置会翻译为native格式并改scale命名；MXFP4/MXFP8 refit需要 `LOADER_FQN`，每个bucket加载后还发送 `FINALIZE_MARKER`，才重建backend布局并在随后flush cache/设置版本。混合MXFP8 dense+MXFP4 experts及 `delta_flush`+自定义量化refit被拒绝。不是每bucket都完成后处理，也不能把第一次RPC返回当整轮就绪。

`load_and_reprocess` 在异常时 `_abandon_sync` 恢复被staging替换的live storage引用，但没有保存并回滚全部已写参数；早期bucket或部分layout后处理仍可能发生。控制端超时也不能证明远端未写。失败后按实际receiver状态重建一致baseline并验固定输入logprob，不能原样重试后直接宣布原子发布。参见[固定loader](https://github.com/verl-project/verl/blob/31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe/verl/utils/sglang/sglang_quant_utils.py)，不要把更晚SGLang/vLLM主干的另一套事务API套到此consumer。

固定CPU测试覆盖NVFP4 per-token scheme、carve-out、缺半对和runtime guard；`test_nvfp4_per_token_refit_on_gpu.py` 是量化对照入口。本页只阅读设计，未运行GPU、HCU或全模型回归。

## 持久化 save/load 与数据进度

[`RayPPOTrainer._save_checkpoint`](https://github.com/verl-project/verl/blob/31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe/verl/trainer/ppo/ray_trainer.py)保存`global_step_N/actor`、可选critic和`data.pt`（statefuldataloader）；同步路径再写latesttracker。async_save时driver明确跳过写`latest_checkpointed_iteration.txt`，需确认实际backend的完成/恢复选择协议，目录出现不证明可用。

`_load_checkpoint`支持disable/auto/resume_path，目前HDFS恢复明确未实现。恢复actor/critic后处理data.pt；若globalstep恰在epoch边界，刻意不恢复耗尽的dataloader，让新epoch重新迭代；缺data.pt则警告从头读数据。model加载、optimizer恢复和数据准确接续分别验证。

HCU父仓如果patchMegatron的asyncpreload，联查父仓和固定MCore依赖确认D2H实际阻塞/异步、后台hosttensor所有权及staging完成边界，不能由外层async_save名称判断实现。本页只解释官方实现，不将私有patch细节复制为上游事实。

Megatron `load_checkpoint` 的新顺序还要求在恢复前onload optimizer：HybridDeviceOptimizer会在load_state_dict内按参数is_cuda重建其子optimizer，若仍停CPU可能缺pinned副本并在第一次step发生设备/KeyError。加载结束再按原配置offload；只确认模型参数读回或save目录存在不足以验收该路径。

## 验收、排障和更新

对共卡/分离、SGLang/vLLM、普通/mergeLoRA/adapter、首次/稳态分别验证。保存→停机→恢复时比较step、数据位置、参数/optimizer与首批rollout概率；模拟部分receiver失败时确认拒绝发布或可重建一致baseline，不能只重试driver整数。

OOM先查每rank的weights/KV恢复时序和peak；版本错查传输backend/缓存而非只调采样；恢复缺状态则标明降级范围，不宣称无损续训。更新engine_workers或后端sleep协议时联动[总览](../overview/engineering-guide.md)、动态批次专题和HCUpatch/依赖。本页未在HCU或NVIDIA执行训练/恢复。


## 本轮补充固定证据

- [verl/utils/qat/__init__.py](https://github.com/verl-project/verl/blob/31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe/verl/utils/qat/__init__.py)
- [verl/utils/qat/compressed_tensors.py](https://github.com/verl-project/verl/blob/31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe/verl/utils/qat/compressed_tensors.py)
- [verl/workers/engine/base.py](https://github.com/verl-project/verl/blob/31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe/verl/workers/engine/base.py)
- [verl/workers/engine/megatron/transformer_impl.py](https://github.com/verl-project/verl/blob/31cfccb4dbad8f1f4aa41a34eb589afbe283e8fe/verl/workers/engine/megatron/transformer_impl.py)
