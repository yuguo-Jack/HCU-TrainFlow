---
id: official-cudnn-frontend-wiki/flex-attention-plans
title: cuDNN Flex Attention：区间 MaskPlan、反向和复用成本
engine: cudnn-frontend
stages:
- adapt
- optimize
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-12'
sources:
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/attention/flex_attention.md
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: 9c68c4c91f47c7f23f53530720762c11db93bb4a52e82c127174d0dd1d9a19c8
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/attention/flex_attention_design.md
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: 1af61823a766ee7b81ad7cdf10a55a33031f289066d031bde5cf8c1b953167a7
- source: nvidia-cudnn-frontend
  path: python/cudnn/flex_attention/api.py
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: 112f3ce7a630bf6ae95820c301336839c6a3bb646592e11dbb29f26ba5fadad6
- source: nvidia-cudnn-frontend
  path: python/cudnn/flex_attention/autograd.py
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: c167fb4d91e174ab2f593deaf0d6558b9e0888244c8c6b76155d1c9c5e7f5d78
---
# cuDNN Flex Attention：区间 MaskPlan、反向和复用成本

## 定位与输入语义

这是 Frontend 中实验性的 CuTe DSL 稀疏 mask attention API，不等于任意 PyTorch FlexAttention score_mod 实现。每个 query 行用正奇数个有序端点表示可见 key 区间并集 `[0,F0) ∪ [F1,F2) ...`，避免显式建立 dense Boolean mask。模型移植先确认这种表示能够保持原注意力语义；名称相同不是等价证明。

固定长度使用 BSHD，变长使用 THD 并在创建 plan 时同时提供 cu_seqlens_q/k。Q/K head 数需满足 GQA 整除关系，mask 可跨 head 共享或逐 head，端点是每个样本自己的 key 坐标，不是 flattened batch 全局索引。dtype、head_dim、device 和架构仍由当前 API/check_support 限制。

## 调用链与目录

`create_mask_plan` 将端点和样本几何转换成可复用的 MaskPlan；`plan/` 处理布局/稀疏拓扑。`FlexAttentionFwd` / `FlexAttentionBwd` 使用 APIBase 的 check_support→compile→execute；`autograd.py` 里的 `flex_attn_func` 组合分配式 wrapper 和 PyTorch backward。`kernels/sm90` 与 `sm100` 是设备实现；plan可复用不代表编译制品跨架构通用。

## 安装、运行与测试路线

官方源码安装采用项目的 editable 安装并安装 torch 依赖组；发布包需要兼容 CUDA PyTorch 和 CuTe DSL。接口声明面向 SM90/SM100/SM103，不能直接在 HCU 镜像执行这套 CUDA 配方。教程先构造 `requires_grad=True` 的 Q/K/V、建立 plan，再调用 out.backward 验证前后向；`benchmark/flex_attention/` 提供测量入口，完整单测要沿当前树查对应 test。

核对固定长度/变长、MHA/GQA/MQA、空可见行、边界端点、不同 mask/head、返回统计与确定性。返回的 max_logit 是有符号最大分数，不是绝对值最大值；没有可见 pair 的 head 为负无穷，不能简单把它标成数值故障。它不求梯度；LSE 是否作为输出与反向内部保留 LSE 是不同问题。

## 机制一：plan 复用与失效条件

把 plan 建设和 compile 放出稳态计时；相同几何、dtype、device 和 mask 才能换新 Q/K/V 值复用。变长 plan 保存自己的累计长度副本，之后修改调用者 cu_seqlens 不会自动改变 plan。模型每步样本长度或 mask 变化时，必须把重建成本计入训练关键路径，不能拿固定 plan 的独立 kernel 时间当全部成本。

显式输出/workspace 支持预编译、避免分配的执行；便利 wrapper 可能分配输出，两种路径计时要分开。Graph 捕获前确认 plan/制品、内存地址与 workspace 生命周期，而不是认为“有 plan”就自动 graph-safe。

## 机制二：前向 plan 不自动支持训练反向

`build_backward=None` 根据建 plan 时 autograd 与 Q/K/V 的 requires_grad 推断；纯推理上下文创建的 plan 可能没有 backward payload，后续用到训练时不能补一个 backward 调用就假装支持。应在训练语义下建立或显式要求 backward，验证 dQ/dK/dV、返回 LSE 和确定性路径。

稀疏 mask 的收益取决于可跳过 tile、元数据构建、调度和后向归约；不按理论 sparsity 比例直接承诺等比加速。端到端比较涵盖 plan建设、前后向、重排和临时显存，且保持相同 mask 与 loss。

## HCU 借鉴、诊断与回退

先查 HCU Flash-Train/TE 已有对应 sparse attention 和 layout，缺功能时提取端点语义、前后向保存量和 cache失效条件再实现 HIP/Triton 版本。若只能支持部分 mask，显式分发到 reference，不悄悄改成 dense causal 或删稀疏路由。

异常先检查 sample-local 端点、cu_seqlens、plan几何、是否建立反向、dtype/head及编译目标；性能低先分离首次构建和稳态，再看有效块数、load imbalance、workspace与反向。已发布包、main和实验API分别标记，版本升级联动 TE 调用方、attention总览与集成测试；没有 HCU 实测不报告迁移收益。

## 固定来源与版本

本页固定到 `develop` 的 `941078f2ce6aa0a45ac5813b81760a19c616732a`，为源码与教程阅读。发布信息从[官方 Releases](https://github.com/NVIDIA/cudnn-frontend/releases)查询，开发分支不自动等于已安装 wheel。

- [docs/fe-oss-apis/attention/flex_attention.md](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/docs/fe-oss-apis/attention/flex_attention.md)
- [docs/fe-oss-apis/attention/flex_attention_design.md](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/docs/fe-oss-apis/attention/flex_attention_design.md)
- [python/cudnn/flex_attention/api.py](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/python/cudnn/flex_attention/api.py)
- [python/cudnn/flex_attention/autograd.py](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/python/cudnn/flex_attention/autograd.py)
