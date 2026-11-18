---
id: official-torchtitan-wiki/titanrl
title: TitanRL：训练生成协同、权重同步与精度边界
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-11-18'
retrieved_on: '2026-11-18'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/rl/train.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 63d83a8ee812a76d4d04abbff5d4a5821074a703145757ebf4904a2cdc551a78
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer/trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: f52d1d78a769b06bc511dc638486626592d0f0bdbd249d14a2f8df4107d0c3b3
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3b46f79840dec9f3efd25319247fe259c0009daeec74bf381d06c483ddea8b09
- source: pytorch-torchtitan
  path: torchtitan/rl/BITWISE_PARITY.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 830da7e6052e07ab5a9cc302436dc1ece1d97955a4fa28b66ec8e9833e2f3ac7
- source: pytorch-torchtitan
  path: torchtitan_recipes/rl/model_configs.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: d62f1526bb38cb195554426f9f19d7f688f7f0c84c52ec8e905159709e1499e8
- source: pytorch-torchtitan
  path: torchtitan/rl/observability/metrics/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 97fa0871d9c44375c0a5fdf4508f61c2749b6a35c62ba3d43ee13e98945bab83
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/generator.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: fe3ccd0288aa613d11234607fa24e91e98953015dd75a49657da0b4c7dd56b01
- source: pytorch-torchtitan
  path: torchtitan/rl/controller/controller.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 8103ebbdfd0f36476fd7f46cfb9acc748b978f297e6ae92009d62722da68f6fc
- source: pytorch-torchtitan
  path: torchtitan/rl/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: c4f1816a03546f6ffd5d800a3008aedfdf24a9fa34161a6cfa3fb5cae6184c72
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/system.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 7733d646cda32114febac5a669f9beb12be8445c864d8b540bc908f240e1650a
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/system.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: fe63bfd041a5f03d4f8afc4f80b77f1085c7c808ae2b4a2d3cf4786b938c1bb9
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 529598c47479754fb689dcc3f852daae28ad60c926f479f284cbcb8fcaa7f9fc
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/generator.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 7d5cdae138c14aeb9e037a294734d78c85817bfbf6e09788ec9a6127bd1ab0e9
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/engine_loop.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 08690a20311acba28c61b8ca65a2062da4bbfd0ee2cb2168b50543887dd401b0
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/dispatcher.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 4f4324b3a4afb7d6c0a1c687d27275a52a3d887ff8f88b642f65a0ed840f26cb
- source: pytorch-torchtitan
  path: torchtitan/config/transform/freeze_moe_routing.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 985eee889df806f156a8545a93baff4450c0fde0980786a6cdf7ecfcc4c1faa8
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_model_defaults.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 44bf357ff2ddfa185feca23384b2152168c25c0727dcc253f14616e36c6e2427
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_engine_loop.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: b9a5defb95961aad5fab4f6cf65705e2e118f74d5292f1b89e3e785b7cc85c0f
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/vllm/model_wrapper.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: dfd3054a05f24eefa3e7bfaa5ffc24433700ede8579e53d8371277ae9a0f56e8
- source: pytorch-torchtitan
  path: torchtitan/config/configs.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3465866709813651cc91114c4a006a5cc3c05d6069e9f04200e68d10c91c3659
- source: pytorch-torchtitan
  path: torchtitan/rl/controller/controller.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: e7111207a551e02c27b80dc4059b354353204dcbfb1d1af6ab54f423212c941b
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/generator.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: b88fa03663902dc27ba4c48da13627bab556804b8e2314a506c9634273fb715a
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/engine_loop.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 026acfe34ddeefe069614ac2a10e2a17501820d0e260a5ed8afe0c2fe89d4c8e
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/model.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: d0cd8f39610905786265c3b8926e33f23285533d9b1e1dc5013d411e78c7d7df
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer/trainer.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 4204515230aac8cee7d9cc836b3709b4b66ca461335f72d21146c17cd1cc9ffb
- source: pytorch-torchtitan
  path: torchtitan/rl/MODEL_STATE_DICT_TRANSPORT.md
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: c0a9a44177743c4f3acf3cfb803f0944f48b69174078bf777c5cd32171eed92b
- source: pytorch-torchtitan
  path: torchtitan/rl/model_state_dict_transport.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 13f48f0ed2b0a6b422000979b5463895c5e474f621932e5ffe24cf9eef9f5592
