---
id: doc-baidu-baige-loongforge-b0c102ad7b55a80cf961
title: baidu-baige/LoongForge / docs/source_zh/features/fp8_grad_comm_hook.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source_zh/features/fp8_grad_comm_hook.md
raw_sha256: a0bfc1d4fd56296cf3b8ba1c1c6c20f5ebe35e6a7b4e3b048627df5359b0cde5
sources: []
generated_body_sha256: cc2b6f84558ac9a710438b50f5db18f40ade02c8f2c69be0e398c6ecb63ea9f3
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source_zh/features/fp8_grad_comm_hook.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source_zh/features/fp8_grad_comm_hook.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# DDP FP8 Grad AllReduce

DDP FP8 Grad AllReduce（`fp8_a2a_allgather_hook`）是 LoongForge embodied 训练栈中一项可选的 DDP 通信优化。它把每个梯度 bucket 量化成 FP8 E4M3，走 AllToAll，本地按 FP32 reduce，再重新量化并用 AllGather 把结果收回，从而压缩梯度 all-reduce 的通信量。该功能只改变通信精度，不影响 forward / backward 计算。

本 hook 作用于 **DDP 下的梯度**，是 [FSDP2 Delta-FP8 Param AllGather](delta_fp8_allgather.md) 的 DDP 对应物——后者压缩的是 **FSDP2 下的参数** AllGather 通信量。按并行策略二选一，两者不同时使用。它们都与 LoongForge 端到端 [FP8 训练](fp8_training.md) 相互独立，不会把权重、激活或 GEMM 转为 FP8。

## 1. 使用条件

- DDP 数据并行，并通过 `--ddp-comm-hook fp8_a2a_allgather_hook` 注册本 hook
- CUDA 设备与 NCCL 分布式后端
- compute capability 8.9 及以上的 NVIDIA GPU
- PyTorch FP8 E4M3 支持，以及暴露 `tl.float8e4nv` 的 Triton 后端

小于 `--ddp-comm-hook-fp8-min-mib` 的 bucket，以及会超出 scratch 预算的 bucket，会回退到全精度 AllReduce 而不是让训练失败，因此不受支持或超预算的 bucket 会优雅降级。

## 2. 使用方法

在 DDP embodied 启动脚本上追加 hook 参数：

```bash
bash path/to/ddp_launcher.sh \
    --ddp-comm-hook fp8_a2a_allgather_hook
```

精度敏感排除默认开启（`--ddp-comm-hook-fp8-exempt 1d,embed`），能以极小代价挽回大部分 FP8 loss 偏差。通信路径支持本身并不保证对每个模型都数值/性能适用。在其他配方中采用前，请对同一模型的全精度 DDP baseline 校验 loss、单步时间和峰值显存。

