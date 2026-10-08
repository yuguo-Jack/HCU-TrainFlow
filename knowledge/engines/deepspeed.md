---
id: engines/deepspeed
title: DeepSpeed：ZeRO、扩展构建与训练阶段定位
engine: deepspeed
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: deepspeedai-deepspeed
  path: README.md
  commit: c6af3faf29101ccd7efba77df4b0768058ff1f4a
  sha256: e2f2dad685784770f1cd1fe72ba3be22788864ddf9234a899b75fb7dbdd15151
- source: deepspeedai-deepspeed
  path: setup.py
  commit: c6af3faf29101ccd7efba77df4b0768058ff1f4a
  sha256: d694bc8b1cd23e50c79763dab76cc08461cd963aa6e4e5b6b31d9f18f359ed53
---

# DeepSpeed：ZeRO、扩展构建与训练阶段定位

## 目录

`deepspeed/` 为 Python 引擎，`op_builder/` 与 `csrc/` 管构建及底层算子，`accelerator/` 区分设备后端，`tests/` 和 `benchmarks/` 是测试入口。首先记录当前 HCU 分支修改了哪些层，再沿运行时实际 accelerator 和 extension import 定位。

## 建立基线

保留 ZeRO stage、offload 配置、micro/global batch、precision、optimizer 和数据语义。检查扩展是 JIT 还是预编译、编译器与运行时 ABI、实际加载的共享库。安装完成不等于优化器或通信候选实际启用。

## 性能路线

ZeRO 的参数获取、梯度归约与 optimizer 状态分片产生不同通信/显存权衡。用真实 tensor 和 bucket 大小做 collective 单测，比较模型内等待与孤立性能。主存 offload 与数据 loader、checkpoint 争用时，应同时看 PCIe、NUMA、CPU 和 pinned memory。

## 验证范围

逐项检查输出、梯度、optimizer step、溢出跳步、分片保存和恢复；并行规模变化后重新验证。此页目前覆盖仓结构和工程级检查路线，具体 ZeRO 版本实现与优化案例需任务触发后继续细化源码，不能推导出 HCU 的全特性兼容表。

## 固定源码与更新范围

- [README.md](https://github.com/deepspeedai/DeepSpeed/blob/c6af3faf29101ccd7efba77df4b0768058ff1f4a/README.md)
- [setup.py](https://github.com/deepspeedai/DeepSpeed/blob/c6af3faf29101ccd7efba77df4b0768058ff1f4a/setup.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
