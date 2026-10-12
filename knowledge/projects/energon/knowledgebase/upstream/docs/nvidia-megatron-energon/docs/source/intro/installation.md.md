---
id: doc-nvidia-megatron-energon-c7e6479320d4e7f010bc
title: NVIDIA/Megatron-Energon / docs/source/intro/installation.md
engine: energon
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/Megatron-Energon
commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
path: docs/source/intro/installation.md
raw_sha256: 7204daf1d0df9b82d6618232e417270b7522245701e65cb19d0d7d0680c4b8e6
sources: []
generated_body_sha256: 2b66e3ecf37818d2a7bf3b7c250dd0cdcf1e07220cf2f4aaa81ad1265a78e091
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/intro/installation.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/intro/installation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Installation

If you simply want to use this package without modifying it, the best option is to install it 
as a dependency of your project like you would with any other pip package.

## Normal Installation

To install the most recent release version, run

```shell
pip install megatron-energon
```

in your project's Python environment, which could be a virtualenv, or a conda environment.
You can even install it inside a `Dockerfile` to include it in your custom docker container.

If you want to use [remote datasets](../advanced/remote_dataset) or [audio/video decoding](av-decoder), you
need to provide *extras* to the installation command, for example like

```shell
pip install megatron-energon[s3,av_decode]
```

For all available extras, check out the above links and the `pyproject.toml` file.

If you want to install the energon commandline tool, we recommend the following extras:
```shell
uv tool install megatron-energon[all] --torch-backend=cpu
```

## Installation for Development

If you want to manage, debug or modify the code of energon itself, we recommend that you clone this repository
on your disk.

You can then install the package in **editable** mode.
This way, you can use energon and its CLI scripts while still being able to modify the source code.

First, check out the repository locally:
```shell
git clone https://github.com/NVIDIA/Megatron-Energon.git megatron-energon
```

Then install with your favorite tooling:

### Editable installation with uv and just

* `uv` is a fast modern tool that can replace legacy tools like pip, conda and virtualenv.
* `just` is command runner that simplifies common tasks using the `justfile` we provide.

Check out the [official website](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) on how to install `uv`.
On [this page](https://github.com/casey/just?tab=readme-ov-file#packages) you can find out how to install `just`.


Then, to setup a `.venv` and install energon in editable mode:
```shell
cd megatron-energon
just dev-sync
```

The `dev-sync` command will setup a local virtual environment in `.venv` and install all dependencies.
It will also install energon in editable mode for development inside that venv.

Activate the environment
```shell
. .venv/bin/activate
```

Now you can call the `energon` command.

You can also use `just` to do a bunch of other things shown below.
Note that you don't need to activate the venv before running those.

```shell
# Run all unit tests
just test

# Run the code linter and format check
just check

# Build the documentation
just docs

# Show all available commands
just help
```

### Editable installation with pip

First make sure you are in some python environment where you want to set up energon.
Then install in development mode:
```shell
pip install -e ./megatron-energon
```

```{warning}
**We discourage importing the cloned repo without pip install** 
- You will not be able to use the command line tool
- You would have to use hacks to get the package into your `PYTHONPATH`
- You would need to take care of the dependencies yourself. 

Instead, simply install in development mode.
```