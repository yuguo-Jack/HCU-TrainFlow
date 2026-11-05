---
id: doc-ascend-mindspeed-llm-1d8e666311a8be704205
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/environment_variable.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
path: docs/en/pytorch/features/mcore/environment_variable.md
raw_sha256: a4ad0f5a73914ac5a45202350b9f50f4f27c19c0105ff3974e36e8f93a87fb1c
sources: []
generated_body_sha256: 20bfafac574b2f0adb605c30f43c0cc6fb6c4c1ca5a6be237bf41361e6e329a2
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/environment_variable.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/pytorch/features/mcore/environment_variable.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Model Script Environment Variables

The environment variables used by the scripts in the preceding model list are as follows.

| Environment Variable |  Description |
|-----------------------------|-------------------------------------|
| [ASCEND_LAUNCH_BLOCKING](https://gitcode.com/Ascend/pytorch/blob/master/docs/en/api/environment_variable/op_execution/ASCEND_LAUNCH_BLOCKING.md) | `1`: Forces operators to run in synchronous mode. This degrades performance and disables the `task_queue` optimization feature.<br>`0`: This increases memory use and creates an out-of-memory (OOM) risk. |
| [ASCEND_SLOG_PRINT_TO_STDOUT](https://gitcode.com/cann/runtime/blob/9.2.0/docs/zh/env_vars/ASCEND_SLOG_PRINT_TO_STDOUT_deprecated.md) | `0`: Disables log output to the screen. Logs use the default output method and are saved in log files.<br>`1`: Enables log output to the screen. Logs are not saved in log files and are printed directly to the screen. |
| [HCCL_WHITELIST_DISABLE](https://gitcode.com/cann/hccl/blob/master/docs/en/user_guide/hccl_env/HCCL_WHITELIST_DISABLE.md) | Enables or disables the HCCL allowlist. `1` disables it, and `0` enables it. |
| [HCCL_CONNECT_TIMEOUT](https://gitcode.com/cann/hccl/blob/master/docs/en/user_guide/hccl_env/HCCL_CONNECT_TIMEOUT.md) | Sets the HCCL timeout. The default value is 120. |
| CUDA_DEVICE_MAX_CONNECTIONS | Specifies the number of hardware queues that a task stream can use or map to. |
| [TASK_QUEUE_ENABLE](https://gitcode.com/Ascend/pytorch/blob/master/docs/en/api/environment_variable/op_execution/TASK_QUEUE_ENABLE.md) | Controls the optimization level of the `task_queue` operator dispatch queue.<br>`0`: Disables optimization.<br>`1`: Enables level 1 optimization.<br>`2`: Enables level 2 optimization. |
| [COMBINED_ENABLE](https://gitcode.com/Ascend/pytorch/blob/master/docs/en/api/environment_variable/op_execution/COMBINED_ENABLE.md) | Sets the `combined` flag.<br>`0`: Disables this feature.<br>`1`: Enables this feature for optimized scenarios that combine two non-contiguous operators. |
| [PYTORCH_NPU_ALLOC_CONF](https://gitcode.com/Ascend/pytorch/blob/master/docs/en/api/environment_variable/memory_management/PYTORCH_NPU_ALLOC_CONF.md) | Switch for memory fragmentation optimization. The default value is `expandable_segments:False`. Set the value to `expandable_segments:True` to enable memory management and fragmentation reclamation. |
| [ASCEND_RT_VISIBLE_DEVICES](https://gitcode.com/cann/runtime/blob/master/docs/zh/env_vars/ASCEND_RT_VISIBLE_DEVICES.md) | Specifies which devices are visible to the current process. You can specify one or more device IDs at a time. This environment variable lets you adjust the devices in use without modifying the application. |
| NPUS_PER_NODE | Configures the number of NPUs used on a compute node. |
| [HCCL_SOCKET_IFNAME](https://gitcode.com/cann/hccl/blob/master/docs/en/user_guide/hccl_env/HCCL_SOCKET_IFNAME.md) | Specifies the network interface card configuration used for HCCL Socket communication. |
| GLOO_SOCKET_IFNAME | Specifies the network interface card configuration used for Gloo Socket communication. |
| [HCCL_LOGIC_SUPERPOD_ID](https://gitcode.com/cann/hccl/blob/master/docs/en/user_guide/hccl_env/HCCL_LOGIC_SUPERPOD_ID.md) | Specifies the logical SuperPoD ID of the current device. If you use ROCE, different multi-node superpods have different IDs, from 0 to `N`. |
| [CPU_AFFINITY_CONF](https://gitcode.com/Ascend/pytorch/blob/master/docs/en/api/environment_variable/performance_tuning/CPU_AFFINITY_CONF.md) | Enables coarse-grained or fine-grained CPU core binding. This configuration helps avoid thread contention, improve cache hit rates, avoid memory access across NUMA nodes, reduce task scheduling overhead, and improve task execution efficiency. |
| [NPU_ASD_ENABLE](https://gitcode.com/Ascend/pytorch/blob/master/docs/en/api/environment_variable/eigenvalue_detection/NPU_ASD_ENABLE.md) | `0`: Disables detection.<br>`1`: Enables feature detection, prints exception logs, and does not raise alarms.<br>`2`: Enables detection and raises alarms.<br>`3`: Enables detection, raises alarms, and records process data in device-side logs at the `info` level. |
| [TORCH_HCCL_ASYNC_ERROR_HANDLING](https://gitcode.com/Ascend/pytorch/blob/master/docs/en/api/environment_variable/collective_communication/TORCH_HCCL_ASYNC_ERROR_HANDLING.md) | When you use HCCL as the communication backend, this environment variable controls whether asynchronous error handling is enabled. The default value is 1.<br>`0`: Disables asynchronous error handling.<br>`1`: Enables asynchronous error handling. |
