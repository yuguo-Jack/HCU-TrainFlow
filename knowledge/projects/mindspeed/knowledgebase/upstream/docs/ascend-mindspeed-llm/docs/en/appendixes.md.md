---
id: doc-ascend-mindspeed-llm-f82cdc786c602a875338
title: Ascend/MindSpeed-LLM / docs/en/appendixes.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/en/appendixes.md
raw_sha256: e42a8613abf4c640daed5e5f44bc2aa22bd6cd84a88ac49be7d7ecae7e578bd5
sources: []
generated_body_sha256: 8439c8aa3a69549b3326a3924fa0eca49862f893b8f4d30c1c8a64c8926e1b04
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/appendixes.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/appendixes.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Appendix

## FAQ

Refer to [FAQ](./FAQ.md).

## Join the Ascend Developer Ecosystem

- 🌐 **Community resources**: Visit the [Ascend Open Source Community](https://gitcode.com/ascend) to get the latest model support.
- 📈 **Performance optimization**: Refer to [Profiling Data Collection](./pytorch/tools/profiling.md) to analyze bottlenecks.
- 💡 **Customization needs**: Extend custom models through `model_cfg.json`.

## Linearity

Based on the dense GPT3-175B LLM, we scaled the Model FLOPs Utilization (MFU) and linearity experiments from 128 NPUs to 7,968 NPUs. The experimental data is shown below.

<p align="center"> <img src="./pytorch/figures/readme/linearity&mfu.png" height="490px" width="715px"> </p>

The figure shows the `MFU` values and the overall `linearity` of the cluster at the corresponding scale. You can click the following links to refer to the calculation formulas:

- [MFU calculation formula](https://gitcode.com/Ascend/MindSpeed-LLM/wiki/%E6%9C%AF%E8%AF%AD%E5%AE%9A%E4%B9%89%2F%E5%A4%A7%E6%A8%A1%E5%9E%8B%20MFU%20%E8%AE%A1%E7%AE%97%E5%85%AC%E5%BC%8F.md)
- [Linearity calculation formula](https://gitcode.com/Ascend/MindSpeed-LLM/wiki/%E6%9C%AF%E8%AF%AD%E5%AE%9A%E4%B9%89%2F%E7%BA%BF%E6%80%A7%E5%BA%A6%E5%85%AC%E5%BC%8F.md)
