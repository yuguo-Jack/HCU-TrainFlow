---
id: doc-volcengine-verl-877107d64ddc27983092
title: verl-project/verl / docs/start/ray_debug_tutorial.rst
engine: verl
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: verl-project/verl
commit: 5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d
path: docs/start/ray_debug_tutorial.rst
raw_sha256: a3b8826e3af9661e15f124fc353bd4d78e42a344be4543b028251a4df2c757ca
sources: []
generated_body_sha256: f284272c31232a053de6f23a281c8bb70e6eec737fa43f6e95e9f5a9e56809ee
source_state: current-scan
---

# verl-project/verl / docs/start/ray_debug_tutorial.rst

[Original at fixed commit](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/docs/start/ray_debug_tutorial.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Ray Debug Tutorial
==================

Last updated: 04/23/2025


.. _wuxibin89: https://github.com/wuxibin89

Author: `Ao Shen <https://aoshen524.github.io/>`_.

How to debug?
---------------------


Ray Distributed Debugger VSCode Extension (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Starting with Ray 2.39, Anyscale has introduced the `Ray Distributed Debugger <https://docs.ray.io/en/latest/ray-observability/ray-distributed-debugger.html>`_ VSCode extension. Follow the extension’s installation instructions, then add your cluster using the dashboard URL you obtained earlier.

   .. image:: https://github.com/eric-haibin-lin/verl-community/blob/main/docs/ray/debugger.png?raw=true
      :alt: Ray Distributed Debugger VSCode extension screenshot

2. Prerequisites.

   Ensure the following are installed (see the extension README for more detail):

   - Visual Studio Code  
   - `ray[default]` >= 2.9.1  
   - `debugpy` >= 1.8.0  

   .. image:: https://github.com/eric-haibin-lin/verl-community/blob/main/docs/ray/readme.png?raw=true
      :alt: VSCode with Ray prerequisites

3. Environment Variables.

   To enable post‑mortem debugging, set:

   .. code-block:: bash

      export RAY_DEBUG_POST_MORTEM=1

   .. admonition:: Note
      :class: important

      Be sure to remove any legacy flags before starting Ray:

      - `RAY_DEBUG=legacy`  
      - `--ray-debugger-external`

4. Configuring BreakpointsSet up breakpoint() in your code, and submit job to cluster. Then the extension will show the breakpoint information.


   1. Insert `breakpoint()` calls into your remote functions.  
   2. Submit your job to the cluster.  

   The extension will detect active breakpoints and display them in VSCode.

   **Note:** Breakpoints are only supported inside functions decorated with `@ray.remote`.

5. Launching the Debugger.

   Run your job directly from the command line (do not use a `launch.json`):

   .. code-block:: bash

      python job.py

6. Attaching to a Breakpoint.

 Once the process hits the first `breakpoint()`, click the Ray Distributed Debugger icon in the VSCode sidebar to attach the debugger.

   .. image:: https://github.com/eric-haibin-lin/verl-community/blob/main/docs/ray/launch.png?raw=true
      :alt: Attaching VSCode debugger to Ray process

7. Debugging With Multiple breakpoint().

   For each subsequent task, first disconnect the current debugger session, then click the extension icon again to attach to the next breakpoint.

   .. image:: https://github.com/eric-haibin-lin/verl-community/blob/main/docs/ray/disconnect.png?raw=true
      :alt: Disconnecting and reconnecting the debugger

Legacy Ray Debugger
~~~~~~~~~~~~~~~~~~~
1. Ray has a builtin legacy `debugger <https://docs.ray.io/en/latest/ray-observability/user-guides/debug-apps/ray-debugging.html>`_ that allows you to debug your distributed applications. To enable debugger, start ray cluster with ``RAY_DEBUG=legacy`` and ``--ray-debugger-external``.

.. code-block:: bash

    # start head node
    RAY_DEBUG=legacy ray start --head --dashboard-host=0.0.0.0 --ray-debugger-external
    # start worker node
    RAY_DEBUG=legacy ray start --address='10.124.46.192:6379' --ray-debugger-external

2. Set up breakpoint in your code, and submit job to cluster. Then run ``ray debug`` to wait breakpoint:

.. image:: https://github.com/eric-haibin-lin/verl-community/blob/main/docs/ray/legacy.png?raw=true