---
id: doc-nvidia-nemo-megatron-bridge-d9be4758f618e1ffa337
title: NVIDIA-NeMo/Megatron-Bridge / docs/training/README.md
engine: bridge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA-NeMo/Megatron-Bridge
commit: 34ddd53b0e023d93f107f29b7dc61f9c5dd76a57
path: docs/training/README.md
raw_sha256: 0a93ea272713be2af229f9ec50b3770a9220275073b69ef15b8bf7039d4a9023
sources: []
generated_body_sha256: 520e5907a167dbd470d71058242c1a4450eb2afbec6f5f16486d0a2412517583
source_state: current-scan
---

# NVIDIA-NeMo/Megatron-Bridge / docs/training/README.md

[Original at fixed commit](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/34ddd53b0e023d93f107f29b7dc61f9c5dd76a57/docs/training/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Training and Customization

This directory contains comprehensive documentation for training and customizing models with Megatron Bridge. Learn how to configure training, optimize performance, and customize training workflows.

## Quick Navigation

### I want to

**🚀 Get started with training**
→ Start with [Configuration Container Overview](config-container-overview.md) and [Data Preparation](data-preparation.md) to understand the training setup

**⚙️ Configure training parameters**
→ See [Training Loop Settings](training-loop-settings.md) and [Optimizer & Scheduler](optimizer-scheduler.md)

**📊 Monitor and profile training**
→ Check [Logging](logging.md) and [Profiling](profiling.md) guides

**💾 Manage checkpoints**
→ Read [Checkpointing](checkpointing.md) for saving and resuming training

**⚡ Optimize performance**
→ Explore [Performance Guide](../performance-guide.md) and [Performance Summary](../performance-summary.md)

**🔧 Customize training**
→ See [PEFT](peft.md), [Distillation](../modelopt/distillation.md), [Entry Points](entry-points.md), and [Callbacks](callbacks.md)

## Core Training Documentation

### Configuration and Setup

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[Configuration Container Overview](config-container-overview.md)** | Central configuration object for all training settings | First time setting up training |
| **[Entry Points](entry-points.md)** | Training entry points and execution flow | Understanding how training starts |
| **[Data Preparation](data-preparation.md)** | Dataset formats for pretraining, SFT, PEFT, and VLM fine-tuning | Preparing data or choosing dataset config fields |
| **[Training Loop Settings](training-loop-settings.md)** | Training loop parameters and configuration | Configuring batch sizes, iterations, validation |

### Optimization and Performance

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[Optimizer & Scheduler](optimizer-scheduler.md)** | Optimizer and learning rate scheduler configuration | Setting up optimization |
| **[Mixed Precision](mixed-precision.md)** | Mixed precision training for memory efficiency | Reducing memory usage |
| **[Communication Overlap](communication-overlap.md)** | Overlapping communication with computation | Optimizing distributed training |
| **[Hierarchical Context Parallel](hierarchical-context-parallel.md)** | Hierarchical `a2a+p2p` context parallel guidance | Advanced long-sequence scaling |
| **[Attention Optimizations](attention-optimizations.md)** | Optimizing attention mechanisms | Improving training speed |
| **[Activation Recomputation](activation-recomputation.md)** | Gradient checkpointing strategies | Reducing memory footprint |
| **[CPU Offloading](cpu-offloading.md)** | Offloading to CPU for memory management | Working with limited GPU memory |

### Monitoring and Debugging

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[Logging](logging.md)** | Logging configuration and TensorBoard/WandB integration | Monitoring training progress |
| **[Profiling](profiling.md)** | Performance profiling and analysis | Identifying bottlenecks |
| **[Theoretical Memory Estimator](memory-estimator.md)** | Formula-based per-GPU memory planning | Sizing dense and MoE training configs |
| **[Resiliency](resiliency.md)** | Handling failures and recovery | Building robust training pipelines |

### Advanced Features

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[PEFT](peft.md)** | Parameter-Efficient Fine-Tuning (LoRA, etc.) | Fine-tuning with limited resources |
| **[Packed Sequences](packed-sequences.md)** | Sequence packing for efficiency | Optimizing data loading |
| **[Megatron FSDP](megatron-fsdp.md)** | Stable overview of Megatron FSDP | Choosing an FSDP path |
| **[Distillation](../modelopt/distillation.md)** | Knowledge distillation techniques | Transferring knowledge between models |
| **[Checkpointing](checkpointing.md)** | Checkpoint saving, loading, and resuming | Managing training state |
| **[Callbacks](callbacks.md)** | Inject custom logic into training loop | Custom logging, metrics, third-party integrations |

## Training Workflow

A typical training workflow involves:

1. **Configure Training** - Set up `ConfigContainer` with model, data, and training parameters
2. **Prepare Data** - Configure dataset loading and preprocessing with the right data format
3. **Set Optimization** - Configure optimizer, scheduler, and mixed precision
4. **Enable Monitoring** - Set up logging and profiling
5. **Configure Checkpointing** - Set up checkpoint saving and resuming
6. **Launch Training** - Start training with configured entry points
7. **Monitor Progress** - Track metrics via logging and profiling
8. **Resume if Needed** - Use checkpointing to resume from saved state

## Related Documentation

- **[Main Documentation Index](../index.md)** - Return to main documentation
- **[Performance Guide](../performance-guide.md)** - Comprehensive performance optimization guide
- **[Performance Summary](../performance-summary.md)** - Quick performance reference
- **[Recipe Usage](../recipe-usage.md)** - Using training recipes
- **[Parallelisms](../parallelisms.md)** - Understanding distributed training strategies
- **[Bridge Guide](../bridge-guide.md)** - Working with Hugging Face models

## Common Training Scenarios

### 🆕 First-Time Training Setup

1. [Configuration Container Overview](config-container-overview.md) - Understand the configuration system
2. [Data Preparation](data-preparation.md) - Choose the right dataset format and config fields
3. [Entry Points](entry-points.md) - Learn how to start training
4. [Training Loop Settings](training-loop-settings.md) - Configure basic training parameters
5. [Logging](logging.md) - Set up monitoring

### ⚡ Performance Optimization

1. [Performance Guide](../performance-guide.md) - Comprehensive optimization strategies
2. [Mixed Precision](mixed-precision.md) - Enable mixed precision training
3. [Communication Overlap](communication-overlap.md) - Optimize distributed training
4. [Activation Recomputation](activation-recomputation.md) - Reduce memory usage
5. [Profiling](profiling.md) - Identify bottlenecks

### 💾 Production Training

1. [Checkpointing](checkpointing.md) - Reliable checkpoint management
2. [Resiliency](resiliency.md) - Handle failures gracefully
3. [Logging](logging.md) - Comprehensive monitoring
4. [Profiling](profiling.md) - Performance analysis

### 🔧 Customization

1. [PEFT](peft.md) - Parameter-efficient fine-tuning
2. [Distillation](../modelopt/distillation.md) - Knowledge distillation
3. [Entry Points](entry-points.md) - Custom training workflows
4. [Callbacks](callbacks.md) - Inject custom logic (third-party integrations)

---

**Ready to start training?** Begin with [Configuration Container Overview](config-container-overview.md) or return to the [main documentation](../README.md).