- source: pytorch-torchtitan
  path: torchtitan_recipes/rl/model_configs.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: fe0da78525a977441c3d762b4cbfef36485de6b9c206dd593e11cd9c3e55ff00
- source: pytorch-torchtitan
  path: torchtitan/config/transform/disable_moe_load_balancing.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 6cc86786d375364ed32b0f894f35649a017e782f41fa81582516c08bb772904e
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_model_defaults.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 3a7e87bc9f400f044ebdca7ead6807f672c8d2cc60424b47ebfc8df2611a157a
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_engine_loop.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 248e42247c43e0274a5d1d2efdf2e99021fa12fb8a6fda80d848c6d2bc21da6d
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_model_state_dict_transport.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 545285c0ebd315d40efa3de6bb8be82f0f5a0799b03ca5292530befe74fa04fe
pr_sources:
- pr-pytorch--torchtitan-5107
- pr-pytorch--torchtitan-5268
- pr-pytorch--torchtitan-5280
---
# TitanRL：训练生成协同、权重同步与精度边界

## 组件分工

TitanRL 由 Controller 协调 trainer、generator、rollouter、数据、环境/奖励和 work buffer；经 ActorSystem 组织进程与任务，默认实现为 Monarch，使用 ModelStateDictTransport 传输 model state dict（显式 None 才走 TorchStore），生成侧由可配置engine（当前默认vLLM）对接TorchTitan模型。训练侧复用 `TrainingEngine`，并非把监督 Trainer 的一轮循环直接改个 loss。

trainer 与 generator 各自有并行配置、资源和模型 Config；`build_rl_model_configs` 一类构造器分别建立布局。可以布局不同，但模型语义、参数映射和权重版本必须一致。RL 安装/启动由其独立入口和脚本负责，不能用普通 `run_train.sh` 的默认预训练配置假定已经启动全部组件。

## 同步与异步的可观测语义

`target_offpolicy_steps=0` 对应同步策略；正值允许一定策略滞后。队列深度、windowed FIFO 与慢 rollout 会影响样本年龄，不应只看平均生成 throughput。需要保存 rollout 使用的 policy version、trainer 更新 step、生成器已应用版本、队列等待、token 长度分布和奖励/优势统计。

`windowed_fifo_batches` 的有限窗口可限制批次拖尾与策略滞后，但也改变吞吐与调度。调参需要同时观察训练有效利用、生成端 KV/显存、样本年龄和训练质量，不能把更快收集旧策略样本当作无条件收益。

## 显式 TorchStore 路线的权重同步时间线

```text
optimizer N 完成 → push stream 依赖该更新
  → worker 等待 push stream，以 live tensor 调 TorchStore PUT（direct_rdma=False）
  → StorageVolume 稳定快照
  → generator cpu_prefetch 后应用，或暂停 engine 后 gpu_fetch
  → 所有 generator 完成该版本 load，才释放下一批 rollout groups
下一轮 forward/backward 可与 push overlap
  → optimizer N+1 修改原权重前等上次 push
  → 下一次 push 覆盖 key 前等上次全部 pull
```

显式 TorchStore 路线的 trainer 不再自建完整 pinned CPU mirror；当前默认新 transport 另有 pinned staging。SharedMemory transport 可直接复制/转换到 StorageVolume，其他 transport 可能先产生分批 GPU cast；不能称为通用 GPU-to-GPU 零拷贝。live tensor 在 PUT 完成前必须保持权重稳定，下一轮 forward/backward 不得修改 persistent model state；线程只保持 asyncio 响应，不取消同步所有权。详见[权重同步案例](../cases/rl-weight-sync-memory.md)。

## Trainer / generator 数值一致性

官方 bitwise parity 方法包含 batch-invariant 配置、确定性策略、匹配 TP/序列布局、计算与主权重 dtype、相同 attention/logprob 处理。某些设置限定 NVIDIA FlashAttention、collective 算法或 TF32 行为，不能直接作为 HCU 的环境配方。

