---
id: ecosystem/primus
title: AMD Primus：后端组织、版本锁与迁移路线
engine: primus
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: amd-agi-primus
  path: README.md
  commit: 0f996490ad1bf53f0756dc631e195c94738a6341
  sha256: 9e1fdbb705ff22352d96f6c4e110744f338b6e0e824f34938932fc466cafde36
- source: amd-agi-primus
  path: .gitmodules
  commit: 0f996490ad1bf53f0756dc631e195c94738a6341
  sha256: 3a6fe9a0aabd4d2d6d3b323171eec4c451c21001395a98d3b725279b91a61fc5
- source: amd-agi-primus
  path: primus/backends/megatron/patches/__init__.py
  commit: 0f996490ad1bf53f0756dc631e195c94738a6341
  sha256: b558482f6abc630155ed78773d7e0ba4cfe1ccd5610845101d31675ddfee344b
- source: amd-agi-primus
  path: docs/04-technical-guides/fault-tolerance-and-elastic-training.md
  commit: 0f996490ad1bf53f0756dc631e195c94738a6341
  sha256: 95a139372f53910555884c391081d1a6da9cae86901aadd20ca4ce32b174be00
---

# AMD Primus：后端组织、版本锁与迁移路线

## 为什么是重点参考

Primus 将后端、模型配方、补丁和运行运维组织在一个工程里，可用于寻找 ROCm 场景下的编译、并行和内存优化。它仍需与 HCU 的 runtime、编译器及库实现对照，不能因同属 HIP 生态就直接认定兼容。

## 目录和依赖

`primus/backends/megatron` 组织模型和补丁，`primus/configs` 为配置入口，`tests` 提供针对机制的回归。`third_party` 下的 Megatron-LM、Bridge 等使用固定 gitlink；本轮父仓锁定的 LM 为 `d3528a21301db2d12e92912b3ec025dc8a2ed4d6`，不是官方 main 的同一提交。

## 采用流程

先确定补丁触发条件、调用阶段、上游符号与回退路径，再在真实 HCU 基线查是否已经有等价实现。适合优先研究：compile 与 DDP hook 的边界、逐层重算、TP overlap、offload 与容错配置。每项保留依赖锁及测试的有效执行证据。

## 容错参考边界

其文档分别讨论 scheduler checkpoint 重启、进程内重启及其他后端弹性训练，不能混成“Primus 自动处理所有故障”。HCU 部署优先任务指定的 Cluster Manager；Primus 相关工具作为实际环境允许的补充，单一恢复负责人保持不变。

## 固定源码与更新范围

- [README.md](https://github.com/AMD-AGI/Primus/blob/0f996490ad1bf53f0756dc631e195c94738a6341/README.md)
- [.gitmodules](https://github.com/AMD-AGI/Primus/blob/0f996490ad1bf53f0756dc631e195c94738a6341/.gitmodules)
- [primus/backends/megatron/patches/__init__.py](https://github.com/AMD-AGI/Primus/blob/0f996490ad1bf53f0756dc631e195c94738a6341/primus/backends/megatron/patches/__init__.py)
- [docs/04-technical-guides/fault-tolerance-and-elastic-training.md](https://github.com/AMD-AGI/Primus/blob/0f996490ad1bf53f0756dc631e195c94738a6341/docs/04-technical-guides/fault-tolerance-and-elastic-training.md)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
