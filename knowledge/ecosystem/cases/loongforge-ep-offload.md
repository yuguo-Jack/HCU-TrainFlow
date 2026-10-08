---
id: ecosystem/cases/loongforge-ep-offload
title: 案例：跨微批 EP overlap 与细粒度激活策略
engine: loongforge
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: baidu-baige-loongforge
  path: docs/source/features/moe_all2all_overlap.md
  commit: 359b894a157261716d95c241b854460470afc9b5
  sha256: bd5b07da7b731f7cc3b3d0259ea4c9153da39fa0da7622e3a6cc493aaa46a615
- source: baidu-baige-loongforge
  path: .gitmodules
  commit: 359b894a157261716d95c241b854460470afc9b5
  sha256: b5aca9eaf884dfde53b152fc6000eff8a8c793339b659411f6e79292bf68b2ed
---

# 案例：跨微批 EP overlap 与细粒度激活策略

## 机制与适用条件

文档描述把相邻微批的前向、反向与 EP all-to-all 交错，并将部分 wgrad 推迟，依赖交错 1F1B。因为同时存活的激活和调度发生改变，需要重新设计重算/offload 粒度。

这里是文档级机制索引：本页没有宣称已完成子仓实现逐行验证，也不把文档 flag 视为任何 Megatron 分支通用接口。真正移植前必须拉取固定 gitlink，定位 schedule、dispatcher 和 offload 实现，再登记调用链及测试。

## 应测量什么

比较暴露的 EP 等待、forward/backward/wgrad 分配、活动微批数、D2H/H2D 带宽、NUMA 和主存占用。保持实际模型 shape 和专家分布，检查 TP overlap 与 EP overlap 是否争用资源。不要将 kernel 自身慢一点直接等同于 e2e 退化，也不要忽略 e2e 加速同时留下的显存风险。

## 正确性与回退

检查梯度累计顺序、offload buffer 生命周期、RNG、低精度 scale/缓存和 checkpoint 恢复。回退以完整机制包为单位，不保留一半调度加一半旧缓存逻辑。阶段 loss 失败时恢复初始可信基线，按最小差异缩小问题。

## 固定源码与更新范围

- [docs/source/features/moe_all2all_overlap.md](https://github.com/baidu-baige/LoongForge/blob/359b894a157261716d95c241b854460470afc9b5/docs/source/features/moe_all2all_overlap.md)
- [.gitmodules](https://github.com/baidu-baige/LoongForge/blob/359b894a157261716d95c241b854460470afc9b5/.gitmodules)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