排查顺序：相同 checkpoint 和 policy version → 相同 token/mask/position → logits/selected logprob → 前向 backend 与 dtype → TP/SP/CP 分布 → sampling/reward/advantage → 训练更新。batch-invariant 与严格确定性可能有性能代价；保留用于定位的严格模式，再决定正式训练需要的容差与性能配置。

没有 NVIDIA 环境时，仍可在同一 HCU 上比较 trainer 与 generator、保守 eager 与优化后端、固定 batch 与变 batch，找第一个不同的 tensor；有 NVIDIA 环境也需同语义和版本，不能直接比较两个不同默认配置。

## 支持范围与诊断

当前官方 RL 支持表中的许多结果只是两步 debug 验证。不能从某模型的预训练支持推导 RL 支持，也不能把计划中的 Kimi/DeepSeek 路线写成已可用。高价值入口：

| 现象 | 主要证据 |
| --- | --- |
| 首次 sync OOM | trainer 临时 cast、pinned CPU snapshot、generator FSDP group、KV cache 预算 |
| 同步卡住或偶发旧权重 | push/pull future、权重版本、buffer/key 复用、远端 worker 异常 |
| 生成很快训练仍空闲 | rollout 长尾、队列/backpressure、奖励服务、不同角色资源占用 |
| loss/reward/logprob 漂移 | policy age、数据处理、数值配置、KL/优势与采样参数 |
| 恢复后重复数据/版本错位 | Controller、数据队列与模型/optimizer checkpoint 的一致性 |

移植时复用 HCU 已有 RL/推理引擎能力，必要时读底层库对应分支；不要因为官方采用某个 NVIDIA kernel 就重写整个 RL 系统。

## 当前角色配置、输入传输与数值默认

`Controller.Config.actor_system` 默认构造MonarchActorSystem，负责provision、spawn和stop；领域服务不直接依赖Monarch，trainer handles按DP列组织，generator通过router访问。launcher自有hosts时传入预建actor system。显式 TorchStore 路线的 storage 与 trainer mesh 同置，并为每个trainer/generator rank初始化client；移植需同时满足handle调用约定、进程生命周期、DP列分发和传输所有权，不能仅替换class名字。

`build_rl_model_configs` 当前默认给trainer和generator都设FP32-output LM head，并冻结 expert bias、去掉 aux load-balancing loss，router gate 继续训练，保持对齐。它改变可训练参数/优化器状态与目标，不只改变计算速度；显式关闭任一默认时两侧一起复核。某些SoftCappedLinear配方不能应用同样head converter，测试保留例外。vLLM config转换还要保留YaRN scale、首个full-attention选择和sharding；相同模型名不足以保证logprob一致。

RDMA microbatch是数据传输优化，和TorchStore模型快照不是同一路径。未开lazy preprocessing时，RDMA tensor仍会全部先读完再前后向，不能宣称已overlap。当前 Controller 仍拒绝 RDMA+PP；旧 RL Trainer 的统一 CP>1 拒绝已随 per-token loss kwargs 进入模型/CP 预处理而移除，实际模型支持仍需验证。lazy preprocessing要求关闭CUDA graphs且无SDC replay；逐group Graph有不同的归约与metadata要求，见[编译通信](compile-fusion-and-communication.md)。RL optimizer-step边界由 `async_loop.num_prompts_per_train_step` 控制，普通 `training.num_tokens_per_train_step` 会被忽略并警告。

## 精度、load mode 与恢复状态

`Controller.Config.precision` 统一传给 trainer/generator；generator 在基础 `dtype` 构造模型并保留 buffers/受保护参数，其余权重用 `param_dtype`，vLLM compute dtype 必须一致。旧独立 `generator.model_dtype` 不再是当前接口。FP32-output LM head、冻结 expert bias 与无 aux loss 默认保留，router gate 继续训练，并有 SoftCappedLinear 配方例外；不能把 logits FP32 当作全部权重都强制 FP32。

