---
id: doc-pytorch-torchtitan-35f8d6de329fd874fb84
title: pytorch/torchtitan / docs/benchmarks/README.md
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
path: docs/benchmarks/README.md
raw_sha256: f29fd47431dbc380c86062b9cd798339315a64f70c1d85ee183acc381efdd689
sources: []
generated_body_sha256: a5a85621491b2071e159d46a62e097ced5bb03eaf31da3a5a417ff6c74697082
source_state: current-scan
---

# pytorch/torchtitan / docs/benchmarks/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/docs/benchmarks/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

We welcome the community to submit reproducible benchmarking results.

## Submission Guidelines

A submission should be a file / files including the following information

1. Entity, which could be your name, GitHub username, company, university, team, etc.
2. The model or theme of benchmarking, e.g. Llama 3.1, Async TP.
3. The hardware setup, including the types of GPUs, interconnections, etc.
4. The actual performance report with training configs, e.g. via
   - Python config files / commandline arguments
   - complete resolved configs, printed by passing `--print-config` to
     `run_train.sh` (preferred because defaults can change over time)
5. The versions and date/time of `torchtitan`, `torch`, `torchao`, or any relevant dependencies.
6. Other notes which could help reproduce the results.

The name of the file should follow the format of
```
[model/theme]_[hardware]_[date/time]_[entity].md
```
For example, `llama3.1_h100_202412_pytorch.md`, `asynctp_256xh100_20250613_alice+bob.md`.

An example can be found at [llama3_h100_202412_torchtitan.md](./llama3_h100_202412_torchtitan.md).
