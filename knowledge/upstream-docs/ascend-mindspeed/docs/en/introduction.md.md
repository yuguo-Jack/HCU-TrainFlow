---
id: doc-ascend-mindspeed-ee96db90901b4ceb58a0
title: Ascend/MindSpeed / docs/en/introduction.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/introduction.md
raw_sha256: 8fb0fa2dbde58e427ca191d2c2d2f3b818be22f2dbc154c6ce0f8ab6dc570eeb
sources: []
generated_body_sha256: 12afe5ec89ae6ecf3efd26e1e088afa22f9e8e4e1f2e4e6069d21df44678bcbc
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/introduction.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/introduction.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Introduction

## Overview

MindSpeed Core is an acceleration library for large models on Huawei Ascend devices. Large model training is a highly complex process involving numerous technologies and challenges. A key difficulty is that large model training requires substantial device memory resources, posing a significant challenge for compute cards. To address the issue of insufficient device memory on a single compute card, the industry has developed third-party large model acceleration libraries such as Megatron and DeepSpeed. These libraries partition models and input data, distribute them across different compute cards, and then aggregate the results through collective communication. Ascend provides the MindSpeed Core acceleration library to enable rapid migration of customer large model services to Ascend devices, with support for Ascend-specific algorithms to ensure out-of-the-box usability.

## MindSpeed Core Architecture

The overall architecture of MindSpeed Core is illustrated in the figure below, which is divided into three layers:

- Acceleration features:
Provides a rich variety of acceleration features across multiple dimensions such as parallelism, memory, communication, and computation.
Features are designed with cohesion and decoupling, enabling quick one-click activation and convenient secondary development.

- Tool/functional features:
Powerful and easy-to-use tool features accelerate the end-to-end model tuning process, significantly improving development efficiency.
Automatic parallel strategy search uses small-scale simulation to quickly provide near-optimal parallel configurations.

- Patch/feature management:
Non-intrusive patch management facilitates rapid iteration between versions.
Independent and decoupled management of various features enables lightweight and quick application to your own framework.

Figure 1 MindSpeed architecture

![MindSpeed Core architecture](./figures/01_architecture_mindspeed_core_en.png)

## Features

MindSpeed features consist of seven major modules: Megatron feature support, parallelism strategies, memory optimization, affinity computing, communication optimization, key scenario support, and multimodality.
