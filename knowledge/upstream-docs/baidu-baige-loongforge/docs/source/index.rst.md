---
id: doc-baidu-baige-loongforge-83345edd971cd4da397e
title: baidu-baige/LoongForge / docs/source/index.rst
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
path: docs/source/index.rst
raw_sha256: 235d70b1f3ff3ab7700b17c0bc85fc43838675d4bccec69241aa7a0eb123cd58
sources: []
generated_body_sha256: e100cb53259928d33bf50ceb42fb52b64ab7fb8b0f650e63d1482a6c398a0828
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/index.rst

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/index.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

LoongForge
==========================

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
   :target: https://loongforge.readthedocs.io/en/latest/
.. image:: https://img.shields.io/github/license/baidu-baige/LoongForge.svg
   :target: https://github.com/baidu-baige/LoongForge/blob/master/LICENSE
.. image:: https://img.shields.io/github/stars/baidu-baige/LoongForge.svg?style=social
   :target: https://github.com/baidu-baige/LoongForge

A modular, scalable, and highly efficient training framework for language, multimodal, and embodied models. Built upon Megatron-LM with significant enhancements.

---

.. toctree::
   :maxdepth: 1
   :caption: Get Started

   get_started/installation
   get_started/support_model
   get_started/optimization_guide

.. toctree::
   :maxdepth: 2
   :caption: LLM Training

   llm_tutorial/quick_start_llm_pretrain
   llm_tutorial/quick_start_llm_sft
   llm_tutorial/llm_ckpt_convert
   Advanced Features <llm_tutorial/features_index>

.. toctree::
   :maxdepth: 2
   :caption: VLM Training

   vlm_tutorial/quick_start_vlm_pretrain
   vlm_tutorial/quick_start_vlm_sft
   vlm_tutorial/dataset_conversion
   vlm_tutorial/vlm_ckpt_convert
   Advanced Features <vlm_tutorial/features_index>

.. toctree::
   :maxdepth: 2
   :caption: Embodied Training

   embodied_tutorial/overview
   Quick Start <embodied_tutorial/quick_start_index>
   Advanced Features <embodied_tutorial/features_index>
   embodied_tutorial/eval_overview

.. toctree::
   :maxdepth: 1
   :caption: Diffusion Training

   wan_tutorial/quick_start_wan_training
   wan_tutorial/wan_packing
   qwen_image_edit_tutorial/quick_start_qwen_image_edit_2511_training

.. toctree::
   :maxdepth: 1
   :caption: KunLun Training

   kunlun_tutorial/README
   kunlun_tutorial/install_p800
   kunlun_tutorial/quick_start_llm_pretrain_p800
   kunlun_tutorial/quick_start_llm_sft_p800
   kunlun_tutorial/quick_start_vlm_p800

.. toctree::
   :maxdepth: 1
   :caption: Developer Guide

   advance/support_new_model

.. toctree::
   :maxdepth: 1
   :caption: More

   CONTRIBUTING
   HEADER_GUIDELINES
   faqs
