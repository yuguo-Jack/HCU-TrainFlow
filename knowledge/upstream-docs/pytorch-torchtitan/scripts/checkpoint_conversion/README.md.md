---
id: doc-pytorch-torchtitan-6e1ca8ce3eb990390d52
title: pytorch/torchtitan / scripts/checkpoint_conversion/README.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
path: scripts/checkpoint_conversion/README.md
raw_sha256: adc64d98cfd2e41f3dc030014d8ed400a9e8e0373f231ca40d054ca1e3e97ac7
sources: []
generated_body_sha256: 24c46f115eed3c9f95fbfba59f5b76842044d063fff184e873b3a6b0705738fc
source_state: current-scan
---

# pytorch/torchtitan / scripts/checkpoint_conversion/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/scripts/checkpoint_conversion/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Testing Checkpoint Conversion for Correctness

When converting checkpoints between file types or model definitions, we need to ensure that the converted checkpoints are correct, i.e. their model definition remains the same, which includes that the converted checkpoint's weights will give the same outputs when loaded in the new intended program context.

This guide provides a general framework on how to test your conversion script for correctness. The example that we will use here is bidirectional conversion between HuggingFace and `torchtitan`.

## Methods

### Sanity Check (Greedy Decode)
A quick way to sanity check if your conversion is correct is to perform greedy decoding inference on both the initial and converted checkpoints and confirm that they are the same. This method doesn't guarantee correctness but will very likely result in a fast **true negative** if the model definitions are not the same. The vLLM-based [`generate.py`](/torchtitan/rl/generate.py) is largely model-agnostic and can serve this purpose; pass `--temperature 0` for greedy decode. It has been tested on some but not all models. The methodology holds the same for a model with no inference entry point of its own.

Note that your model definition needs to match your conversion script. For example, if converting from `torchtitan` to HuggingFace, be sure to include the correct `config.json` file that matches the `torchtitan` model architecture. Providing an incorrect `config.json` when loading the model with HuggingFace `transformers` will result in incorrect generations despite a correct weight conversion.

### Comprehensive Check (KL Divergence)
In our `./scripts/checkpoint_conversion/numerical_tests_example.py` this will be performing forward on DCP checkpoints loaded in `torchtitan` and safetensors checkpoints loaded in HuggingFace `AutoModelForCausalLM`. This script tests the HuggingFace -> `torchtitan` direction, as loading a HuggingFace checkpoint requires both
- converting the instantiated `torchtitan` state dict `to_hf` so that safetensors weights can be loaded into it, and
- converting the HF version of state dict back to torchtitan using `from_hf`.

To convert Llama 3 between HuggingFace and `torchtitan` we had to perform a permutation on several of the attention matrices to account for difference between HuggingFace and native Llama RoPE implementations. To demonstrate how a KL divergence test can reveal subtle inaccuracies such as this, we additionally compare the KL divergence between the original and converted model with and without the permutation. The results are as follows:
```
$ python ./scripts/checkpoint_conversion/numerical_tests_example.py
Average loss of test from_hf is -1.45365707318601e-13
Average loss of test from_hf_no_perm is 5.368335223465692e-06
```
