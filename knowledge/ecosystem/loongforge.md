---
id: ecosystem/loongforge
title: 百度 LoongForge：调度、offload 和模型适配参考
engine: loongforge
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: baidu-baige-loongforge
  path: README.md
  commit: 359b894a157261716d95c241b854460470afc9b5
  sha256: a1b33f28e4fa6dc0ea7a5fc002f03821f7ac750a1438ce0f7765fc69b5a75c6a
- source: baidu-baige-loongforge
  path: .gitmodules
  commit: 359b894a157261716d95c241b854460470afc9b5
  sha256: b5aca9eaf884dfde53b152fc6000eff8a8c793339b659411f6e79292bf68b2ed
- source: baidu-baige-loongforge
  path: docs/source/features/moe_all2all_overlap.md
  commit: 359b894a157261716d95c241b854460470afc9b5
  sha256: bd5b07da7b731f7cc3b3d0259ea4c9153da39fa0da7622e3a6cc493aaa46a615
- source: baidu-baige-loongforge
  path: loongforge/data/dp_balance/train_hooks.py
  commit: 359b894a157261716d95c241b854460470afc9b5
  sha256: 98ae698ebf87dd8c3412983397b6a74ed9718c71eb038fed50f43c5dcab4ab75
---

# 百度 LoongForge：调度、offload 和模型适配参考

## 依赖与目录

LoongForge 父仓包含训练封装、数据处理和文档；核心 Megatron 修改在 `third_party/Loong-Megatron` gitlink。本轮锁为 `64c279afb879229cff12fb293624e3691990403f`。分析或移植必须以此子提交为起点，不能用子仓当前 HEAD 替代父仓实际依赖。

`loongforge/data/dp_balance` 的 hooks、重排与样本平衡值得用于定位多模态/变长数据导致的 DP 不均；分析要同时关注重排后 loss 权重、样本顺序及恢复语义。

## 优化案例入口

EP all-to-all 的跨微批 overlap 与延迟 wgrad，将调度和显存生命期联系起来。配套 offload/重算不是独立开关，应与交错 1F1B 及活动微批数一起评估。官方文档给出的 CUDA 环境变量仅适用于其 NVIDIA 实现，不是 HCU 的推荐数值。

## HCU 参考方式

先对比当前官方与 HCU 主仓是否已有实现，再从子仓找真正修改符号，阅读 PR 讨论和测试。优先复用算法、调度与组织形式；性能证据需要在实际硬件和软件栈重建。引入机制前列出 correctness、recompute、graph、checkpoint、memory 等组合验证。

## 固定源码与更新范围

- [README.md](https://github.com/baidu-baige/LoongForge/blob/359b894a157261716d95c241b854460470afc9b5/README.md)
- [.gitmodules](https://github.com/baidu-baige/LoongForge/blob/359b894a157261716d95c241b854460470afc9b5/.gitmodules)
- [docs/source/features/moe_all2all_overlap.md](https://github.com/baidu-baige/LoongForge/blob/359b894a157261716d95c241b854460470afc9b5/docs/source/features/moe_all2all_overlap.md)
- [loongforge/data/dp_balance/train_hooks.py](https://github.com/baidu-baige/LoongForge/blob/359b894a157261716d95c241b854460470afc9b5/loongforge/data/dp_balance/train_hooks.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
