---
id: official-megatron-wiki/parallelism
title: 并行域、微批与 rank 采样
engine: megatron
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-megatron-lm
  path: megatron/core/parallel_state.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 414ecaf3b1891e8d621e5ec86a80af9d2d313d4393ac11e83832ff4bf7257dd2
- source: nvidia-megatron-lm
  path: docs/user-guide/parallelism-guide.md
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 8fe555b69e65abd543acc633c23f1b33491d6b0266a7b6c9848dd997222e674d
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 3719d850b8822e221f30472881b8802b8f88ce02167856130fae97849d1d91ee
---

# 并行域、微批与 rank 采样

## 需要显式建模的拓扑

TP、PP、DP、CP、EP 和 expert tensor parallel 不应只登记几个整数。保存每个实际 process group 的成员、节点和设备映射；EP 可能与其他维度共享或重组 rank。不能直接按 world size 除某几个参数猜测所有组。

`profile-plan` 接收实际 groups 和可抓取 ranks，每个非单例组至少选两个成员。PP 关注首尾及不平衡 stage，EP 关注负载明显不同成员。两 rank 是最低观测要求，collective 全组分析或跨节点偏斜可能需要全组。

## 调参推理

全局 batch、microbatch 和梯度累积必须满足当前 schedule 与 DP 的关系；packing、动态 batch 或变长场景应记录真实 token 数。缩层代理保留模型其他维度，不能为了跑通同时缩 seq 或专家数再拿其耗时外推。

PP 空泡由调度、微批和 stage 工作量共同决定；EP token 不均可能使最慢 rank 限制整个步。分别记录各 rank phase 的计算、通信和等待，先解释时间线，再决定改并行度还是算子实现。

## 验证

改变拓扑后重新构造 context；旧 trace/环境检查/质量报告仍保留，但不能为新配置放行。DP/TP/EP collective 单测的数据量与 dtype 应来自真实模型，机内与机间测试不能互相替代。

## 固定源码与更新范围

- [megatron/core/parallel_state.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/parallel_state.py)
- [docs/user-guide/parallelism-guide.md](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/docs/user-guide/parallelism-guide.md)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/pipeline_parallel/schedules.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
