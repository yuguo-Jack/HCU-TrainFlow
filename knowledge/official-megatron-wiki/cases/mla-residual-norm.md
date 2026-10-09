---
id: official-megatron-wiki/cases/mla-residual-norm
title: 案例：MLA 融合分支遗漏 residual 声明，导致反向少一层融合
engine: megatron
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-megatron-lm
  path: megatron/core/models/gpt/gpt_layer_specs.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 9e153c7f3d3a671f1bd9b84023bfe0f14711fe942c4c0df3dc1dec288100c4af
- source: nvidia-megatron-lm
  path: tests/unit_tests/transformer/test_multi_latent_attention.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 744af8ccef91748b2d0117ba43219c5084d0a93dd1e13d0bee8a839a3a858d58
pr_sources:
- pr-nvidia--megatron-lm-7942
---

# 案例：MLA 融合分支遗漏 residual 声明，导致反向少一层融合

## 问题与触发条件

[官方 PR #7942](https://github.com/NVIDIA/Megatron-LM/pull/7942) 修复 MLA down-projection fusion 的 MoE 分支：构造 pre-MLP norm 时没有声明 residual，而相邻实现已声明。当 fused_residual_rmsnorm 开启时，这会影响 TE 是否采用包含残差梯度相加的融合 backward。

这类问题说明“配置开了融合”不等于实际进入融合 kernel。适配时不仅比较算子名字，还要沿 layer spec→backend 工厂→module 属性→autograd/TE dispatch 追踪。

## 改动位置和原因

`get_gpt_layer_with_transformer_engine_submodules` 的对应分支传入 `has_residual=True`，保持不同 MLA 构造路径对接口契约的一致表达。目标是让后台识别可融合的残差梯度工作，不是删除残差或少算梯度。

## Review 与测试证据

本轮真实采集了 PR 正文、普通评论、行内评论、5 条独立 review 及全部两个改动文件。顶层 review 明确提出应增加融合开/关的对照测试；最终变更同时补了 spec 属性检查和实际层的数值对照。

测试先加载同一 state dict，检查真实 `returns_residual` 属性，再比较输出、输入梯度和参数梯度。对未受该加法舍入影响的路径要求严格一致，对经过 BF16 残差加法的路径允许有依据的舍入误差。不能把这个测试中的阈值直接变成所有 HCU 算子的统一容差。该测试还有依赖版本/运行环境要求，skip 不代表已验证。

## HCU 应用步骤

1. 确认当前 HCU Megatron 分支是否已有这一修复，并确认 HCU TE 是否真正实现对应 fused backward。
2. 捕获实际模型的 MLA/MoE 配置、norm 实例属性和 backward trace，检查融合粒度差距。
3. 优先复用 HCU TE/Flash-Train 已有能力；缺少时按其接口和数值契约补齐。
4. 做同参数的融合开/关局部测试与 kernel dispatch 证据，再跑 profiler-off 步时间；稳定阶段补 loss 验收。
5. 失败则回退该融合候选，保留非融合正确路径。上游修复存在不代表某个 HCU release 已包含。

## 证据边界

PR head 为 `0e98321a9ddacc11141177202769712415d9f4bd`，merge 为 `91655aa78007e74e55c963f99861b8a97368c024`。本页源码链接固定到本轮官方主干快照；没有执行 NVIDIA/HCU GPU 测试，也没有编造吞吐提升比例。

## 固定源码与更新范围

- [megatron/core/models/gpt/gpt_layer_specs.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/models/gpt/gpt_layer_specs.py)
- [tests/unit_tests/transformer/test_multi_latent_attention.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/tests/unit_tests/transformer/test_multi_latent_attention.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。

[PR 原文、review 与 diff](../../prs/NVIDIA--Megatron-LM/PR-7942.md)
