---
id: doc-ascend-mindspeed-b9180de14dfe1aa831e1
title: Ascend/MindSpeed / docs/en/features/npu_datadump.md
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
path: docs/en/features/npu_datadump.md
raw_sha256: fb121d319717b2835bb52bb30b6d9bfc7a93f3337473ad793be4e20d36605a17
sources: []
generated_body_sha256: 234b04a2b7f7373449773e3416e183ffb6c8bd4d12c151900a0504a6ff56e443
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/npu_datadump.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/npu_datadump.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Ascend MindStudio Training Tools for Precision Comparison

## Background and Challenges

During large model training, even minimal data fluctuations can lead to a significant drop in the final evaluation score. This often results in a substantial workload for model precision comparison, especially in cross-platform (GPU to NPU) comparison scenarios. With the msProbe tool, Ascend chips can complete the collection of full-network training data relatively quickly, and by leveraging deterministic computation, precision comparison can be achieved. However, using msProbe requires manual code modification and configuration adjustments, which introduces certain inconveniences when enabling it within MindSpeed.

## Solution

To address the requirements above, the "Precision Comparison" feature has been introduced. MindSpeed integrates and simplifies the use of the msProbe tool, allowing users to quickly perform full-network precision data dumping and comparison by setting parameters.

## Application Scenario

When precision comparison or reproduction of specific scenarios is required.

## Usage

To enable this feature, add `--npu-datadump` to the script. Before use, modify the `config.json` file as described below. By default, statistics precision data for `RANK0` and `STEP0` is collected.
You can adjust various options for full-network dumping by modifying `mindspeed/functional/npu_datadump/config.json`.
You can use msProbe to compare the precision of dumped data by modifying `mindspeed/functional/npu_datadump/compare.json`.
For more details on config settings refer to [the official msProbe tutorial](https://gitcode.com/Ascend/msprobe/blob/master/docs/en/user_guide/dump/config_json_introduct.md).

- The Lite backend is not currently supported.
- The dumped data is saved in the Megatron-LM directory by default.

## Effects

The precision comparison feature allows for quick identification of precision errors during full-network execution.
