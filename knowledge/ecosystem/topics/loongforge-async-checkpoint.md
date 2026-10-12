---
id: ecosystem/topics/loongforge-async-checkpoint
title: LoongForge Torch-native：异步保存完成投票与 DCP 恢复
engine: loongforge
kind: authored
stages:
- fault-tolerance
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: baidu-baige-loongforge
  path: loongforge/embodied/distributed/checkpoint.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 15dee38364ca4e3da741ad9f2b9a793220557a4a4224fdb556f8b6fd7fb2a124
- source: baidu-baige-loongforge
  path: loongforge/embodied/train/trainers/base_trainer.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 24c31c517d4d2a712ba1e0ed31327ebe32b5f2a896be85e9207fb0853027e86b
- source: baidu-baige-loongforge
  path: tests/embodied/unit/test_async_checkpoint_finalize.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: d63a03a60df4ad26c83023409869a7c9e8f8eed47df9cadb30a8bb2b2965c5ce
- source: baidu-baige-loongforge
  path: loongforge/embodied/README.md
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: cea16e85bafe721b0a31015891d18b948974706c2acc263c871c0e98cac5217b
---

# LoongForge Torch-native：异步保存完成投票与 DCP 恢复

## 问题：文件写完仍被当作不可恢复

Embodied Torch栈用`resume_meta.json`标记可恢复checkpoint。若只在下一次save或exit才finalize async save，即使数据已经持久写完，故障发生在两次save之间时仍会丢掉这份完成的checkpoint。另一个问题是DCP对共享参数alias的FQN映射，DDP wrapper下恢复可能报告成批missing/unexpected。

## 源码与 PR 的修复链

[#261](../../prs/baidu-baige--LoongForge/PR-261.md)的当前实现由BaseTrainer每optimizer step调用`maybe_finalize_pending_save`。无pending直接返回；有pending时**所有rank**对完成状态`all_reduce(MIN)`，只有共同完成才进入`flush_pending_save`。rank-local `Future.done()`不能决定只有部分rank进入后者，否则内部collective会死锁。

`_async_save_completion`识别`AsyncSaveResponse.upload_completion`，等待持久写入的completion而非只等staging。`flush_pending_save`在`future.result()`成功后由主rank写marker，失败则共同处理并保留原错误；不能先写marker再在后台补数据。DCP resume将权重加载到unwrapped module，避免同一参数多属性alias在DDP FQN还原时丢键。

## 运行契约与开销

只有实际使用async DCP等相关路径才有该机制，不等同Megatron schedule或所有格式的行为。pending时每step增加一次小完成投票；这换取更早确认已完成checkpoint，不改save interval或承诺GPU零开销。最终可恢复身份包括模型、optimizer、scheduler、RNG及stateful data sampler，marker存在不证明这些内容与当前模型兼容。

## 验证和已知边界

单测覆盖无pending、完成后commit、幂等、慢写、失败清理及等待upload；真实集群还需要kill在“数据完成/下一次save前”的窗口，证明这份checkpoint确实可resume。恢复检查参数alias、step与数据进度，watch旧rank/残留写进程。

PR描述另明确没有解决某些async-save与detail-log的Gloo abort；其临时参数 workaround只属于对应版本/实验，不升级为HCU全局默认。测试和A800实测为上游证据，本轮没有HCU运行或推广同等性能。

## 回退、诊断和更新

异常先查pending所有rank一致性、Future异常、storage持久化与marker次序；不要反复启动新的writer覆盖旧输出。可退到可信同步保存，代价是save暴露时间；保持上次可恢复checkpoint。更新DCP/PyTorch、wrapper/FQN或BaseTrainer循环同时复核本页与[总览](../loongforge.md)，容错系统继续是唯一重启owner。

## 固定证据与复核范围

- [loongforge/embodied/distributed/checkpoint.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/embodied/distributed/checkpoint.py)
- [loongforge/embodied/train/trainers/base_trainer.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/embodied/train/trainers/base_trainer.py)
- [tests/embodied/unit/test_async_checkpoint_finalize.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/tests/embodied/unit/test_async_checkpoint_finalize.py)
- [loongforge/embodied/README.md](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/embodied/README.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
