---
id: doc-ascend-mindspeed-f0a88e2072d985ea2fbc
title: Ascend/MindSpeed / docs/en/features/unaligned-ulysses-context-parallel.md
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
path: docs/en/features/unaligned-ulysses-context-parallel.md
raw_sha256: 479a9e9da47c3fbb6293cec60d88a62e171eb594ad88225e1e854016c9f1fb6b
sources: []
generated_body_sha256: 4fe3dd0f45d9cfd80a33d8f48f854b14a5e6d831d3ac5fc86e71b61d8b43a7a0
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/unaligned-ulysses-context-parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/unaligned-ulysses-context-parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Unaligned Ulysses Long-Sequence Parallelism

## Background and Challenges

With the development of generative AI and scientific research models, long sequence training has become increasingly important. However, the traditional Ulysses design requires that the sequence length must be divisible by the Context Parallel size (CP size). This imposes limitations when processing dynamic or irregular inputs, especially in multimodal apps where the sequence length of input data may be unpredictable and frequently changing. Therefore, a mechanism is needed to support operations in these unaligned scenarios to accommodate a wider range of application scenarios.

## Solution

To address the limitations of the traditional Ulysses design when processing unaligned sequence lengths, the "Unaligned Ulysses" mechanism introduces an abstract base class `GatherSizeCalculator` to provide an interface for calculating the gather size. The gather size typically refers to the size of the output tensor along the `gather_idx` dimension after the all-to-all communication (in the Ulysses mechanism). This base class defines the `calculate()` method that any concrete implementation must provide, which returns the gather size as an integer or None.

Based on this interface, two specific strategies are implemented: `DefaultGatherSizeCalculator` and `DynamicGatherSizeCalculator`. The former returns `None` by default, meaning aligned Ulysses long-sequence parallelism is used; the latter dynamically calculates the gather size based on the attention mask sequence length of the current batch. This design enables the system to flexibly adapt to the needs of different scenarios, which is especially important in multimodal domains when the sequence length cannot be evenly divided by the CP size.

Additionally, in the `UlyssesContextAttention` class, users are allowed to inject a `gather_size_calculator` instance, enabling the system to flexibly choose different gather size calculation methods to meet the needs of various scenarios.

## Application Scenario

The "Unaligned Ulysses" feature is suitable for the following typical scenarios:

- **Multimodal learning**: When processing multiple types of data such as images, videos, and text, the sequence lengths of different data types vary significantly, making it difficult to unify them to a fixed CP size.
- **Real-time data analysis**: When processing streaming data, the arrival time of data is uncertain, resulting in potentially different sequence lengths for each processing operation.
- **Personalized recommendation systems**: The sequence lengths of user behavior data are typically different, and unaligned operations are also required in such scenarios.

## Usage

To leverage the "Unaligned Ulysses" feature, users can pass in a custom Calculator based on the `GatherSizeCalculator` base class according to business requirements, or directly use the predefined `DynamicGatherSizeCalculator`. The basic steps are as follows:

1. Configure the context parallel size to be greater than 1 in the launch script, for example, `--context-parallel-size [int]`. Also configure `--context-parallel-algo ulysses_cp_algo`.
2. Create a custom calculator class that inherits from `GatherSizeCalculator` and implement the `calculate()` method. When initializing the `UlyssesContextAttention` object, pass the custom `gather_size_calculator` instance through the constructor parameter.
3. If complex custom logic is not required, you can directly use `DynamicGatherSizeCalculator`, which automatically calculates the gather size based on the attention mask sequence length of the current batch.

```python
# Example code
import megatron.core.parallel_state as ps
from mindspeed.core.context_parallel.ulysses_context_parallel.ulysses_context_parallel import UlyssesContextAttention, GatherSizeCalculator, DynamicGatherSizeCalculator
from your_library import FlashSelfAttention

# Custom GatherSizeCalculator
class CustomGatherSizeCalculator(GatherSizeCalculator):
    def calculate(self, *args, **kwargs):
        # Example logic
        return kwargs.get("gather_size", None)


core_attention = FlashSelfAttention()
# Use the predefined DynamicGatherSizeCalculator() or a custom CustomGatherSizeCalculator() based on the actual situation.
calculator = DynamicGatherSizeCalculator()
ulysses_attention = UlyssesContextAttention(core_attention, ps.get_context_parallel_group(),
                                            gather_size_calculator=calculator)

```

## Effects

By introducing "Unaligned Ulysses", the system improves its adaptability to different input lengths. This not only resolves the issues encountered by traditional Ulysses when processing dynamic or irregular input sequences, but also maintains good scalability.

> [!NOTE]
>
> - Unaligned Ulysses long-sequence parallelism does not support use on the legacy branch, meaning it cannot be enabled simultaneously with `--use-legacy-models`.
> - Unaligned Ulysses long-sequence parallelism is currently incompatible with Ulysses long-sequence parallelism KV cache optimization. If the launch script sets `--context-parallel-kv-cache-policy` to `full` or `half`, the system will automatically fall back to using the aligned Ulysses long-sequence parallelism.
