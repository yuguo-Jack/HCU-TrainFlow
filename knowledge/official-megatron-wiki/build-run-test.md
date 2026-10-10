---
id: official-megatron-wiki/build-run-test
title: Megatron 安装、启动、测试与 HCU 接入
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
  path: docs/get-started/install.md
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: b5e97dc226f7ff5c18c7f91d5dd0c5439dd2850bb5276b57eb528a664011317a
- source: nvidia-megatron-lm
  path: docs/get-started/quickstart.md
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 12facd93f82e65b9ca752faeff7496de268832713ea3746dabc00e3c148db9dc
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: a6a17536d6cd4c66f956651b519d5e96b84c088133543f99ae90798a49b8899f
---

# Megatron 安装、启动、测试与 HCU 接入

## 安装与运行原则

官方安装文档是 NVIDIA 环境的基准。HCU 环境使用匹配 DTK、PyTorch、编译器、通信库及 TE 的镜像或包，不照搬 CUDA 容器。记录 Python/import 路径、wheel 版本、动态库解析和构建参数，检查扩展是否误用了另一个环境的缓存。

本工作流的 HCU 适配顺序是：先读取选定 HCU 分支已有的同模型脚本及其环境/启动依赖，结合现场部署和用户 patch；没有同模型脚本时参考相近模型的 HCU 配方，再与官方模型配置核对训练语义。没有适用 HCU 配方时才据官方示例构建平台适配方案。HCU 旧脚本也须核对当前 DTK/依赖和参数支持，不能仅凭名称相同直接运行。

确认实际入口是 HCU 包装脚本、Bridge recipe 还是 `pretrain_gpt.py`，在已获授权的调度资源内用匹配解释器及该入口支持的帮助/配置输出方式核对参数。`--help` 也可能初始化导入依赖。沿启动链核对最终 argv、cwd、非敏感环境及其覆盖顺序，再写入 command card；保存与原 HCU 脚本的差异及原因。具体核对见 [适配工作流](../../skills/hcu-train-environment-check-and-adapt/references/workflow.md#启动配方选择与核对)。

## 测试阶梯

1. 导入/设备分配/单个 primitive；明确执行数和 skipped 项。
2. 单层 forward、backward、梯度和优化器更新与保守基线比较。
3. 缩层模型，保留 hidden/head/seq/专家数和数据语义，检查实际 candidate 分发。
4. 冻结阶段候选后做固定样本、相同聚合定义的 loss 验证。
5. 完整模型最小 DP 域、checkpoint 恢复及扩容验证。

不能把单元测试收集成功、空跑或 fallback 路径当成候选通过。每一层留下命令、stdout/stderr、源快照和报告。正式优化出口优先实际活跃 HCU 主仓分支，开发 checkout 与知识库源码缓存分离。

## 报错分流

导入失败查 wheel/依赖；编译失败查编译器和目标 ISA；分布式初始化卡住查所有 rank 的错误先后与网络；训练后才失败查真实 shape、precision、保存状态及异步错误。不要在没有症状分类前同时改多个环境变量。

## 固定源码与更新范围

- [docs/get-started/install.md](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/docs/get-started/install.md)
- [docs/get-started/quickstart.md](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/docs/get-started/quickstart.md)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/arguments.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
