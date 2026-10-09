---
id: ecosystem/mindspeed
title: 华为 MindSpeed / MindSpeed-LLM：机制级参考
engine: mindspeed
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: ascend-mindspeed
  path: README.md
  commit: 485d1077017a39963de83944230cfab26a6ec467
  sha256: 10c6731705c141a7f72921b1ec77fbb498adb617d4a2639c7831209b26bbea34
- source: ascend-mindspeed
  path: mindspeed/features_manager/moe/moe_alltoall_overlap.py
  commit: 485d1077017a39963de83944230cfab26a6ec467
  sha256: 98f147c94abd5db221b522a34a396d8a046f571e0d2075d3f6eb574aa322f6ec
- source: ascend-mindspeed
  path: docs/en/features/megatron_moe/megatron-moe-zero-memory.md
  commit: 485d1077017a39963de83944230cfab26a6ec467
  sha256: 1d4c360ee5c3a6df9dbf0ebff17eb2049a156f2b1faabc9a9958b7c2c84561b1
---

# 华为 MindSpeed / MindSpeed-LLM：机制级参考

## 工程关系

MindSpeed 提供特性和适配机制，MindSpeed-LLM 提供模型训练应用、脚本和更高层配置。阅读时同时记录各自 SHA 与所依赖 Megatron 基线。Ascend 特有运行时、通信与算子不能当 HCU 命令执行。

## 有价值的线索

MoE 通信计算重叠、重算/显存管理、长序列 CP、模型接入及配方是优先入口。先从 features manager 的参数验证与补丁注册，进入实际替换模块，再去看算子/通信实现；比仅摘 README flag 更容易发现依赖和互斥条件。

## 迁移分层

算法与调度思想可以重建；NPU kernel、HCCL/CANN 接口和环境参数需要映射到 HCU 对应能力并重新验证。把性能目标拆成可证伪假设，例如“减少 dispatch 暴露等待”，再检查真实 rank timeline，而非照搬某个宣传加速比。

## 退出和采用决策

每项参考标记 proposed/rejected/implemented/validated/upstream-equivalent。官方同类 PR 合并后，继续比较实际采用分支和数值/恢复行为；有同名功能不足以直接删 HCU 补丁。

## 固定源码与更新范围

- [README.md](https://github.com/Ascend/MindSpeed/blob/485d1077017a39963de83944230cfab26a6ec467/README.md)
- [mindspeed/features_manager/moe/moe_alltoall_overlap.py](https://github.com/Ascend/MindSpeed/blob/485d1077017a39963de83944230cfab26a6ec467/mindspeed/features_manager/moe/moe_alltoall_overlap.py)
- [docs/en/features/megatron_moe/megatron-moe-zero-memory.md](https://github.com/Ascend/MindSpeed/blob/485d1077017a39963de83944230cfab26a6ec467/docs/en/features/megatron_moe/megatron-moe-zero-memory.md)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
