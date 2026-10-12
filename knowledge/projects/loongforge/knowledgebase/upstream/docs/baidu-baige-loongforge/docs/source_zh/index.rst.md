---
id: doc-baidu-baige-loongforge-d10006275118bbfc998c
title: baidu-baige/LoongForge / docs/source_zh/index.rst
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source_zh/index.rst
raw_sha256: 45ab429470cd5a66d1f4c6f669b4f38b3138a3fa3391bd3efcaf23ba7aace68a
sources: []
generated_body_sha256: ca9670e81eb62ebe3af9b724f536a2dda97bf634c4fbfc351052c5c9d5c1deb4
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source_zh/index.rst

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source_zh/index.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

.. LoongForge 中文文档主文件

LoongForge 中文文档
=====================

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
   :target: https://loongforge.readthedocs.io/en/latest/
.. image:: https://img.shields.io/github/license/baidu-baige/LoongForge.svg
   :target: https://github.com/baidu-baige/LoongForge/blob/master/LICENSE
.. image:: https://img.shields.io/github/stars/baidu-baige/LoongForge.svg?style=social
   :target: https://github.com/baidu-baige/LoongForge

面向语言、多模态与具身模型的模块化、可扩展、高效训练框架。基于 Megatron-LM 并进行了大量增强。

---

.. toctree::
   :maxdepth: 1
   :caption: 快速开始

   get_started/installation
   get_started/support_model
   get_started/optimization_guide

.. toctree::
   :maxdepth: 2
   :caption: LLM 训练

   llm_tutorial/quick_start_llm_pretrain
   llm_tutorial/quick_start_llm_sft
   llm_tutorial/llm_ckpt_convert
   高级特性 <llm_tutorial/features_index>

.. toctree::
   :maxdepth: 2
   :caption: VLM 训练

   vlm_tutorial/quick_start_vlm_pretrain
   vlm_tutorial/quick_start_vlm_sft
   vlm_tutorial/dataset_conversion
   vlm_tutorial/vlm_ckpt_convert
   高级特性 <vlm_tutorial/features_index>

.. toctree::
   :maxdepth: 2
   :caption: Embodied 训练

   embodied_tutorial/overview.md
   快速入门 <embodied_tutorial/quick_start_index.md>
   高级特性 <embodied_tutorial/features_index.md>
   embodied_tutorial/eval_user_guide.md

.. toctree::
   :maxdepth: 1
   :caption: Diffusion 训练

   wan_tutorial/quick_start_wan_training
   wan_tutorial/wan_packing

.. toctree::
   :maxdepth: 1
   :caption: 昆仑训练

   kunlun_tutorial/README
   kunlun_tutorial/install_p800
   kunlun_tutorial/quick_start_llm_pretrain_p800
   kunlun_tutorial/quick_start_llm_sft_p800
   kunlun_tutorial/quick_start_vlm_p800

.. toctree::
   :maxdepth: 1
   :caption: 开发指南

   advance/support_new_model

.. toctree::
   :maxdepth: 1
   :caption: 更多

   HEADER_GUIDELINES
   faqs
