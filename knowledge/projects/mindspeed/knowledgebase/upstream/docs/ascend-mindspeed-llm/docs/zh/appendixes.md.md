---
id: doc-ascend-mindspeed-llm-c20a51caaf84088eb7cf
title: Ascend/MindSpeed-LLM / docs/zh/appendixes.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/zh/appendixes.md
raw_sha256: 032b49f616b1715b6e021ed62d5be3e641a80f43fdf405f4919e55bb73ec8757
sources: []
generated_body_sha256: 91ba24b3e112240cbc967f9a29a8d47a9d497bd161d09a7823d6b966e375501f
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/appendixes.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/appendixes.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 附录

## 常见问题

常见问题见[FAQ](./FAQ.md)

## 加入昇腾开发者生态

- 🌐 **社区资源**：访问[昇腾开源社区](https://gitcode.com/ascend)获取最新模型支持
- 📈 **性能优化**：参考[MindSpeed Profiling](./pytorch/tools/profiling.md)分析瓶颈
- 💡 **定制需求**：通过`model_cfg.json`扩展自定义模型

## 线性度

基于`GPT3-175B`稠密大模型，从128颗NPU扩展到7968颗NPU进行MFU与线性度实验，下图是实验数据：

<p align="center"> <img src="./pytorch/figures/readme/linearity&mfu.png" height="490px" width="715px"> </p>

图中呈现了对应集群规模下的`MFU`值与集群整体的`线性度`情况。计算公式可单击如下链接进行参考：

- [MFU计算公式](https://gitcode.com/Ascend/MindSpeed-LLM/wiki/%E6%9C%AF%E8%AF%AD%E5%AE%9A%E4%B9%89%2F%E5%A4%A7%E6%A8%A1%E5%9E%8B%20MFU%20%E8%AE%A1%E7%AE%97%E5%85%AC%E5%BC%8F.md)
- [线性度计算公式](https://gitcode.com/Ascend/MindSpeed-LLM/wiki/%E6%9C%AF%E8%AF%AD%E5%AE%9A%E4%B9%89%2F%E7%BA%BF%E6%80%A7%E5%BA%A6%E5%85%AC%E5%BC%8F.md)
