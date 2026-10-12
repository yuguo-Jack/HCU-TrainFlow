---
id: doc-yuguo-jack-hyperloom-f3c36dea7cd122fab5b1
title: yuguo-Jack/Hyperloom / docs/kernelforge/index.rst
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
path: docs/kernelforge/index.rst
raw_sha256: a79b9a7ab50b08ff00306f00b8825214999052e09b8ba45f809933f2d4b15b63
sources: []
generated_body_sha256: 15a1210be37271244d2ea82ce89e956dcdf6fbb9a04c6976ac65bb31fefc22aa
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/kernelforge/index.rst

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/kernelforge/index.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

.. meta::
  :description: KernelForge autonomously develops and optimizes high-performance GPU kernels on AMD Instinct hardware using domain-specialized AI agents and hardware-counter-driven measurement.
  :keywords: KernelForge, GPU kernel, AMD Instinct, MI355X, gfx950, optimization, agentic, ROCm, Composable Kernel, Triton, HIP, hipBLASLt, FlyDSL, PMC, documentation

***********
KernelForge
***********

KernelForge is an autonomous, measurement-driven system for developing and
optimizing high-performance GPU kernels on AMD Instinct hardware. It replaces
weeks of manual expert iteration with domain-specialized AI agents for
Composable Kernel, Triton, HIP, hipBLASLt, FlyDSL and AITER that build,
benchmark, and profile every change against real hardware counters — then learn
from each campaign.

KernelForge ships inside Hyperloom as the built-in kernel-optimization agent: installing
Hyperloom installs it, and its standalone CLI stays available as ``kernelforge``.
The source lives under ``src/kernelforge`` in the Hyperloom repository.

.. grid:: 2
  :gutter: 3

  .. grid-item-card:: Install

    * :doc:`Quickstart </kernelforge/install/quickstart>`

  .. grid-item-card:: Overview

    * :doc:`Architecture </kernelforge/conceptual/architecture>`
    * :doc:`Optimization loop </kernelforge/conceptual/optimization-loop>`

  .. grid-item-card:: How to

    * :doc:`Run a campaign </kernelforge/how-to/run-a-campaign>`
    * :doc:`Autonomous overnight loop </kernelforge/how-to/autonomous-loop>`
    * :doc:`Fuse a launch-bound decode path </kernelforge/how-to/kernel-fusion>`
    * :doc:`Debug task preparation </kernelforge/how-to/debug-task-preparation>`
    * :doc:`Add a kernel backend, tool, or knowledge </kernelforge/how-to/extending>`

  .. grid-item-card:: Reference

    * :doc:`CLI reference </kernelforge/reference/cli>`
    * :doc:`Experience store </kernelforge/reference/experience-store>`
    * :doc:`Deployment modes </kernelforge/reference/deployment-modes>`
    * :doc:`API reference </kernelforge/reference/api-reference>`

To contribute to the documentation, see
`Contributing to Hyperloom <https://github.com/AMD-AGI/Hyperloom/blob/main/CONTRIBUTING.md>`_.
