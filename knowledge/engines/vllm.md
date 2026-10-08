---
id: engines/vllm
title: vLLM：RL rollout 的推理侧检查
engine: vllm
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: vllm-project-vllm
  path: README.md
  commit: 242e4213fc9845ff6fe607af1aee626fd8acc990
  sha256: 8d2e7cd8d120bcd91ddfa85ef957f7246021b4a3f46f2e1f4ccf084ec6c20026
---

# vLLM：RL rollout 的推理侧检查

## 在训练工作流里的位置

vLLM 承接 RL rollout，性能和正确性边界包括权重版本、tokenizer、采样、logprob、KV cache、调度和通信。训练引擎能跑不代表 rollout 返回了预期 policy 的样本。

## 仓库阅读路线

实现优先从 `vllm/ 和 csrc/` 查实际启动/调度/模型执行，官方 `docs/`、`examples/`、benchmark 和测试目录提供对应版本的入口。先核对当前 HCU fork 与官方配置/模型差异，再读取真实 attention、GEMM、通信和权重更新路径。不要以缓存 Wiki 的源码快照作为提交 PR 的开发 checkout。

## 实验

prefill/decode 分别记录 batch、seq、KV 格式、dtype、并发和调度策略。训练与推理共享设备时记录切换、权重同步、显存释放及预留余量；模型内 kernel 要与相同 shape 的独立测试比较。在线吞吐需要配合样本年龄、失败/重试和策略版本看。

## 回归

固定 seed 不保证跨后端逐 token 一致，应对齐 logits/logprob、mask、停止条件和容差，并评估实际 RL 算法需要的误差界。复用上游故障定位的“保存现场—最小重现—工具升级”方法，具体 HCU profiler 与调试工具按目标平台选择。

当前为训练侧的官方入口索引，尚未复刻整个推理引擎 Wiki；遇到 rollout 瓶颈按需查 HCU 大知识库和固定源码深化。

## 固定源码与更新范围

- [README.md](https://github.com/vllm-project/vllm/blob/242e4213fc9845ff6fe607af1aee626fd8acc990/README.md)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
