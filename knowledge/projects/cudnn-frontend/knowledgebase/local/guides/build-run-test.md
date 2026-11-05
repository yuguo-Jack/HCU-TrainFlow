---
id: official-cudnn-frontend-wiki/build-run-test
title: cuDNN Frontend 编译安装、运行示例与测试路线
engine: cudnn-frontend
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
sources:
- source: nvidia-cudnn-frontend
  path: README.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 13505fbe9dda7756a916f924600a2e7b44e22515129aa4ba16971f02e1c2e790
- source: nvidia-cudnn-frontend
  path: setup.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 2f928bd4305e6dda4cda1f74dba910a1706eb65028dfaf855d04c74fd7c0ab55
- source: nvidia-cudnn-frontend
  path: pyproject.toml
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 16a9fb227c1c78b00a791f5bca576074e3d0cc249603675de822c69b0e30efb0
- source: nvidia-cudnn-frontend
  path: CMakeLists.txt
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: fde803f82ba122a58da737d194479cb613901f90412876c42b36563279d5c304
- source: nvidia-cudnn-frontend
  path: samples/cpp/CMakeLists.txt
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: bffe7f6b1a813839e39ae67a1614458c13cced33d8ed89f3f6291713ad17d13e
- source: nvidia-cudnn-frontend
  path: samples/cpp/sdpa/fp16_bwd.cpp
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 62f47b922848b39b6ec9ee07f2dbac8e65b2f46cfffb1e327e9b050a4d9f6bc2
- source: nvidia-cudnn-frontend
  path: docs/quickstart.mdx
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: b2d16117ddd1956a6b5fe4e231b5a9260dce41f6130b47627e77d2b77e8a378a
- source: nvidia-cudnn-frontend-docs
  path: quickstart
  commit: 62596f777aca773f340569b88fbd42c5fcd807249e8a188810cd38297d19cab9
  sha256: a360753931c52ab40d573da739ed74d9d730d7c0063c3634116f89b7075f6c7c
  url: https://docs.nvidia.com/cudnn/quickstart/
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

当前 `a7269d7607db` 已把 Python binding 从 pybind11 改为 nanobind 3.0.1以上且小于4，CMake 最低3.26；源码安装须按本版 build-system 准备，旧构建依赖不是当前合同。可选 `CUDNN_FRONTEND_PYTHON_STABLE_ABI=ON` 仅接受 CPython≥3.12 且 GIL 开启，默认 OFF；它不把整个 Python 支持下界提高到3.12，也不证明所有可选 GPU runtime/平台都有对应 wheel。

2026-11-04 的 `f88a1ef2a35b` 保留上述 binding 合同，将项目版本升至1.33.0，依赖中的 `nvidia-cutlass-dsl[cu13]` 下界升为4.8.0；绕过依赖解析时仍受各 engine 的版本/架构门禁。当前 Windows 动态加载要求 CUDA13 headers/runtime，并校验 override 指向的 runtime major；Linux 多个 libcudart 匹配改为告警并保留首个匹配。应保存实际加载位置，不能据导入成功推断加载的是期望版本。

新官网 Quick Start 使用 `with cudnn.Graph(...) as graph` 构图，退出 context 时 validate/build，之后 `graph(...)` 执行；inputs/outputs 名字列表确定调用次序。构图时只用 tensor 元数据，执行时才读值。这个高级入口与显式 pygraph 的计划/工作区生命周期可以对照，不能把教程的矩阵尺寸、宽松误差和性能当训练验收；主控不因此安装 NV 包。

## 正确性与性能验收

单测至少覆盖 forward、backward、非连续布局、变长/边界、RNG、不同 head/专家规模及实际需要的精度。运行数为零、unsupported、skip 与 fallback 分开报告。性能分构图/编译、首次调用、稳态 execute 和模型墙钟；同步位置与 workspace 分配边界保持一致。

测试目录会重组。旧 notebook 仍可能引用已经迁移的 `test/python/test_mhas.py`；本次主干实际应在 `test/python/sdpa/` 等路径继续查找。更新时先查树和测试收集，不把旧文档链接存在过当成当前测试覆盖。

## 来源与版本复核

- [nvidia-cudnn-frontend: README.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/README.md)
- [nvidia-cudnn-frontend: setup.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/setup.py)
- [nvidia-cudnn-frontend: pyproject.toml](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/pyproject.toml)
- [nvidia-cudnn-frontend: CMakeLists.txt](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/CMakeLists.txt)
- [nvidia-cudnn-frontend: samples/cpp/CMakeLists.txt](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/samples/cpp/CMakeLists.txt)
- [nvidia-cudnn-frontend: samples/cpp/sdpa/fp16_bwd.cpp](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/samples/cpp/sdpa/fp16_bwd.cpp)
- [nvidia-cudnn-frontend: docs/quickstart.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/quickstart.mdx)
- [nvidia-cudnn-frontend-docs: quickstart](https://docs.nvidia.com/cudnn/quickstart/)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