## 3. 配置

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--ddp-comm-hook` | `None` | 设为 `fp8_a2a_allgather_hook` 启用本 hook |
| `--ddp-comm-hook-fp8-block` | `256` | 共用一个 FP32 scale 的元素数；`[1, 1024]` 内的 2 的幂。越小越贴合局部动态范围，但每 block 多 `4/block` 字节上线（256 时为 1.6%） |
| `--ddp-comm-hook-fp8-min-mib` | `8.0` | 小于此值的 bucket 走普通 AllReduce；`0` 则量化所有 bucket |
| `--ddp-comm-hook-fp8-max-scratch-gb` | `24.0` | 所有 bucket 的常驻通信 scratch 总量（约每桶 1.15x）。超预算的 bucket 降级为 AllReduce；没有能取消该上限的取值 |
| `--ddp-comm-hook-fp8-exempt` | `1d,embed` | 逗号分隔的参数类别，保留在精确 FP32 跨卡均值上（见 4.1）；`''` 关闭 |
| `--ddp-comm-hook-fp8-error-feedback` | `none` | `none` / `allgather` / `both`——把某量化点的残差带入下一步（见 4.2） |

除非有匹配的 loss 与性能校验支撑，否则保持默认 block 大小。

## 4. 工作原理

对每个可量化的梯度 bucket，hook 执行：

1. 按 block 把 bucket 量化成带 FP32 scale 的 FP8 E4M3 payload。
2. AllToAll 交换 payload，使每个 rank 持有所有 rank 贡献的一个 shard。
3. 本地按 FP32 reduce 自己那个 shard。
4. 对 reduce 后的 shard 重新量化，并跨 rank AllGather。
5. 把收回的各 shard 反量化写回 bucket buffer。

由于每个 rank 都对**同一份** AllGather 结果反量化，最终 bucket 在各 rank 间逐位一致。这条路径上有两个有损量化点（AllToAll 前的 bucket、AllGather 前的 shard），它们的 E4M3 取整误差是系统性同号的，而非零均值，因此长程会累积成相对全精度 baseline 的 loss 偏置。下面两节介绍两种独立、正交的抑制手段。

### 4.1 精度敏感排除（`--ddp-comm-hook-fp8-exempt`）

FP8 block 量化对 1-D 张量（RMSNorm/LayerNorm scale、bias）尤其狠：它们元素少，却要和量级大得多的邻居共用一个 256 元素 block scale，尾数被整体拉偏。这些 1-D scale 直接乘在激活上，对 loss 高度敏感，embedding 和输出头同理。排除方案把这一小撮精度敏感参数从 FP8 路径里摘出，改走精确 FP32 跨卡均值（一次额外 AllReduce，`÷world_size`），再 patch 回 FP8 reduce 后的 buffer；其余参数仍走 FP8。

| token | 含义 | 判定方式（结构判定、模型无关） |
| --- | --- | --- |
| `1d` | 所有 1-D 张量（norm scale、bias） | `param.dim() <= 1` |
| `embed` | `nn.Embedding` 模块的参数 | 所属模块类型 |
| `head` | 输出头参数 | leaf 名为 `lm_head` / `output` / `score` / `classifier` 的模块 |

判定按模块类型 / leaf 名，而非参数名 substring，因此只是路径里含 `head`/`embed` 的容器不会被整体误扫，token embedding 无论怎么命名都能命中。未知 token 在启动时直接报错。默认排除集通常只占可训练元素的一小部分，额外 AllReduce 可忽略。若排除一个大的可训练词表 embedding（如 `tune_llm=True`），排除集可能大到抵消吞吐收益——这时用 `1d`；逐桶排除占比会打在 INFO 日志里。

### 4.2 误差补偿（`--ddp-comm-hook-fp8-error-feedback`）

误差补偿（EF）用经典残差对付同一个累积偏置：`v = g + residual; q = quant(v); residual = v − dequant(q)`。把每个量化点的残差带入下一步，使残差序列 telescoping，把累积偏置约束在 `e_0 − e_T` 而不再漂移。残差以 FP32 存储——低精度残差会重新引入 EF 本要消除的漂移。

| 模式 | 补偿的量化点 | 每元素常驻残差 |
| --- | --- | --- |
| `none` | — | 0 |
| `allgather` | 仅 AllGather 前的 shard | 0.5 字节 |
| `both` | AllToAll 前的 bucket + AllGather 前的 shard | 4.5 字节 |

`allgather` 用 1/9 的显存覆盖两个误差贡献中较大的那个。残差是唯一跨步携带的状态；bucket layout 变化（DDP rebuild）时残差随之丢弃，因为残差按 buffer 内字节偏移绑定。

### 4.3 排除与误差补偿的组合

排除与误差补偿正交，可以同时启用；在精度敏感的场景下组合使用效果最好。两者同开时，被排除的参数保留其精确 FP32 跨卡均值，且不受误差补偿影响，因此两种机制彼此独立。

## 5. 排障

| 现象 | 处理 |
| --- | --- |
| 启动报设备/后端/Triton FP8 类型不支持 | 换用全精度 comm hook，或在支持的 CUDA/NCCL 环境上运行 |
| 吞吐没有提升 | 确认 bucket 大于 `--ddp-comm-hook-fp8-min-mib`、未因 scratch 预算降级，且梯度 all-reduce 确实是瓶颈 |
| 开误差补偿后 OOM | `both` 大致翻倍常驻 scratch；改用 `allgather`，或优先用不增显存的 exempt |
| loss 偏离 baseline | 确认 exempt 已开（默认），恢复默认 block 大小，并对同模型全精度 baseline 校验 |
| exempt 似乎无效 | 查 INFO 日志里的逐桶排除占比；确保参数名在任何重建参数的 dtype/device 转换之前完成注册 |