`model_state_dict_load_mode="cpu_prefetch"` 默认保留应同步 trainable 参数与 buffers 的 generator pinned CPU 副本，生成期间预取；`"gpu_fetch"` 不分配该副本，逐 FSDP group 直接读 StorageVolume，但传输发生在 engine 暂停期间，hot-swap 请求会等待，非 hot-swap 则保持 drained。gpu_fetch 拒绝量化参数；每个本次应同步的 trainable 参数 key 必须填充；frozen base 按初始 checkpoint 合同排除，不能靠 `strict=False` 跳过应更新参数。失败可能留下部分新权重，engine loop 在所有 generator ranks 停止，不继续生成。

恢复状态改为 checkpoint extra state `"resume"`；`MirroredState.value` 是新提交、`.loaded` 是恢复值，Controller 用 `get_resume_state` 恢复 rollouter。旧 checkpoint schema/数据游标迁移需显式验证，不能把一次 load 当作样本流完全连续；当前恢复仍有重新生成 pending prompts 的 TODO。

## 固定证据与使用边界

本页保留官方 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 的固定历史证据；2026-11-18 新实现按 `361ae5df6280e578614026b206d801d6ea1baf98` 逐项复核，见本页增量。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/rl/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/README.md)
- [torchtitan/rl/train.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/train.py)
- [torchtitan/rl/trainer/trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/trainer/trainer.py)
- [torchtitan/rl/generator/generator.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/generator.py)
- [torchtitan/rl/actors/monarch/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/monarch/README.md)
- [torchtitan/rl/BITWISE_PARITY.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/BITWISE_PARITY.md)
- [torchtitan_recipes/rl/model_configs.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/rl/model_configs.py)
- [torchtitan/rl/observability/metrics/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/observability/metrics/README.md)

