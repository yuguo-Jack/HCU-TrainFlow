---
id: doc-baidu-baige-loongforge-6e9959e827b074abba5b
title: baidu-baige/LoongForge / docs/source_zh/features/optimizer_support.md
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
path: docs/source_zh/features/optimizer_support.md
raw_sha256: cec990d28b0a6f616acc338cb347c4bed43c6312eebeec372ec3951b18a92e90
sources: []
generated_body_sha256: 3666fe9d58e8e3528e73399e62090cac5b9bdc34952a1d93472f7cb427a05d68
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source_zh/features/optimizer_support.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source_zh/features/optimizer_support.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 优化器支持
LoongForge 提供优化器卸载和低精度优化器，以降低低精度训练时的显存占用。

---

## 1. 启用低精度训练的优化器卸载
优化器卸载是缓解优化器状态导致 GPU 显存压力的最有效方法之一。通过将部分或全部优化器状态迁移到 CPU 内存，可以在不改变计算图的情况下训练更大的模型或使用更大的批量大小。

**BF16 示例**
```bash
--bf16 \
--use-precision-aware-optimizer \
--optimizer-cpu-offload \
--optimizer-offload-fraction 1.0
```

**FP8 示例**
```bash
--fp8-format e4m3 \
--fp8-recipe blockwise \
# --fp8-param-gather \
--use-precision-aware-optimizer \
--optimizer-cpu-offload \
--optimizer-offload-fraction 1.0
```

参数说明
* `--optimizer-cpu-offload` — 启用 CPU 卸载
* `--optimizer-offload-fraction` — 卸载的状态比例（1.0 = 全部，0.0 = 无）

以上两个参数均需要 `--use-precision-aware-optimizer`。
启用后，训练的比特精确性得以保持。

---

## 2. 低精度优化器状态
与其将优化器保持为 FP32，不如将 `exp_avg` 和 `exp_avg_sq` 存储为 BF16/FP16/FP8，在保持数值稳定性的同时降低显存和带宽占用。

```bash
--use-precision-aware-optimizer \
--exp-avg-dtype bf16 \
--exp-avg-sq-dtype bf16
```

参数说明
* `--exp-avg-dtype` — Adam 一阶矩的数据类型
* `--exp-avg-sq-dtype` — Adam 二阶矩的数据类型

同样，`--use-precision-aware-optimizer` 是必需的。
训练保持比特精确。

---

## 3. 优化器卸载性能调优
我们用 DeepSpeed 高度优化的 CPU-Adam 替换了 Megatron 原生的 Torch CPU-Adam（默认启用）。

禁用并回退到原生实现：
```bash
--no-use-deepspeed-cpu-adam
```

为获得最佳吞吐量，请导出：
```bash
export OMP_NUM_THREADS=8
```

---

## 4. 低精度优化器性能调优
我们提供了 TransformerEngine 低精度优化器的优化版本（仅 BF16）。
*原始 TE 步长时间 ≈ 1.34 s*
![origin_te](../../assets/images/ori_te_optimizer.png)
*优化后步长时间 ≈ 358 ms*
![after_opt](../../assets/images/now_optimizer.png)

使用低精度优化器时，快速路径会自动启用。
如需强制使用原始 TE 实现：

```bash
export USE_BF16_BUFFER=false
```
