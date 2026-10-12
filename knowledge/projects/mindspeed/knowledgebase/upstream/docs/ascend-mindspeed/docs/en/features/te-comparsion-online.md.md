---
id: doc-ascend-mindspeed-1a9b951fa486ee9d3f27
title: Ascend/MindSpeed / docs/en/features/te-comparsion-online.md
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
path: docs/en/features/te-comparsion-online.md
raw_sha256: edae9ae0c3ad8e262c7286539f80754ea7454fe83166ee108276783016bd23f9
sources: []
generated_body_sha256: c14273318600db7107a713ed55f81f15e02fbe323021d21517c77e0cf3e85ac8
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/te-comparsion-online.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/te-comparsion-online.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Low-Precision Online Comparison

## Problem Analysis

Precision issues are often difficult to locate in model training. To improve the efficiency of precision tracking and ensure the reliability of low-precision modules, a method for real-time monitoring of low-precision computation results is needed, while also reducing the cost of issue localization.

## Solution

The low-precision online comparison feature helps users inspect the precision differences of low-precision operations (including cast and quantmatmul) in real time by comparing computation results across different hardware (NPU, CPU) and different precisions (BF16). When this feature is enabled, computations are performed on both NPU and CPU/BF16 simultaneously, and the error values are output, allowing users to detect potential precision issues conveniently.

## Application Scenario

This feature is applicable to models that have low-precision training enabled.

## Usage

1. Add `--te-comparison-with-cpu` to the parameter list in the training script to enable low-precision online comparison using CPU computation results as the benchmark.
2. Add `--te-comparison-with-bf16` to the parameter list in the training script to enable low-precision online comparison using BF16 computation results as the benchmark.

## Effects

During low-precision computation, the error between the `cast` and `quant_matmul` operations on NPU and the precision benchmark (CPU or BF16) will be output at each step. If the error exceeds the preset range, an error will be reported and the training process will be terminated.