- [PR #5107：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5107.md)
- [PR #5268：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5268.md)
- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)

## 当前请求失败与模型版本等待

PR #5182 引入的单请求失败边界在本固定代码中移到 `generator/engine_loop.py` 与 `generator/dispatcher.py`：engine admission的rejected请求回送相应错误，其他请求继续；loop异常则失败outstanding、排队load/generate与后续调用，并释放engine资源。`wait_engine_loop`让controller观察loop异常；旧 `_rank0_drain_results` 的私有回调/TODO不能继续作为当前源码入口。CPU `test_request_rejected_at_admission_fails_alone` 与 `test_crash_fails_outstanding_and_queued_calls_and_later_calls` 分别覆盖两种边界，仍不替代真实多rank故障测试。

`load_model_state_dict(version, drain=...)` 排队等待引擎在step间应用；同一批load请求可合并到最高version，再统一完成reply。Controller等待push与所有generator pull完成后才释放下一批rollout group，早完成的generator仍可能等待慢者。session affinity释放、drain与模型版本等待属于不同依赖，不能把合理等待当死锁而任意重路由。

当前启动输出参数为 `--output-dir`，资产和角色配置由recipe提供。升级要同时核对Controller、ActorSystem、Generator engine与配方；以上为固定源码和上游测试阅读，未进行新的RL现场恢复实验。

## 本次补充的实现与测试依据

- [torchtitan/rl/actors/system.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/system.py)
- [torchtitan/rl/actors/monarch/system.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/monarch/system.py)
- [torchtitan/rl/actors/monarch/trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/monarch/trainer.py)
- [torchtitan/rl/actors/monarch/generator.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/monarch/generator.py)
- [torchtitan/rl/generator/engine_loop.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/engine_loop.py)
- [torchtitan/rl/generator/dispatcher.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/dispatcher.py)
- [torchtitan/config/transform/freeze_moe_routing.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/transform/freeze_moe_routing.py)
- [tests/rl/unit_tests/cpu/test_model_defaults.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/rl/unit_tests/cpu/test_model_defaults.py)
- [tests/rl/unit_tests/cpu/test_engine_loop.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/rl/unit_tests/cpu/test_engine_loop.py)

- [torchtitan/rl/generator/vllm/model_wrapper.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/vllm/model_wrapper.py)

- [torchtitan/config/configs.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/configs.py)


## 2026-11-18 固定主线复核

按 `361ae5df6280e578614026b206d801d6ea1baf98` 的实际消费者和来源测试设计复核：

权重传输默认 `ModelStateDictTransport`（NIXL，可选 Mooncake），通过 torch 私有 `_transport` 的 one-sided reads，初始化按 trainer/generator shard boxes 预规划并注册 pinned staging/prefetch。它不经过 StorageVolume/key，trainer 重新保留一份按目标布局准备的 CPU staging；`model_state_dict_transport=None` 才走原 TorchStore，且 `gpu_fetch` 当前要求 None。相同 dtype/preserve-key、分片完整覆盖、无重叠、拒 Partial/uneven StridedShard 是准入，不能只测链路带宽。

push stream 依赖 optimizer 完成，stage 的异步复制完成后 generator 才能读；下一 optimizer 修改 live tensor 前等 push，下一 push 重写 staging 前等全部 pull。packed prefetch 回填后还须等 copy 才能复用 buffer。read_timeout 默认 600 秒，超时仍有在途写、prefetch 未定义，来源要求重启，不允许简单重试同 buffer。Mooncake 文档还明确要求 Torch nightly≥2026-11-10，而该提交安装脚本所配 vLLM wheel 仍约束较早 Torch；这是一项未解决配对缺口，不把默认可配置等同可用，更不升级 HCU 环境。

`ModelStateDictLoader.load` 与构建逻辑移到 `rl/generator/model.py`。同步只带 trainable parameters 和 buffers，冻结参数（如 LoRA base）来自 generator.checkpointer；没有则硬拒。混合 FSDP group 加载时先从既有 unsharded 值补回 frozen shard，防止未初始化数据 all-gather 覆盖 base；纯 frozen group 不再重载，量化 frozen/trainable 混合有明确拒绝。旧每 key 覆盖要求作用于本次应同步参数，不能要求被设计排除的 frozen 参数也来自 push。

RL 默认现为 `disable_moe_load_balancing=True`，只冻结 expert bias 并去 aux loss，router gate 仍训练。`Generator.generate` 接受 `Prompt`（token IDs、图像字节），不再接裸 token list/metrics_prefix；vision_processor、模型 text/mm 资格和 M-RoPE 配置要三方一致。源码有 SGLang engine 入口，但不据此推断任意模型/HCU/ABI 已通过。

`load_model_state_dict(version, drain=...)` 新增显式排空：True 停止新 admission、继续已 admission 请求，归零后加载，再放入等待请求；False 在下一决策 hot-swap。已排队但未 admission 请求不计排空，否则会死锁；同批 load 仍合并到最高版本。单请求 rejection 与整个 engine 故障继续分开。

Validation 现可与训练并行，默认保留 step0、可设 freq、默认 defer 防堆积，结束后才打日志并带 started_at_step；期间权重可能变化，不能称固定单策略评测。final validation 默认关闭。cancelled validation 可能仍留住请求/组直到 close，异常训练路径在途 push/pull 收尾也有 TODO；恢复不会自动续上未完成 validation。按实际结束/失败/关闭证据验收，不将未解决的任务生命周期写成已恢复。

生成并发上限现由训练 rollout 在每个 generator DP rank 的份额推导两倍余量，向上取二次幂并受 batched-token budget/FA2 profile 条件约束，不能沿用旧固定512或将其当可达并发保证。已读 engine-loop、model-defaults、transport CPU 测试，未运行上游或 RDMA/设备/训练验收。

固定入口：[torchtitan/rl/controller/controller.py](https://github.com/pytorch/torchtitan/blob/361ae5df6280e578614026b206d801d6ea1baf98/torchtitan/rl/controller/controller.py)；[torchtitan/rl/generator/generator.py](https://github.com/pytorch/torchtitan/blob/361ae5df6280e578614026b206d801d6ea1baf98/torchtitan/rl/generator/generator.py)；[torchtitan/rl/generator/engine_loop.py](https://github.com/pytorch/torchtitan/blob/361ae5df6280e578614026b206d801d6ea1baf98/torchtitan/rl/generator/engine_loop.py)。本次未安装或运行上游测试/训练，没有 HCU 设备实测结论。
