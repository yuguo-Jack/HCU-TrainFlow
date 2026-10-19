---
id: project-loongforge
title: loongforge 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: c6146e56fb42797748316d929ba624bef402c8ef19923c118a04d563df24d2eb
---

# loongforge

从[工程总览：LoongForge：两类训练入口、DP 均衡、EP 重叠与状态恢复](knowledgebase/local/overview/engineering-guide.md)进入。

## 整理后的知识

### 定位与代码地图

- [LoongForge：两类训练入口、DP 均衡、EP 重叠与状态恢复](knowledgebase/local/overview/engineering-guide.md)

### 机制专题

- [LoongForge Torch-native：异步保存完成投票与 DCP 恢复](knowledgebase/local/topics/loongforge-async-checkpoint.md)
- [LoongForge：变量长 ChunkPipe 的位置、缓存与梯度归一化](knowledgebase/local/topics/loongforge-chunkpipe-variable-length.md)
- [LoongForge：变长/视觉 DP 代价模型与跨 rank 样本均衡](knowledgebase/local/topics/loongforge-dp-balance.md)
- [LoongForge：跨微批 EP 重叠、延迟 wgrad 与细粒度卸载](knowledgebase/local/topics/loongforge-ep-offload.md)

### 优化案例

- [案例：跨微批 EP overlap 与细粒度激活策略](knowledgebase/local/cases/loongforge-ep-offload.md)

## 上游资料

- [baidu-baige-loongforge](https://github.com/baidu-baige/LoongForge)
- [baidu-loong-megatron](https://github.com/baidu-baige/Loong-Megatron)
- [官方文档原文](knowledgebase/upstream/docs/)
- [PR 描述、review 与固定代码](knowledgebase/upstream/prs/)
- [完整源码路径](knowledgebase/upstream/source-map/)

原始 PR JSON 集中保存在 [evidence/prs](../../evidence/prs/)；每篇 PR 原文页链接其固定原件。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
