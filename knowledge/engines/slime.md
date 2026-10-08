---
id: engines/slime
title: slime：Megatron 训练与 SGLang rollout 的联动
engine: slime
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: thudm-slime
  path: README.md
  commit: 2f2318653f6f794dddd321eff7c9d4b7b174643f
  sha256: 47cf69f284c175823244262a3ea712f53fc42e3a968fdcfbc4f76536e59c7ea3
---

# slime：Megatron 训练与 SGLang rollout 的联动

## 仓库给出的阅读路线

从 `train.py` 进入，`slime/ray/placement_group.py` 负责资源，`slime/ray/rollout.py` 组织生成，`slime/rollout/sglang_rollout.py` 承接采样/奖励，`slime/ray/actor_group.py` 派发训练，`slime/backends/megatron_utils` 连接模型与 RL loss。参数入口在 `slime/utils/arguments.py`；权重同步另有实现目录。

## 验证契约

冻结 tokenizer、生成参数、奖励函数、sample ID、policy version、训练权重与 logprob 来源。Data Buffer 不只是缓存，可能携带多轮轨迹及恢复状态。当前 README 还区分默认 Ray object store 与可选其他传输路径，不能用一种队列模型解释所有部署。

## 优化优先级

先比较生成、训练、权重同步、等待各自耗时；针对长尾 rollout 看批次分配与异步程度。对比 co-located 与分离布局时同时检查显存复用、模型切换、内存释放完成事件和 KV 余量。训练侧沿 Megatron，推理侧沿 SGLang 对应分支继续查源码。

## 范围

本页为上游明确给出的目录/阶段阅读索引，未声称完成每条 transport、算法或模型验证。新任务需要把实际选择的 actor/loss/update_weight 路径补成固定源码专题，并把异常重现脚本保存在私有任务目录。

## 固定源码与更新范围

- [README.md](https://github.com/THUDM/slime/blob/2f2318653f6f794dddd321eff7c9d4b7b174643f/README.md)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
