---
id: project-loongforge
title: loongforge 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: 6d610bf16d5a9ff8629fcd146313a8b1946eda068e36395d69f469394e7bb8cd
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
- [选定官方文档原文](knowledgebase/upstream/docs/)
- [已选定 PR 与固定证据](knowledgebase/upstream/prs/)
- [固定源码阅读入口](knowledgebase/upstream/source-map/)

普通 PR 通过官方原页联搜，正文、代码和讨论按需读取；已选定页面链接固定原件，历史材料由既有固定 Git 基线按需恢复。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
