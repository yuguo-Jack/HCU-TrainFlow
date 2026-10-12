---
id: doc-yuguo-jack-hyperloom-3e9a9deaa88ec35bf250
title: yuguo-Jack/Hyperloom / docs/index.rst
engine: hyperloom
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: yuguo-Jack/Hyperloom
commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
path: docs/index.rst
raw_sha256: 9d89d45708226937754745c5d3325e2983669695bc6b9d4cc3f2b09986061ae0
sources: []
generated_body_sha256: a4750b9e16127c3f58826477236a780fff743d9c65b005b6a6167096adf420ab
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/index.rst

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/index.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

.. meta::
  :description: Learn how Hyperloom autonomously optimizes large language model inference on AMD GPUs — from installation and components to API reference and case studies.
  :keywords: Hyperloom, LLM inference, AMD GPU, optimization, agentic, ROCm, GEMM tuning, kernel optimization, throughput, TraceLens, Magpie, GEAK, IntelliKit, documentation

***********************
Hyperloom documentation
***********************

ROCm Hyperloom is an autonomous agentic system designed to optimize end-to-end inference workloads
on AMD GPUs. It uses advanced AI agents and profiling tools to analyze a workload, identify performance
bottlenecks, implement targeted optimizations, and validate the performance and correctness of the
optimizations -- all without requiring manual intervention.
 
The Hyperloom source code is hosted on GitHub at `https://github.com/AMD-AGI/Hyperloom <https://github.com/AMD-AGI/Hyperloom>`_.

.. grid:: 2
  :gutter: 3

  .. grid-item-card:: Install

    * :doc:`Install on Docker or bare metal </install/install>`
    * :doc:`Install on a Slurm cluster </install/slurm>`

  .. grid-item-card:: Components

    * :doc:`Components </components/index>`
    * :doc:`Hyperloom optimization loop </conceptual/optimization-loop>`

  .. grid-item-card:: How to

    * :doc:`Run a Hyperloom optimization </how-to/optimize>`
    * :doc:`Optimize your own workload </how-to/optimize-custom-workload>`
    * :doc:`Quantization with AMD Quark </how-to/quantization-quark>`

  .. grid-item-card:: Reference

    * :doc:`API reference </reference/api-reference>`
    * :doc:`Environment variables </reference/environment-variables>`
    * :doc:`Authentication and credentials </reference/authentication>`
    * :doc:`Kernel optimization execution path </reference/kernel-execution-path>`
    * :doc:`Operations and self-hosting </reference/operations>`
    * :doc:`Upgrade guide </reference/upgrade>`
    * :doc:`Session output schema </reference/session-breakdown>`
    * :doc:`Knowledge base integration </reference/integrate-kb>`
    * :doc:`Operator scripts </reference/operator-scripts>`
    * :doc:`Multi-node inference optimization </reference/multi-node>`
    * :doc:`Troubleshooting </reference/troubleshooting>`

To contribute to the documentation, see `Contributing to Hyperloom <https://github.com/AMD-AGI/Hyperloom/blob/main/CONTRIBUTING.md>`_.

Hyperloom is released under the MIT license. For details, see the :doc:`License <license>` page.
