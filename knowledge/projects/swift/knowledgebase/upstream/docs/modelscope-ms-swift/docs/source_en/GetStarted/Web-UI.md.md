---
id: doc-modelscope-ms-swift-cae75d48ef5903c01377
title: modelscope/ms-swift / docs/source_en/GetStarted/Web-UI.md
engine: swift
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: modelscope/ms-swift
commit: 22249748429ce7e8516640e35cbe997e572a233a
path: docs/source_en/GetStarted/Web-UI.md
raw_sha256: c5442545cc55df3afc2d5ace55aa7ae4fd3d653aeb579932f8147fd56cbdb7e2
sources: []
generated_body_sha256: 86d2d0c5af3819625cc3c1383e9d65c5bf2c36da0c98a61a2fcd6f3f680ceb8f
source_state: current-scan
---

# modelscope/ms-swift / docs/source_en/GetStarted/Web-UI.md

[Original at fixed commit](https://github.com/modelscope/ms-swift/blob/22249748429ce7e8516640e35cbe997e572a233a/docs/source_en/GetStarted/Web-UI.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Web-UI

Currently, SWIFT supports interface-based training and inference, with parameter support similar to script training. After installing SWIFT, use the following command:

```shell
swift web-ui --lang zh
# or en
swift web-ui --lang en
```

to start the interface for training and inference.

SWIFT web-ui is a high-level wrapper for the command line. In other words, tasks such as training and deployment initiated through the interface will start an independent process in the system via the command line. Pseudo-code is similar to:

```python
import os
os.system('swift sft --model xxx --dataset xxx')
```

This provides several features for the web-ui:

1. Each hyperparameter description in the web-ui is prefixed with `--xxx`, consistent with the [command line arguments](../Instruction/Command-line-parameters.md).
2. The web-ui can concurrently start multiple training/deployment tasks on a multi-GPU machine.
3. After the web-ui service is closed, the background services continue to run. This prevents the training processes from being affected when the web-ui is shut down. If you need to terminate background services, simply **select the corresponding task** and click the kill service button in the `Runtime` tab on the interface.
4. After restarting the web-ui, if you need to display the running services, click `Recover Runtime Tasks` in the `Runtime` tab.
5. The training interface supports displaying runtime logs. After selecting a specific task, manually click `Show Runtime Status`. During training, the runtime status can display training charts, including basic metrics such as training loss, training accuracy, and learning rate. In the human alignment task interface, the charts display key metrics like margin and logps.
6. Training through the web-ui does not support PPO, as the process is more complex. It is recommended to use the [shell script](https://github.com/modelscope/ms-swift/tree/main/examples/train/rlhf/ppo) in the examples directory to run it directly.

If you need to use share mode, please add the `--share true` parameter. **Note:** Do not use this parameter in environments such as dsw or notebooks.

Additionally, ms-swift supports interface inference mode (i.e., Space deployment):

```shell
swift app --model '<model>' --studio_title My-Awesome-Space --stream true
# or
swift app --model '<model>' --adapters '<adapter>' --studio_title My-Awesome-Space --stream true
```
This will launch an application with only the inference page, which will deploy the model upon startup and provide it for subsequent use.