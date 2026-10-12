---
id: doc-deepspeedai-deepspeed-fe8bb3d8c7fee19af3ea
title: deepspeedai/DeepSpeed / docs/code-docs/source/initialize.rst
engine: deepspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: deepspeedai/DeepSpeed
commit: bc1ad320a9afb516797577924a9983c6d7cd6793
path: docs/code-docs/source/initialize.rst
raw_sha256: 1b678ed2389539b5d01de058516122f5ac906badf26af3210276355732f3abc2
sources: []
generated_body_sha256: 6af49fd2daf9f116e543a89a476efb5f03c312846b5811bde3661085c244b32c
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/initialize.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/initialize.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Training Setup
==============

.. _deepspeed-args:

Argument Parsing
----------------
DeepSpeed uses the `argparse <https://docs.python.org/3/library/argparse.html>`_ library to
supply commandline configuration to the DeepSpeed runtime. Use ``deepspeed.add_config_arguments()``
to add DeepSpeed's builtin arguments to your application's parser.

.. code-block:: python

    parser = argparse.ArgumentParser(description='My training script.')
    parser.add_argument('--local_rank', type=int, default=-1,
                        help='local rank passed from distributed launcher')
    # Include DeepSpeed configuration arguments
    parser = deepspeed.add_config_arguments(parser)
    cmd_args = parser.parse_args()

.. autofunction:: deepspeed.add_config_arguments


.. _deepspeed-init:

Training Initialization
-----------------------
The entrypoint for all training with DeepSpeed is ``deepspeed.initialize()``. Will initialize distributed backend if it is not initialized already.

Example usage:

.. code-block:: python

    model_engine, optimizer, _, _ = deepspeed.initialize(args=cmd_args,
                                                         model=net,
                                                         model_parameters=net.parameters())

.. autofunction:: deepspeed.initialize

Distributed Initialization
--------------------------
Optional distributed backend initialization separate from ``deepspeed.initialize()``. Useful in scenarios where the user wants to use torch distributed calls before calling ``deepspeed.initialize()``, such as when using model parallelism, pipeline parallelism, or certain data loader scenarios.

.. autofunction:: deepspeed.init_distributed