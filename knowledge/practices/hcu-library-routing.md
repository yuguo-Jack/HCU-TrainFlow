---
id: practices/hcu-library-routing
title: HCU Primus Turbo、UCCL、UltraEP、MoonEP 与底层库优化入口
engine: cross-engine
stages: [adapt, optimize, fault-tolerance]
visibility: public
review_level: source-guided-methodology
runtime_validated: false
---

# 从训练瓶颈追到 HCU 底层库

这是跨任务搜索入口，具体分支和能力结论来自 HCU-Knowledge 保留报告，尚不代表当前环境已安装或通过训练。完整的选库、源码路径、构建与回归步骤统一维护在 [优化 Skill 的依赖联动指南](../../skills/hcu-train-optimize/references/hcu-library-integration.md)。该指南变更时复核本页，避免知识与执行流程各写一套互相矛盾的规则。

| 实际问题 | 查询入口 | 关键边界 |
| --- | --- | --- |
| 融合算子、Grouped GEMM、低精度、专家计算 | HCU Transformer Engine、Flash-Train、Primus Turbo；Primus/Primus-LM patch 的实际调用 | 先复用已有后端；核对 fwd/bwd、cast/累加精度、真实 dispatch、DTK/CK/AICC 与目标 gfx |
| 集合通信、P2P、CPU proxy 或链路利用率 | HCU RCCL、UCCL | UCCL collective、P2P、EP 是不同路径；不能按仓名整体替换 RCCL |
| MoE token dispatch/combine | HCU DeepEP、UCCL EP、MoonEP | 节点范围、dtype、路由顺序、空专家、异步完成、handle/buffer 生命周期和反向必须匹配 |
| 专家复制、负载重路由、权重与梯度归并 | HCU UltraEP 与实际 rocSHMEM provider | 不等同于单纯 dispatch 库；额外显存与训练状态一致性都要验证 |
| 通算融合、设备侧通信与推进 | HCU rocSHMEM、MORI、Flux 及上列库 | 需要实际 provider、可见性/同步、资源争用和消费者调用链证据 |
| GEMM、编译器或 runtime 本身限制 | HCU rocBLAS/hipBLASLt、CK、AICC/DCC、Galaxy | 同 shape 重现、当前实际分支与加载制品；必要时修改重编，隔离候选依赖 |

遇到 HCU 问题先用大知识库按报错/符号/shape/gfx/DTK/机制检索，再看实际部署源码。既有证据适用时直接复用；普通查阅不更新大库。没有访问权限、版本未知、接口缺失应形成明确缺口，不用 AMD/NVIDIA 同名工程替代 HCU 支持结论。

底层库改动与引擎改动使用独立开发 checkout 和可回退制品，避免修改知识库源码缓存或共享 DTK。记录编译版本、ABI、产物哈希与实际加载/dispatch；库单测、同形状实测、引擎集成、profiler-off 性能/显存和阶段 loss 分别验收。最后按目标库规范交付 PR。引擎主仓整合仍遵守 [执行基线与交付顺序](execution-baseline.md)。

训练引擎与容错工程的范围不因新增底层候选而扩大。选择由证据和收益决定，不能为了覆盖表中所有名字而增加安装、重编或实验。
