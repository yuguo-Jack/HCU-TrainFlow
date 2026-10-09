---
id: official-cudnn-frontend-wiki/build-run-test
title: cuDNN Frontend 编译安装、运行示例与测试路线
engine: cudnn-frontend
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-cudnn-frontend
  path: README.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 4cabe0bbf2a76d4b5bbb1b06eae8d1de73aaf8cddb756e38903b6f62689b9279
- source: nvidia-cudnn-frontend
  path: setup.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 1751eb8280739e6b7be513a36eaaaec357ce406c2a4d0f76290efafe1e615cdd
- source: nvidia-cudnn-frontend
  path: pyproject.toml
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 27fb5d86264af4263cb8faec5597b6c412a499c0b69d04bb803eac73e868c865
- source: nvidia-cudnn-frontend
  path: CMakeLists.txt
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 2b29c9721c9a03fe90378f323a5bdd2c11c2381fce8f43cfd3c9cfe6e8df9ce6
- source: nvidia-cudnn-frontend
  path: samples/cpp/CMakeLists.txt
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 082d97b1796be55f09fa144c9a510be9ccd3db25725b7eee483492bcbf838ed9
- source: nvidia-cudnn-frontend
  path: samples/cpp/sdpa/fp16_bwd.cpp
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 62f47b922848b39b6ec9ee07f2dbac8e65b2f46cfffb1e327e9b050a4d9f6bc2
- source: nvidia-cudnn-frontend
  path: docs/quickstart.mdx
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 93ed00e9f0f26ad5a4f31971b226ffaef47477e435e61cc66e4f9f9b47c456ea
- source: nvidia-cudnn-frontend-docs
  path: quickstart
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: efb405e71ec606566ab443881a1101611dbc8a64b45cb487a6c421efd2c1a1c4
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/quickstart.html
  revision_kind: web-content-fingerprint
---

# cuDNN Frontend 编译安装、运行示例与测试路线

## 两类安装路径

C++ Frontend 主要通过头文件接入；编译应用和样例仍需匹配 CUDA/cuDNN、编译器及头文件/库路径。Python 包包含 Python 接口及构建/运行依赖；开放 DSL kernel 还可能依赖 CUDA Python、CUTLASS DSL 等。不要只依据 README 中最低 cuDNN 版本推断新 SDPA 或融合功能都可用，具体能力还受单项支持面限制。

官方 NV 环境可按当前 README 使用 `python -m pip install nvidia-cudnn-frontend`，源码开发则选定提交后依据 `setup.py`/`pyproject.toml` 执行源码安装。HCU-TrainFlow 主控安装不需要此包；HCU 训练按当前 HCU 工程已有脚本安装对应实现，避免拉入 NV wheel 污染运行环境。

## 官方示例的执行顺序

1. 读 `docs/quickstart.mdx`，确认图输入输出、计算与中间 dtype，以及 setup 和 execute 的区别。
2. 从 `samples/python/50_sdpa_forward.ipynb` 与 `51_sdpa_backward.ipynb` 开始，在符合要求的 NV 环境比较输出和梯度；不能只跑 inference forward。
3. C++ 样例按当前 CMake 配置构建，查看产生的 samples 测试程序。`fp16_bwd.cpp` 自带的示例选择名为 `Toy sdpa backward`，运行前用生成程序的帮助/用例列表核对。
4. 回到目标模型的真实 shape、stride、mask、dtype、group 和 graph 模式；教程中的小尺寸与宽松误差阈值仅为演示。

构建步骤应记录 source SHA、CUDA/cuDNN/框架/DSL 版本、编译配置、链接库和加载位置。源码已向新的 Python 图封装发展，`cudnn.Graph` 和较显式的 `cudnn.pygraph` 教程可能并存；不能将不同版本片段拼成一段未经验证的命令。

## 正确性与性能验收

单测至少覆盖 forward、backward、非连续布局、变长/边界、RNG、不同 head/专家规模及实际需要的精度。运行数为零、unsupported、skip 与 fallback 分开报告。性能分构图/编译、首次调用、稳态 execute 和模型墙钟；同步位置与 workspace 分配边界保持一致。

测试目录会重组。旧 notebook 仍可能引用已经迁移的 `test/python/test_mhas.py`；本次主干实际应在 `test/python/sdpa/` 等路径继续查找。更新时先查树和测试收集，不把旧文档链接存在过当成当前测试覆盖。

## 来源与版本复核

- [nvidia-cudnn-frontend: README.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/README.md)
- [nvidia-cudnn-frontend: setup.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/setup.py)
- [nvidia-cudnn-frontend: pyproject.toml](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/pyproject.toml)
- [nvidia-cudnn-frontend: CMakeLists.txt](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/CMakeLists.txt)
- [nvidia-cudnn-frontend: samples/cpp/CMakeLists.txt](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/cpp/CMakeLists.txt)
- [nvidia-cudnn-frontend: samples/cpp/sdpa/fp16_bwd.cpp](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/cpp/sdpa/fp16_bwd.cpp)
- [nvidia-cudnn-frontend: docs/quickstart.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/quickstart.mdx)
- [nvidia-cudnn-frontend-docs: quickstart](https://docs.nvidia.com/deeplearning/cudnn/latest/quickstart.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
