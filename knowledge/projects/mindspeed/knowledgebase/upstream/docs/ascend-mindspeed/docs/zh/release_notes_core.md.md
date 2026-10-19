---
id: doc-ascend-mindspeed-51db0885c6025f7cc677
title: Ascend/MindSpeed / docs/zh/release_notes_core.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 3c7f3251c4163f5020407dc6fb1706964817ac9b
path: docs/zh/release_notes_core.md
raw_sha256: 696f066046db4913016d423377a159e49fc4c05c555836a130eddcb00daf3937
sources: []
generated_body_sha256: 8e08ab7aa1d445574d9e63d90045f6b92161391addf95ac988006891459d2fd9
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/release_notes_core.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/3c7f3251c4163f5020407dc6fb1706964817ac9b/docs/zh/release_notes_core.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 版本说明

## 版本配套说明

### 产品版本信息

<table>
  <tbody>
    <tr>
      <th class="firstcol" valign="top" width="26.25%"><p>产品名称</p></th>
      <td class="cellrowborder" valign="top" width="73.75%"><p>MindSpeed</p></td>
    </tr>
    <tr>
      <th class="firstcol" valign="top" width="26.25%"><p>产品版本</p></th>
      <td class="cellrowborder" valign="top" width="73.75%"><p>26.2.0</p></td>
    </tr>
    <tr>
      <th class="firstcol" valign="top" width="26.25%"><p>版本类型</p></th>
      <td class="cellrowborder" valign="top" width="73.75%"><p>release版本</p></td>
    </tr>
    <tr>
      <th class="firstcol" valign="top" width="26.25%"><p>组件名称</p></th>
      <td class="cellrowborder" valign="top" width="73.75%"><p>MindSpeed Core</p></td>
    </tr>
    <tr>
      <th class="firstcol" valign="top" width="26.25%"><p>发布时间</p></th>
      <td class="cellrowborder" valign="top" width="73.75%"><p>2026年7月</p></td>
    </tr>
    <tr>
      <th class="firstcol" valign="top" width="26.25%"><p>维护周期</p></th>
      <td class="cellrowborder" valign="top" width="73.75%"><p>6个月</p></td>
    </tr>
  </tbody>
</table>

> [!NOTE]
>
> 有关MindSpeed的版本维护，具体请参见[分支维护策略](https://gitcode.com/Ascend/MindSpeed/tree/26.1.0_core_r0.12.1#%E5%88%86%E6%94%AF%E7%BB%B4%E6%8A%A4%E7%AD%96%E7%95%A5)。

### 相关产品版本配套说明

**表 1**  MindSpeed Core软件版本配套表

|MindSpeed Core代码分支名称|CANN版本|TorchNPU版本|Python版本|PyTorch版本|
|--|--|--|--|--|
|master（在研版本）|在研版本|在研版本|Python3.12|2.10.0|
|26.2.0_core_r0.12.1|9.2.0|26.2.0|Python3.10|2.10.0|
|26.1.0_core_r0.12.1|9.1.0|26.1.0|Python3.10|2.7.1|
|26.0.0_core_r0.12.1|9.0.0|26.0.0|Python3.10|2.7.1|

>[!NOTE]
>
>用户可根据需要选择MindSpeed代码分支下载源码并进行安装。

## 版本兼容性说明

> [!NOTE]
>
> 本节表格中“/”表示不可配套，“Y”表示可配套。

**表 2**  MindSpeed Core与TorchNPU版本兼容

<table style="table-layout: fixed; width: 750px ; text-align:center">
  <colgroup>
    <col style="width: 150px">
    <col style="width: 150px">
    <col style="width: 150px">
    <col style="width: 150px">
    <col style="width: 150px">
    <col style="width: 150px">
  </colgroup>
  <thead>
    <tr>
      <th rowspan="2">MindSpeed Core</th>
      <th colspan="5">TorchNPU版本</th>
    </tr>
    <tr>
      <th>7.2.0</th>
      <th>7.3.0</th>
      <th>26.0.0</th>
      <th>26.1.0</th>
      <th>26.2.0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>26.0.0_core_r0.12.1</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
    </tr>
    <tr>
      <td>26.1.0_core_r0.12.1</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
    </tr>
      <tr>
      <td>26.2.0_core_r0.12.1</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
    </tr>
  </tbody>
</table>

**表 3**  MindSpeed Core与CANN版本兼容

<table style="table-layout: fixed; width: 750px ; text-align:center">
  <colgroup>
    <col style="width: 150px">
    <col style="width: 150px">
    <col style="width: 150px">
    <col style="width: 150px">
    <col style="width: 150px">
  </colgroup>
  <thead>
    <tr>
      <th rowspan="2">MindSpeed Core</th>
      <th colspan="4">CANN版本</th>
    </tr>
    <tr>
      <th>8.3.RCX</th>
      <th>8.5.X</th>
      <th>9.0.X</th>
      <th>9.1.X</th>
      <th>9.2.X</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>26.0.0_core_r0.12.1</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>/</td>
    </tr>
    <tr>
      <td>26.1.0_core_r0.12.1</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
    </tr>
      <tr>
      <td>26.2.0_core_r0.12.1</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
      <td>Y</td>
    </tr>
  </tbody>
</table>

## 版本使用注意事项

无

## 更新说明

### 新增特性

无

### 删除特性

无

### 接口变更说明

无

### 已解决问题

无

### 遗留问题

无

## 升级影响

### 升级过程中对现行系统的影响

- 对业务的影响

    软件版本升级过程中会导致业务中断。

- 对网络通信的影响

    对通信无影响。

### 升级后对现行系统的影响

无

## 配套文档

|文档名称|内容简介|更新说明|
|--|--|--|
|《[MindSpeed快速入门](../zh/user-guide/quickstart.md)》|介绍基于MindSpeed实现Megatron-LM在昇腾设备上的高效运行。|-|
|《[MindSpeed软件安装](../zh/user-guide/install_guide.md)》|指导用户在NPU上基于PyTorch框架完成MindSpeed的安装，内容涵盖硬件与操作系统兼容性说明、驱动固件及CANN基础软件安装的完整安装流程，帮助用户快速搭建大模型分布式训练环境。|-|

## 病毒扫描及漏洞修补列表

### 病毒扫描结果

|防病毒软件名称|防病毒软件版本|病毒库版本|扫描时间|扫描结果|
|---|---|---|---|---|
|QiAnXin|8.0.5.5260|2026-09-27 08:00:00.0|2026-09-28|无病毒，无恶意|
|Kaspersky|12.0.0.6672|2026-09-28 10:09:00|2026-09-28|无病毒，无恶意|
|Bitdefender|7.5.1.200224|7.101487|2026-09-28|无病毒，无恶意|

### 漏洞修补列表

无

## 修订记录

|文档版本|发布日期|修改说明|
|--|--|--|
|01|2026-10-15|第一次正式发布|
