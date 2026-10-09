---
id: hiyouga-llama-factory-source-map
title: hiyouga/LlamaFactory source directory map
kind: source-map
engine: llamafactory
review_level: inventory-only
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
sources: []
generated_body_sha256: 6585fc666f0f3a5ed8be306fede302498c3c75cb75f12b283accd7abff6877ff
---

# hiyouga/LlamaFactory: fixed source directory map

Commit `ce9dc9e072f80fa3abe0989d4ab90da25f083438` · ref `main`. Full paths are discoverable; listing a file does not imply its contents were read.

Use `wiki-code hiyouga/LlamaFactory ce9dc9e072f80fa3abe0989d4ab90da25f083438 PATH` to inspect exact files, then follow callers/tests. A gitlink entry pins a child SHA, not its latest branch.

## .ai

- [.ai/CLAUDE.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.ai/CLAUDE.md) · blob `e211a26f3740b4b24f42284a561b719f40d5eb8c`

## .claude

- [.claude/skills/llamafactory-sft/SKILL.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.claude/skills/llamafactory-sft/SKILL.md) · blob `d59c968bae7bace4e6fcca72c7ed3377790d303c`
- [.claude/skills/llamafactory-v1-docs/SKILL.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.claude/skills/llamafactory-v1-docs/SKILL.md) · blob `64d802a8645379b3b804da4b241e3123f6bb5259`

## .dockerignore

- [.dockerignore](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.dockerignore) · blob `a07ec860d9e8a49793fb478c405607bbdb3bf80e`

## .env.local

- [.env.local](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.env.local) · blob `f5eeeb65e032c5b33037bc20f016f91071976497`

## .gitattributes

- [.gitattributes](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.gitattributes) · blob `dfe0770424b2a19faf507a501ebfc23be8f54e7b`

## .github

- [.github/CODE_OF_CONDUCT.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/CODE_OF_CONDUCT.md) · blob `c2035cea5425b8de8e88a563214d05dfd415352a`
- [.github/CONTRIBUTING.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/CONTRIBUTING.md) · blob `507d666a23fc35f51b931e4f032c6d4b07872a45`
- [.github/ISSUE_TEMPLATE/1-bug-report.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/ISSUE_TEMPLATE/1-bug-report.yml) · blob `a08596faa5b3be2545412d372f7bdeadca95afb4`
- [.github/ISSUE_TEMPLATE/2-feature-request.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/ISSUE_TEMPLATE/2-feature-request.yml) · blob `5d72271ebc8db3d10bf7e9c6af209e857566bde6`
- [.github/ISSUE_TEMPLATE/config.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/ISSUE_TEMPLATE/config.yml) · blob `1a7719634963d9d78bfa5155b51c5a82311084e4`
- [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/PULL_REQUEST_TEMPLATE.md) · blob `d23d6be3cfb8e2db888b19becedf075c7aa527be`
- [.github/SECURITY.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/SECURITY.md) · blob `d34728ebfeb22e9fda2f3e76ff133014b648ab3c`
- [.github/copilot-instructions.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/copilot-instructions.md) · blob `4a1ba22e24125d8eb1c1c1a868884951b905a9ef`
- [.github/instructions-v0.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/instructions-v0.md) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [.github/instructions-v1.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/instructions-v1.md) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [.github/workflows/docker.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/workflows/docker.yml) · blob `84bfddbf51b1fa427d2524e233c2ef291183a60c`
- [.github/workflows/docker_npu.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/workflows/docker_npu.yml) · blob `7cafe115d56803ee3ec3b15573cb529069e025c4`
- [.github/workflows/docs.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/workflows/docs.yml) · blob `64e7f336a86f724ccab88862082141e67255e127`
- [.github/workflows/label_issue.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/workflows/label_issue.yml) · blob `3d0424c77479d1a18a39f78240491461d50f3d22`
- [.github/workflows/publish.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/workflows/publish.yml) · blob `41cbff65544e4922cfe6a770005467a005d59aa1`
- [.github/workflows/tests.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/workflows/tests.yml) · blob `2dcf2614155279b4ac31375736ab3478c2c9ffe5`
- [.github/workflows/tests_cuda.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/workflows/tests_cuda.yml) · blob `f533b01c5bb88bc2a8a193c9db71ed4dfdaad8fa`
- [.github/workflows/tests_npu.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.github/workflows/tests_npu.yml) · blob `3679eba463e7075cd76b6a9926ba213bdc13ecd1`

## .gitignore

- [.gitignore](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.gitignore) · blob `b9013087f67ba0c9c4f66c75321e5c8bccd30f01`

## .pre-commit-config.yaml

- [.pre-commit-config.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/.pre-commit-config.yaml) · blob `f76f89ddfd5fbd8344e5af4b2f1dc68d01ea8c50`

## CITATION.cff

- [CITATION.cff](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/CITATION.cff) · blob `01b4c9fd28aed295d50c71a7a3ed2e97a69434d4`

## CLAUDE.md

- [CLAUDE.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/CLAUDE.md) · blob `1e135c798b0d4ad660df061cacb720a9ab832f05`

## LICENSE

- [LICENSE](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/LICENSE) · blob `b09cd7856d58590578ee1a4f3ad45d1310a97f87`

## MANIFEST.in

- [MANIFEST.in](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/MANIFEST.in) · blob `1aba38f67a2211cf5b09466d7b411206cb7223bf`

## Makefile

- [Makefile](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/Makefile) · blob `c46720f011836abbfbe45a8df8c413bd5e44806c`

## README.md

- [README.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/README.md) · blob `6de8a1600463068d1da993efee436c4cb26ec6b6`

## README_zh.md

- [README_zh.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/README_zh.md) · blob `e57b6be6c265c44e8105aebb3df975cb427f01b4`

## assets

- [assets/logo.png](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/assets/logo.png) · blob `5fb3dd569342ca3cd30a582fd664145bd88b360c`
- [assets/sponsors/serpapi.svg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/assets/sponsors/serpapi.svg) · blob `79bdf4001382b368148e9c3b611507bb7c0494f9`
- [assets/sponsors/warp.jpg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/assets/sponsors/warp.jpg) · blob `64bc01be277848d0d4c1f8cb3588340c897e2026`
- [assets/thirdparty/colab.svg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/assets/thirdparty/colab.svg) · blob `e5830d5332975c03acc2a9715bd880097083e91d`
- [assets/thirdparty/discord.svg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/assets/thirdparty/discord.svg) · blob `b94f16cca3c6db4545f5d541390e66ddbf99b5a0`
- [assets/thirdparty/dsw.svg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/assets/thirdparty/dsw.svg) · blob `a0df870cc11681ba3cd0b813146238d5b8f5d9b7`
- [assets/thirdparty/lab4ai.svg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/assets/thirdparty/lab4ai.svg) · blob `ad83c1bbeb622074bea3beb2c1353baa7e82dff8`
- [assets/thirdparty/online.svg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/assets/thirdparty/online.svg) · blob `e9051e3048ad1a8dc28d6e5f322854b8ff883672`

## data

- [data/README.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/README.md) · blob `e43e0eed0b48f6ed0054382346311550a2a1a927`
- [data/README_zh.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/README_zh.md) · blob `56c1f42483b72a45b19d027869bb347d5d27e45c`
- [data/alpaca_en_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/alpaca_en_demo.json) · blob `b645c416b5204f25fab66f839a44203a9ad5a2a4`
- [data/alpaca_zh_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/alpaca_zh_demo.json) · blob `4501a26f599373c68a8724ee21a4644f58550ca1`
- [data/c4_demo.jsonl](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/c4_demo.jsonl) · blob `36cbbad705bdf3396bfd4f9e661823de224feedd`
- [data/dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/dataset_info.json) · blob `4d105699026995d1455f6ecb44e2702bef97a7c3`
- [data/dpo_en_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/dpo_en_demo.json) · blob `82769a63b98ef967480ac515bd05602a9808bfca`
- [data/dpo_zh_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/dpo_zh_demo.json) · blob `5a798a3804be41e9f42090e6dc7be862d6848220`
- [data/glaive_toolcall_en_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/glaive_toolcall_en_demo.json) · blob `1b3e8e3e058e5a91a689a268eaa6254c63c1d6a4`
- [data/glaive_toolcall_zh_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/glaive_toolcall_zh_demo.json) · blob `a6caa971689e339e7e2b25165355a665ec900c47`
- [data/identity.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/identity.json) · blob `6210846ced4ad7b8276981ddf7273a0e4373a1f3`
- [data/kto_en_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/kto_en_demo.json) · blob `ce8a408002d2ef8561d50d19c305f10b55dd8567`
- [data/mllm_audio_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_audio_demo.json) · blob `30a50b7d479026f8011499b35263e241eba50aa7`
- [data/mllm_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo.json) · blob `bd05b7f59e6364d91d35c0da5617d016fff752b6`
- [data/mllm_demo_data/1.jpg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/1.jpg) · blob `a29762eda5e2e31e178768b14b5d5265d53331e6`
- [data/mllm_demo_data/1.mp3](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/1.mp3) · blob `150e1080f2e56f4a650e48510d3795e56c012be9`
- [data/mllm_demo_data/1.mp4](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/1.mp4) · blob `f3abd568cb7c0efe15e1bf0a2243fc58cb2b5753`
- [data/mllm_demo_data/2.avi](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/2.avi) · blob `bdb736c25692c950e28b55c98aee14cc0720f62a`
- [data/mllm_demo_data/2.jpg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/2.jpg) · blob `1df98231a1c1009f5baccbdcd5e5432c443c93b3`
- [data/mllm_demo_data/2.wav](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/2.wav) · blob `8c3045c624a13eae406a2bcb6a64fd06c04cc8f2`
- [data/mllm_demo_data/3.flac](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/3.flac) · blob `3b0c844f12abe55b7988eeb62f8553384b0d764f`
- [data/mllm_demo_data/3.jpg](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/3.jpg) · blob `72bc7315cc83be0fadea2d236d3d293dde7d5652`
- [data/mllm_demo_data/3.mp4](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/3.mp4) · blob `48ce6f6622788c9c5829c5efd179c25d098f4500`
- [data/mllm_demo_data/4.mp3](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/4.mp3) · blob `17a8a8455b86bf8bd88085dfddf2e625c3030b15`
- [data/mllm_demo_data/4.mp4](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_demo_data/4.mp4) · blob `fdf859dd76104b93786205d28bc6ac18077ca301`
- [data/mllm_video_audio_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_video_audio_demo.json) · blob `ea27fc67d9c2dfd4cd7fb0e4e11bc352855f66aa`
- [data/mllm_video_demo.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/mllm_video_demo.json) · blob `2aa7bb68961179f15e9ed1ac3de5b028f18f3530`
- [data/reason_tool_use_demo_50.jsonl](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/reason_tool_use_demo_50.jsonl) · blob `dba54f33e0d7b6fc50abfa2c113a3f4ac6f905f6`
- [data/v1_dpo_demo.jsonl](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/v1_dpo_demo.jsonl) · blob `8b8adeb4dd74169be8c9cef9dee37ff52be875ac`
- [data/v1_dpo_demo.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/v1_dpo_demo.yaml) · blob `2edca22f8641064d15f241bb5fa8827017541ac2`
- [data/v1_multimodal_demo.jsonl](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/v1_multimodal_demo.jsonl) · blob `d6cd0b1bb7f25e4d2b42edfb13767d892e01afb6`
- [data/v1_multimodal_demo.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/v1_multimodal_demo.yaml) · blob `7ecb0a45433b0829bbfab357d3d037b728ae5e2c`
- [data/v1_sft_demo.jsonl](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/v1_sft_demo.jsonl) · blob `6ad8b003897d55fcd543dad03296f95804941898`
- [data/v1_sft_demo.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/v1_sft_demo.yaml) · blob `8fed3b1dc2088f2d08b3e2f4a5d015aaa6d6633b`
- [data/wiki_demo.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/data/wiki_demo.txt) · blob `0959fce32dbcb037fb825c3b373fa89c0c78321a`

## docker

- [docker/docker-cuda/Dockerfile](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-cuda/Dockerfile) · blob `f33d14e33722dfb222b273ee5518fbcabc429662`
- [docker/docker-cuda/Dockerfile.base](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-cuda/Dockerfile.base) · blob `542eb8dcced27998875cbd5dc5ee08b61e776db2`
- [docker/docker-cuda/Dockerfile.mbridge](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-cuda/Dockerfile.mbridge) · blob `c6757c769a4d71a96d79f51cb4a3afa8bf877de4`
- [docker/docker-cuda/Dockerfile.megatron](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-cuda/Dockerfile.megatron) · blob `6e6e1cb297bcb442cab6f19185b8725843d6c5d9`
- [docker/docker-cuda/README.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-cuda/README.md) · blob `c1a399a48851c4600d63c17d9425109e5a406fdf`
- [docker/docker-cuda/docker-compose.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-cuda/docker-compose.yml) · blob `eb4250ce61f09d6318968cf30f86ca9f28529773`
- [docker/docker-npu/Dockerfile](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-npu/Dockerfile) · blob `28fabc0e2e9dcc2560d88c87fc58fa4bc06cd8b1`
- [docker/docker-npu/OVERVIEW.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-npu/OVERVIEW.md) · blob `68dba74217d41ba89716adf3e704df11d349f160`
- [docker/docker-npu/OVERVIEW.zh.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-npu/OVERVIEW.zh.md) · blob `f4d47fb79e7052a9413cf2914113d865b855e75e`
- [docker/docker-npu/docker-compose.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-npu/docker-compose.yml) · blob `61fe439f49cf869c78565afd73c09978aab31160`
- [docker/docker-npu/supported_tags.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-npu/supported_tags.md) · blob `9171e5a84e3d3c0520c9116c14e5c437da2ab518`
- [docker/docker-rocm/Dockerfile](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-rocm/Dockerfile) · blob `636099d53d73e53120bab1489d1f6155aa7141c8`
- [docker/docker-rocm/docker-compose.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-rocm/docker-compose.yml) · blob `7e6c83bfb511b91da8f389c7694a65df80be55e7`
- [docker/docker-xpu/Dockerfile](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-xpu/Dockerfile) · blob `c5010f3dd49c8ae5d12b3749b66aa6aa001ba8ce`
- [docker/docker-xpu/README.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-xpu/README.md) · blob `4f3d5884595c3d513ba0ed185d007ec92a50540e`
- [docker/docker-xpu/docker-compose.yml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docker/docker-xpu/docker-compose.yml) · blob `7bf7a4bff91e9a306c46ddfac85ccf49d71b565d`

## docs

- [docs/Makefile](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/Makefile) · blob `6db2f2aab548352a77665a760b3f06f8a549b9f0`
- [docs/_static/css/lang-switcher.css](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/_static/css/lang-switcher.css) · blob `aaf2df88f7a9b3b8c4e0ba850fea98b56c920525`
- [docs/_static/css/tables.css](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/_static/css/tables.css) · blob `e23417ed3c89d2f67401b4ecac6ca00049f17d27`
- [docs/_static/js/switcher.js](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/_static/js/switcher.js) · blob `6f5dc690a16dadeafc38dee4c2460e7601030912`
- [docs/conf.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/conf.py) · blob `0504612571db9f847be44bc4bfa969f00c40af15`
- [docs/en/advanced/custom-kernels/custom-kernels.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/custom-kernels/custom-kernels.md) · blob `d932c9910333ce276e9fd419892293527cbdc820`
- [docs/en/advanced/custom-kernels/fused-operators.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/custom-kernels/fused-operators.md) · blob `45b4b20a5a6111a43996639eaef85c67fc7f40e1`
- [docs/en/advanced/custom-kernels/triton.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/custom-kernels/triton.md) · blob `43a4bf7898545effb8b2e930d17edecc73890c58`
- [docs/en/advanced/distributed/deepspeed.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/distributed/deepspeed.md) · blob `0595dedcb3b0da515daa67142c98662de9de6139`
- [docs/en/advanced/distributed/fsdp.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/distributed/fsdp.md) · blob `37e146745c87769f53f824acec39f9f1b8a8962d`
- [docs/en/advanced/distributed/fsdpturbo-ep-efsdp.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/distributed/fsdpturbo-ep-efsdp.md) · blob `c0c2f6f928b06fe4a122957a7c5ee1eb1ae17bb3`
- [docs/en/advanced/distributed/parallel-dp-tp-ep-sp-cp.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/distributed/parallel-dp-tp-ep-sp-cp.md) · blob `b645ae4897d816980ff524eea892aa5f270d1c22`
- [docs/en/advanced/ktransformers.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/ktransformers.md) · blob `89963014b4c7805fca2ed8ccda56400ddad20bcf`
- [docs/en/advanced/lora-and-quantization/lora.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/lora-and-quantization/lora.md) · blob `2948dd87d9c59de1fe1a4040b57441cd1d49e1e4`
- [docs/en/advanced/lora-and-quantization/quantization.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/advanced/lora-and-quantization/quantization.md) · blob `13268223f52f5bbc1bd31a80262ad2eec1e1bd95`
- [docs/en/conf.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/conf.py) · blob `b53f1840ab08ebb435e6844cf19ae21793594590`
- [docs/en/data-preparation/data-processing.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/data-preparation/data-processing.md) · blob `b43ea8f3e25be0d498ecc670dc58616fa3a8ccdb`
- [docs/en/dev-guide/core/data-engine.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/dev-guide/core/data-engine.md) · blob `1fb42b900982113e780e478142bb52ab4331c90f`
- [docs/en/dev-guide/core/model-engine.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/dev-guide/core/model-engine.md) · blob `763ad1645b0ac92e6c044f7677911ba8b009d9bf`
- [docs/en/dev-guide/core/trainer.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/dev-guide/core/trainer.md) · blob `218a1fe5d4a7ab58d18233a7910d361f8cc6b524`
- [docs/en/dev-guide/plugins/data-plugins.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/dev-guide/plugins/data-plugins.md) · blob `a5a5061787a99ee35921954490140c0350430d6a`
- [docs/en/dev-guide/plugins/model-plugins/initialization.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/dev-guide/plugins/model-plugins/initialization.md) · blob `c7d4730ce4ba9de7937cd0c5b2a27ef4072057da`
- [docs/en/dev-guide/plugins/model-plugins/kernels.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/dev-guide/plugins/model-plugins/kernels.md) · blob `9ddc7789e2e702763e4b02e8a872a46c1debb355`
- [docs/en/dev-guide/plugins/model-plugins/rendering.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/dev-guide/plugins/model-plugins/rendering.md) · blob `90f4ddc16c9cc1fafb0cc3c7e9f8231b8bf689a7`
- [docs/en/getting-started.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/getting-started.md) · blob `78a08e17231ff555ce295b62496eff2803107e9e`
- [docs/en/hyperparameters/data-argument.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/hyperparameters/data-argument.md) · blob `af45859493bdfa342e37da8849a9355532f05072`
- [docs/en/hyperparameters/model-argument.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/hyperparameters/model-argument.md) · blob `413cb2258d61018d4a3bdc3f98766efb061bd8cd`
- [docs/en/hyperparameters/sample-argument.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/hyperparameters/sample-argument.md) · blob `57bbb2857b5ab6bdcee6ad6ffe68a3d77340d437`
- [docs/en/hyperparameters/training-argument.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/hyperparameters/training-argument.md) · blob `2a9bea5d8512672722ab2d1d6c85d85e6d8d1a41`
- [docs/en/index.rst](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/index.rst) · blob `4d845be52e1b9a594fe9ae6f649f7094fae20961`
- [docs/en/inference/deploy.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/inference/deploy.md) · blob `e88e8c5c59fdaeefbf10972df79a4120b4ff7bdc`
- [docs/en/installation.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/installation.md) · blob `e919e7da3106fe2a95270760187306bc89e262bc`
- [docs/en/llamaboard-web-ui.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/llamaboard-web-ui.md) · blob `dfeba709b787ec8a42172a8ebdf5737718e044b2`
- [docs/en/training/dpo.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/training/dpo.md) · blob `e7efc4d9078b5497df2b6dca80d8609d6b104355`
- [docs/en/training/sft.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/en/training/sft.md) · blob `a8ade89be25af20006852cd1d6610a44de2d94be`
- [docs/make.bat](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/make.bat) · blob `f97f4e30b27f2c636027c1872a1ce2c11a9fad34`
- [docs/requirements.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/requirements.txt) · blob `c7d85460d0c67412732cc60d6273f971d3208093`
- [docs/zh/conf.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/conf.py) · blob `4af1c7be5fadc8a312d9f248dbf394c2b6adf22e`
- [docs/zh/configuration/data.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/configuration/data.md) · blob `76dc5bab1aa24f4af51175db0014fbc7c79f7450`
- [docs/zh/configuration/index.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/configuration/index.md) · blob `d6edeac30ad5120660edbd55a0a7d3219251ef5b`
- [docs/zh/configuration/inference.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/configuration/inference.md) · blob `5fe1c4ee9d5c1ceab48eafdea68e6ee33a453cef`
- [docs/zh/configuration/model.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/configuration/model.md) · blob `4474cf39b9aa44563c937ff447988f1b4d6064a9`
- [docs/zh/configuration/training.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/configuration/training.md) · blob `214290be1fc951574e8b78c6f5776a589dbf4077`
- [docs/zh/developer-guide/architecture_overview.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/architecture_overview.md) · blob `3e73bef4fd83bdcb1658e12ca227ad9f6f67ff46`
- [docs/zh/developer-guide/baseplugin_mechanism.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/baseplugin_mechanism.md) · blob `94dbb1157865a42ef6063c249bfeb534e00ff3ce`
- [docs/zh/developer-guide/core/base_sampler.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/core/base_sampler.md) · blob `63440561ba2e772d7fb01cc5aac0c24627bdaba2`
- [docs/zh/developer-guide/core/base_trainer.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/core/base_trainer.md) · blob `f101983c27e29e5f936ab07ce87f905037c3edf1`
- [docs/zh/developer-guide/core/batch_generator.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/core/batch_generator.md) · blob `f138b5db3165f6493097b02e1b7fd339cade64c5`
- [docs/zh/developer-guide/core/callback.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/core/callback.md) · blob `c54fc5ef32b85e259831ee085082b0bb93fc7db4`
- [docs/zh/developer-guide/core/data_engine.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/core/data_engine.md) · blob `135b97365ba290ea3bf98c499a7912293bdb9df5`
- [docs/zh/developer-guide/core/index.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/core/index.md) · blob `89869aed3ff8c31c8f323d6b9858f8254efbff0b`
- [docs/zh/developer-guide/core/model_engine.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/core/model_engine.md) · blob `9880bd546c8c4af7479480d81646eaf536b1507b`
- [docs/zh/developer-guide/core/renderer.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/core/renderer.md) · blob `7ce63db7e7c396d7de87b70bae37f130b14bdfb9`
- [docs/zh/developer-guide/index.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/index.md) · blob `fedc86e5f1d3bfcac985a0e006abb8e36ab2fbd6`
- [docs/zh/developer-guide/plugins/data_plugins.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/plugins/data_plugins.md) · blob `cf1c88cb5d7ad434098f71c9eef43d04e59ffff2`
- [docs/zh/developer-guide/plugins/index.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/plugins/index.md) · blob `7e4b4bf6d39de02c0ef65b1971174df068fd1134`
- [docs/zh/developer-guide/plugins/kernel-acceleration/overview.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/plugins/kernel-acceleration/overview.md) · blob `150c5cb76e5b32e2868681e33742ef5e4e26d8a1`
- [docs/zh/developer-guide/plugins/model_plugins.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/plugins/model_plugins.md) · blob `ca9cdb0350e23d5e9c4c96321e54ef1975b146ce`
- [docs/zh/developer-guide/plugins/trainer_plugins.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/developer-guide/plugins/trainer_plugins.md) · blob `556c26ff612455afe6656406ae8214ae56aa9cfd`
- [docs/zh/feature-guide/batching.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/batching.md) · blob `26785ababc199e2c949ae6ffc0bb4e4d40e5360a`
- [docs/zh/feature-guide/data_preparation.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/data_preparation.md) · blob `8861b02728c35a1af32ec1c59c1c5009175076fa`
- [docs/zh/feature-guide/distributed_training.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/distributed_training.md) · blob `ae41fc269a8e5555495737a788c24c5b1783509d`
- [docs/zh/feature-guide/dpo.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/dpo.md) · blob `2729b517e6272a155e018a68f08727fd3b62a479`
- [docs/zh/feature-guide/index.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/index.md) · blob `3c6270f8583045bdf9c4ea57aa30b9611fb809ad`
- [docs/zh/feature-guide/inference.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/inference.md) · blob `4eace2e29d72b3b974ba3576dee5d4ab04893f18`
- [docs/zh/feature-guide/kernel_acceleration.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/kernel_acceleration.md) · blob `15471f698c0cc3912eaf54efc42ef706fce9ab00`
- [docs/zh/feature-guide/model_export.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/model_export.md) · blob `557102e6204884fb09c00e874b680ea9fe9771b2`
- [docs/zh/feature-guide/model_saving.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/model_saving.md) · blob `66536d32d69b2b3cafa0d5c559c1db37cec3d1c1`
- [docs/zh/feature-guide/optimizer.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/optimizer.md) · blob `4d8c7f9a0dd3b0519529449a43a93a6ca78fe87d`
- [docs/zh/feature-guide/rm.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/rm.md) · blob `b35bd52775520060b71bf27a1491a332bb534bb3`
- [docs/zh/feature-guide/sft.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/feature-guide/sft.md) · blob `c5fa09542202bce63becc343aa2a32f13a7498bf`
- [docs/zh/index.rst](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/index.rst) · blob `8e677bc406aa2dd8619286f4fae42bdb4eecf3ae`
- [docs/zh/multi-backend/npu/index.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/multi-backend/npu/index.md) · blob `47b95d1737e3b2774f28b01481c6f9634e8c1aab`
- [docs/zh/quick_start.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/docs/zh/quick_start.md) · blob `27ae9ce861ca5f7a37c35cf6a0178d2ae4ba9644`

## examples

- [examples/README.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/README.md) · blob `1d79d574c61379db55041b147250098952b2a600`
- [examples/README_zh.md](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/README_zh.md) · blob `324a52be3975aaa16e53b14f9b47f1727fe3b761`
- [examples/accelerate/fsdp2_config.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/accelerate/fsdp2_config.yaml) · blob `34348fdf2e123396a91893318ecf42d21bd202f3`
- [examples/accelerate/fsdp2_config_qwen35.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/accelerate/fsdp2_config_qwen35.yaml) · blob `edc8b8ffbd424dfaf7398679a89f664bb43d8dae`
- [examples/accelerate/fsdp2_config_qwen35_moe.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/accelerate/fsdp2_config_qwen35_moe.yaml) · blob `ae335f11aba8a8e5f8f83a193d8f461486969a5d`
- [examples/accelerate/fsdp_config.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/accelerate/fsdp_config.yaml) · blob `09d2f5d733a6bdd3cab709cfbcac1705cd57a6a0`
- [examples/accelerate/fsdp_config_multiple_nodes.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/accelerate/fsdp_config_multiple_nodes.yaml) · blob `587358e5d777e1217192ae0ec5fe7815d33ef2a4`
- [examples/accelerate/fsdp_config_offload.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/accelerate/fsdp_config_offload.yaml) · blob `a55e652eaf8519a8ce2c9fa8d1afdba104cbf88f`
- [examples/ascend/qwen3_5_full_sft_fsdp2.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ascend/qwen3_5_full_sft_fsdp2.yaml) · blob `915b70f812b23580bea062e1a51ab3b22471bd63`
- [examples/ascend/qwen3_5moe_lora_sft_fsdp2.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ascend/qwen3_5moe_lora_sft_fsdp2.yaml) · blob `738ee06b25fe39c422d3b1f56914a690dadcaac7`
- [examples/ascend/qwen3_full_sft_fsdp2.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ascend/qwen3_full_sft_fsdp2.yaml) · blob `04351ddd6b42086b7732ed82ea2915339f59d436`
- [examples/ascend/qwen3moe_full_sft_fsdp.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ascend/qwen3moe_full_sft_fsdp.yaml) · blob `659918b105c7c33900dd81fadd2ae4579f2573c1`
- [examples/ascend/qwen3vlmoe_full_sft_fsdp2.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ascend/qwen3vlmoe_full_sft_fsdp2.yaml) · blob `d841804d648fcc6edffa6e4a0ccc8dbd1b761247`
- [examples/ascend/qwen3vlmoe_lora_sft_fsdp.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ascend/qwen3vlmoe_lora_sft_fsdp.yaml) · blob `b689fa02c00c98ab7a9314bd26c207cbc5ab95e1`
- [examples/deepspeed/ds_z0_config.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/deepspeed/ds_z0_config.json) · blob `8ac991813e77b1c031ae9829e48e429f5d83c088`
- [examples/deepspeed/ds_z2_autotp_config.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/deepspeed/ds_z2_autotp_config.json) · blob `7090d47b328bba1dc8430de1f9790c26f3e9ff09`
- [examples/deepspeed/ds_z2_config.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/deepspeed/ds_z2_config.json) · blob `c4177e5e05e3f26ffe8ddeacd9f0fa79d5e86315`
- [examples/deepspeed/ds_z2_offload_config.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/deepspeed/ds_z2_offload_config.json) · blob `7550472b3f71542b82f0243d9309d5d6a6e30095`
- [examples/deepspeed/ds_z3_config.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/deepspeed/ds_z3_config.json) · blob `46584a769c753b4f2fd41347f0a4266127481510`
- [examples/deepspeed/ds_z3_fp8_config.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/deepspeed/ds_z3_fp8_config.json) · blob `14eb06708bb33ea71f141c054a4f26f18f7e7da4`
- [examples/deepspeed/ds_z3_offload_config.json](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/deepspeed/ds_z3_offload_config.json) · blob `0fabebb93b8d34bebffde1079fcf89c51d42ac55`
- [examples/extras/adam_mini/qwen2_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/adam_mini/qwen2_full_sft.yaml) · blob `79df9a737581c3206e9c5b85be835294bb63b36f`
- [examples/extras/apollo/llama3_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/apollo/llama3_full_sft.yaml) · blob `d9fb6c2002df08018b7110437471797bdfef777e`
- [examples/extras/asft/llama2_full_asft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/asft/llama2_full_asft.yaml) · blob `fb1d7f128651bd210566a0c607ada33c15f34a33`
- [examples/extras/asft/qwen2_full_asft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/asft/qwen2_full_asft.yaml) · blob `76fd52449114aecffda72557dbd25aac19d5f692`
- [examples/extras/badam/llama3_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/badam/llama3_full_sft.yaml) · blob `7ce332303c744486d8f6426aa65839296f3bdbd2`
- [examples/extras/dft/qwen2_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/dft/qwen2_full_sft.yaml) · blob `865cc85635544161e167833435186e62c2f076f6`
- [examples/extras/eaft/qwen25_05b_eaft_full.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/eaft/qwen25_05b_eaft_full.yaml) · blob `72c0b0184af222c21290ce7cbc1a2334890bb516`
- [examples/extras/fp8/llama3_fp8_deepspeed_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/fp8/llama3_fp8_deepspeed_sft.yaml) · blob `555e884d3066fb1ab517c6737635aed0ae4793e6`
- [examples/extras/fp8/llama3_fp8_fsdp_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/fp8/llama3_fp8_fsdp_sft.yaml) · blob `5983c3e85861d7ede85fc4dc9381e327f336c68e`
- [examples/extras/fsdp_qlora/llama3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/fsdp_qlora/llama3_lora_sft.yaml) · blob `1a8d9743035e3c5848ba943eb0fc47eb7b1da6be`
- [examples/extras/fsdp_qlora/train.sh](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/fsdp_qlora/train.sh) · blob `fac8cdee8781750d96e29999ab8a6b9b4f1bc322`
- [examples/extras/galore/llama3_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/galore/llama3_full_sft.yaml) · blob `99730932ae5150e1eacdd2c20ad9b9a7b0e51263`
- [examples/extras/llama_pro/expand.sh](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/llama_pro/expand.sh) · blob `9f3c013cf2479464637d90e020ca76aea8558b05`
- [examples/extras/llama_pro/llama3_freeze_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/llama_pro/llama3_freeze_sft.yaml) · blob `6c5efb8b27793a5ee1ec922632af389361e9f501`
- [examples/extras/loraplus/llama3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/loraplus/llama3_lora_sft.yaml) · blob `574b4870c586e4cb70d5f350320d81a889fb7340`
- [examples/extras/mod/llama3_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/mod/llama3_full_sft.yaml) · blob `ed784e749da9933961b39ab150ef625a4a89d7e1`
- [examples/extras/multi_tokens/tokens_cfg.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/multi_tokens/tokens_cfg.yaml) · blob `2b2d0c28ac0e37a0e8d01fefc1e4c1af832b8fe7`
- [examples/extras/muon/qwen2_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/muon/qwen2_full_sft.yaml) · blob `4380846ade20a0a8fddb6d40a547131ccb6100ee`
- [examples/extras/nlg_eval/llama3_lora_predict.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/nlg_eval/llama3_lora_predict.yaml) · blob `be51c2e44c75ec3b94e9b6a258b62705b1cb65a0`
- [examples/extras/oft/llama3_oft_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/oft/llama3_oft_sft.yaml) · blob `ae027c40b46279b6ac058415942962e11ada3bce`
- [examples/extras/oft/qwen2_5vl_oft_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/oft/qwen2_5vl_oft_sft.yaml) · blob `a688bd521e57ab92a861ba5a5229f73a5f68e7cb`
- [examples/extras/pissa/init.sh](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/pissa/init.sh) · blob `11e1e3576433aedf7471124f705e6e4e2fe2d331`
- [examples/extras/pissa/llama3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/pissa/llama3_lora_sft.yaml) · blob `1668343bbec09711819d875a684ed646a54f8638`
- [examples/extras/qoft/llama3_oft_sft_awq.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/qoft/llama3_oft_sft_awq.yaml) · blob `37ebf25a0f882d7ce977681c0abfdf24df170a31`
- [examples/extras/qoft/llama3_oft_sft_bnb_npu.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/qoft/llama3_oft_sft_bnb_npu.yaml) · blob `5d57a6de22dc23b661fc458d1c17e6fbfad5c470`
- [examples/extras/qoft/llama3_oft_sft_gptq.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/extras/qoft/llama3_oft_sft_gptq.yaml) · blob `3c0987260269fbc2a376c11ed063aa436b4add8c`
- [examples/inference/mossvl.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/inference/mossvl.yaml) · blob `2517474373fa5d00389f570f84a56b4745c3317a`
- [examples/inference/qwen3.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/inference/qwen3.yaml) · blob `1c4232cd8df2c678f866fe19482ad07ac7d1c2ab`
- [examples/inference/qwen3_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/inference/qwen3_full_sft.yaml) · blob `b11f0e8030baf79a113893732c547cbbd68d7ff7`
- [examples/inference/qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/inference/qwen3_lora_sft.yaml) · blob `44d8471c5f57d86d96b5285e441adb8b4a29468d`
- [examples/inference/qwen3vl.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/inference/qwen3vl.yaml) · blob `0c0b5dcbf2bdd60587526d15ed51d7eb83e1c600`
- [examples/ktransformers/accelerate/fsdp2_kt_bf16.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/accelerate/fsdp2_kt_bf16.yaml) · blob `32f2f45695e740932c3c36796c73e2b2a6a3309f`
- [examples/ktransformers/accelerate/fsdp2_kt_int4.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/accelerate/fsdp2_kt_int4.yaml) · blob `32f2f45695e740932c3c36796c73e2b2a6a3309f`
- [examples/ktransformers/accelerate/fsdp2_kt_int8.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/accelerate/fsdp2_kt_int8.yaml) · blob `32f2f45695e740932c3c36796c73e2b2a6a3309f`
- [examples/ktransformers/accelerate/fsdp2_kt_int8_1gpu.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/accelerate/fsdp2_kt_int8_1gpu.yaml) · blob `8cec01593727fb3a9a4da520aab0be3e0debb6db`
- [examples/ktransformers/accelerate/fsdp2_kt_int8_8gpu.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/accelerate/fsdp2_kt_int8_8gpu.yaml) · blob `ef5a656236cc99b69ca44892763341b0afbb8454`
- [examples/ktransformers/train_lora/deepseek_v2_lora_sft_kt.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/train_lora/deepseek_v2_lora_sft_kt.yaml) · blob `7fe3f60d773031311e80b33d6f1cd34c016b16dc`
- [examples/ktransformers/train_lora/deepseek_v3_int8_lora_sft_kt.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/train_lora/deepseek_v3_int8_lora_sft_kt.yaml) · blob `236601e5c1b1fe14d8cae196b2af662afb2db0da`
- [examples/ktransformers/train_lora/deepseek_v3_lora_sft_kt.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/train_lora/deepseek_v3_lora_sft_kt.yaml) · blob `04c3ed34de4be88104550fa1d26af1f95f3b35f0`
- [examples/ktransformers/train_lora/qwen3_5moe_lora_sft_kt.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/train_lora/qwen3_5moe_lora_sft_kt.yaml) · blob `fbba31c5b161bfb9be92caf42b7ad2937c4dd2b3`
- [examples/ktransformers/train_lora/qwen3moe_lora_sft_kt.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/train_lora/qwen3moe_lora_sft_kt.yaml) · blob `f0633e5655b72e62ee23e92100d28ca8d5a8dfed`
- [examples/ktransformers/train_lora/qwen3vlmoe_lora_sft_kt.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/ktransformers/train_lora/qwen3vlmoe_lora_sft_kt.yaml) · blob `2d1a48c02a1588af41e18f3c798ed8453cf41b8f`
- [examples/megatron/qwen2_vl_full.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/megatron/qwen2_vl_full.yaml) · blob `5e22e3ec4d2625201425afd04d42ed5be78ca772`
- [examples/megatron/qwen3_moe_full.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/megatron/qwen3_moe_full.yaml) · blob `3b62bf911462d112812f09805383ed3fa442cffd`
- [examples/megatron_bridge/llama3_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/megatron_bridge/llama3_sft.yaml) · blob `da4e16e7dc5c87d159eddeae16da95386e10f6af`
- [examples/merge_lora/mossvl_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/merge_lora/mossvl_lora_sft.yaml) · blob `942c76445b60a9d337ac82a64f218998d889c264`
- [examples/merge_lora/qwen3_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/merge_lora/qwen3_full_sft.yaml) · blob `9c6fb92551f2d0cc8497d2bf8ba9d0b44d4a71d8`
- [examples/merge_lora/qwen3_gptq.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/merge_lora/qwen3_gptq.yaml) · blob `800bc8d04632881e7fb05472b95a619c0c694d3b`
- [examples/merge_lora/qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/merge_lora/qwen3_lora_sft.yaml) · blob `f4b93f1ba7de67ab292868920129c7e65e6e7ab7`
- [examples/merge_lora/qwen3vl_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/merge_lora/qwen3vl_lora_sft.yaml) · blob `647b0c1ea9a808003e1446c9586fba1fc8953e48`
- [examples/train_full/mossvl_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_full/mossvl_full_sft.yaml) · blob `9fd2815db597fc86832652fe9aa1a9d253ade21d`
- [examples/train_full/qwen3_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_full/qwen3_full_sft.yaml) · blob `adb7a1dfeb98bc1e4c6462a8ee857c3c63e00e48`
- [examples/train_full/qwen3vl_full_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_full/qwen3vl_full_sft.yaml) · blob `06c6d952814eafe054e0ab85957271f0c1a0afff`
- [examples/train_lora/mossvl_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/mossvl_lora_sft.yaml) · blob `99a05786f8df7c47757a8dea7e9775ffda674ef8`
- [examples/train_lora/qwen3_lora_dpo.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_dpo.yaml) · blob `78f4d31f60de0c778e21da3272d3ad634eef11e7`
- [examples/train_lora/qwen3_lora_kto.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_kto.yaml) · blob `51e67318afbfad0d45e3d604e3fce18bfe648b94`
- [examples/train_lora/qwen3_lora_pretrain.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_pretrain.yaml) · blob `a14e9b4627e0165df784fd24054ac2bd2a6e8498`
- [examples/train_lora/qwen3_lora_reward.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_reward.yaml) · blob `17887c02de9381e410d21ca6edae273204cbe459`
- [examples/train_lora/qwen3_lora_sft.sh](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_sft.sh) · blob `bc63ac2d1d9ebb2df3b2cbf937516bd21bcf5305`
- [examples/train_lora/qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_sft.yaml) · blob `ba19e261c281cb784b714d982a3269ca24738d57`
- [examples/train_lora/qwen3_lora_sft_ds3.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_sft_ds3.yaml) · blob `6fcf1c6c2cfa1594ce080853ac39d4b393f95de0`
- [examples/train_lora/qwen3_lora_sft_ray.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_sft_ray.yaml) · blob `1672bca6f430fadea0b75512d4071862108635b6`
- [examples/train_lora/qwen3_preprocess.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_preprocess.yaml) · blob `60901654c013636da128b63b7f948239a8e80441`
- [examples/train_lora/qwen3vl_lora_dpo.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3vl_lora_dpo.yaml) · blob `12e9a615b0608548f5d29fb91ca55b6b4daacc0b`
- [examples/train_lora/qwen3vl_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3vl_lora_sft.yaml) · blob `749bfe60c5acbb8a41fb3e41a57a9628a3432433`
- [examples/train_qlora/llama3_lora_sft_aqlm.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_qlora/llama3_lora_sft_aqlm.yaml) · blob `16a0a4a2ca964e0dc783f3060374db5f622a3932`
- [examples/train_qlora/llama3_lora_sft_awq.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_qlora/llama3_lora_sft_awq.yaml) · blob `9c57c6a13ca2752e00077ee122dc6a650b4c8f3c`
- [examples/train_qlora/llama3_lora_sft_gptq.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_qlora/llama3_lora_sft_gptq.yaml) · blob `fd23e65c1b29ad14ff550b97562c675ab4148d2a`
- [examples/train_qlora/qwen3_lora_sft_bnb_npu.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_qlora/qwen3_lora_sft_bnb_npu.yaml) · blob `0301ee15a26935d426bdc7fa2ac04f2d8fa5a12c`
- [examples/train_qlora/qwen3_lora_sft_otfq.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_qlora/qwen3_lora_sft_otfq.yaml) · blob `3a0e3d4570b9822b2a2c1d753a6af9be6453bcf9`
- [examples/v1/train_batching_strategy/train_full_fsdp2_batching_normal.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_batching_strategy/train_full_fsdp2_batching_normal.yaml) · blob `1e77d61a718052ade66d27ec3a04fd7330b240da`
- [examples/v1/train_batching_strategy/train_full_fsdp2_dynamic_batching.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_batching_strategy/train_full_fsdp2_dynamic_batching.yaml) · blob `18f79227d9b08addde3d7178b6ff8ea9f7eab66e`
- [examples/v1/train_batching_strategy/train_full_fsdp2_dynamic_padding_free.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_batching_strategy/train_full_fsdp2_dynamic_padding_free.yaml) · blob `d13232f008f202700cca85ba2e462ea4e333bc2a`
- [examples/v1/train_batching_strategy/train_full_fsdp2_padding_free.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_batching_strategy/train_full_fsdp2_padding_free.yaml) · blob `c0c6c416351ceeed3df0ef68c312c7e39e8768c5`
- [examples/v1/train_freeze/train_freeze_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_freeze/train_freeze_sft.yaml) · blob `924524dd955ac3ee989a9853f7c94cc8280086c2`
- [examples/v1/train_full/train_full_chunk_loss.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_full_chunk_loss.yaml) · blob `7b001fe666e20838655085d26f4ead090f38b1ef`
- [examples/v1/train_full/train_full_deepspeed.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_full_deepspeed.yaml) · blob `fe495056f4a9712ef99ea296c7cc565464a82ea2`
- [examples/v1/train_full/train_full_fsdp2.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_full_fsdp2.yaml) · blob `27fefd55c08d07d56afb44289c83b787d2e22152`
- [examples/v1/train_full/train_full_liger_kernel.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_full_liger_kernel.yaml) · blob `f785c8a2523d4d521cf7337dfe34aebcc8222298`
- [examples/v1/train_full/train_full_multimodal_ulysses_cp.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_full_multimodal_ulysses_cp.yaml) · blob `98d5b015b36c2877ef97dab6c5d9f95dd6e8a6ff`
- [examples/v1/train_full/train_full_muon.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_full_muon.yaml) · blob `bcbc6067a5ba7b1a9e11724650c9e36a5c64ba00`
- [examples/v1/train_full/train_full_qwen3_moe_fsdpturbo_ep_fsdp.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_full_qwen3_moe_fsdpturbo_ep_fsdp.yaml) · blob `676ae6f1e95cc269bfc001d67836703140e65a0b`
- [examples/v1/train_full/train_full_ulysses_cp.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_full_ulysses_cp.yaml) · blob `1ee5b1439b68608211d5778d61ac75d41b1495c6`
- [examples/v1/train_full/train_multimodal.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_full/train_multimodal.yaml) · blob `084e041ed0bffcf5ec0f22c227d8e7257ad4a253`
- [examples/v1/train_lora/export_lora.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_lora/export_lora.yaml) · blob `40e8d5211150e90a9372ce74dd7fe11c1660b68b`
- [examples/v1/train_lora/train_lora_dpo.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_lora/train_lora_dpo.yaml) · blob `660bc29bc46b8a0173b7297c675849585382076e`
- [examples/v1/train_lora/train_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_lora/train_lora_sft.yaml) · blob `0da1a1abd1c2b462d245428480e92cfcc2ee5f1a`
- [examples/v1/train_lora/train_lora_sft_rank0.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_lora/train_lora_sft_rank0.yaml) · blob `ff401844e98315493c5f992f7fe31f5cf488d2e0`
- [examples/v1/train_qlora/quantization.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/v1/train_qlora/quantization.yaml) · blob `79a126c29247b3ccb07e3d098cbe19e64a74abb2`

## pyproject.toml

- [pyproject.toml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/pyproject.toml) · blob `7ff84c62e622a0bea2047378f22c370dbbff02ff`

## requirements

- [requirements/adam-mini.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/adam-mini.txt) · blob `14321813980b571835d55e9b0f52a20b218e07fa`
- [requirements/apollo.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/apollo.txt) · blob `0ae4210c831d1209cfcf9732306cd1af45982dc0`
- [requirements/aqlm.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/aqlm.txt) · blob `0ff8e7d604fa90dd4b73b302394d5ae9fdaac191`
- [requirements/badam.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/badam.txt) · blob `3abf0cf2c20dbfb7fa9cbbfd6bcc27ac21f46568`
- [requirements/bitsandbytes.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/bitsandbytes.txt) · blob `0dc8b51f5df1c411d2255d655391255a2cf185f4`
- [requirements/deepspeed.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/deepspeed.txt) · blob `2c16ba94294844def077fbc2a1d7aa80fdf8e9fc`
- [requirements/dev.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/dev.txt) · blob `f0fc17fcc74f6378e38b81f6eee2b623b7c8aed5`
- [requirements/eetq.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/eetq.txt) · blob `05b3cb95097b52f6ab848d6740e5784bb2be703b`
- [requirements/fp8-te.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/fp8-te.txt) · blob `899bc8c4a139c5a6877bd6249a7d2024b484bdb4`
- [requirements/fp8.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/fp8.txt) · blob `6079c17fee167bc71d7299be8f937e531006a5be`
- [requirements/fsdpturbo.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/fsdpturbo.txt) · blob `064513751d5bc22a7043c3f114355e43c7c20266`
- [requirements/galore.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/galore.txt) · blob `e101ee74e3485260b598bdeb1bcd8abc89ddac41`
- [requirements/gptq.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/gptq.txt) · blob `e39481d1f88523c731b81afefee5ef743de6cd03`
- [requirements/hqq.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/hqq.txt) · blob `800846850a99a30935d119e3e417de8e9fc45fe9`
- [requirements/ktransformers.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/ktransformers.txt) · blob `7f67b35b635828d79f651c7abff0d0f672857607`
- [requirements/liger-kernel.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/liger-kernel.txt) · blob `1fd2178ac7cfcf15dba814d2de9302b6578ff8d3`
- [requirements/metrics.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/metrics.txt) · blob `533493d8287cf9a94f50810af3e2fb08a27bf3b3`
- [requirements/minicpm-v.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/minicpm-v.txt) · blob `2c05274c622676b017e12cf2210cd72e445dd247`
- [requirements/moss-vl.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/moss-vl.txt) · blob `e1186a6a188bae757c697facb28329dea6b42218`
- [requirements/npu.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/npu.txt) · blob `9cc3c9ade31db4013fc518f74e004e1e54100452`
- [requirements/openmind.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/openmind.txt) · blob `0c75348f3cf28f7f639f66d8d095f248eb703550`
- [requirements/sglang.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/sglang.txt) · blob `ed4239944f2c74550c1d013775ab3672c8f500a8`
- [requirements/swanlab.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/swanlab.txt) · blob `85381455c6b3bb922c0c4c23a82810e3ddb41f04`
- [requirements/triton_ascend.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/triton_ascend.txt) · blob `40f052aa9bc4e0d8030e3ac9ac1fb0939a48e7e8`
- [requirements/vllm.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/vllm.txt) · blob `881bd2c645948278f2c3a45b5fa7b9ffa479aea4`
- [requirements/xpu.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/requirements/xpu.txt) · blob `a1880bd66f678781348d18f82cb4fc1bdaa5b965`

## scripts

- [scripts/api_example/test_image.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/api_example/test_image.py) · blob `afd2b69c4ec951bcc6b08b4d5e50f11048f7f7d8`
- [scripts/api_example/test_toolcall.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/api_example/test_toolcall.py) · blob `e291ba693df025673d14198fd07fbbe5e8552421`
- [scripts/bench_qwen.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/bench_qwen.py) · blob `4ab48dda2c42b4e3ea291ee539c2e4afe7b51c99`
- [scripts/convert_ckpt/llamafy_baichuan2.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/convert_ckpt/llamafy_baichuan2.py) · blob `62dc6a51ac38e5fa9dc06a2136bb9dd2154af055`
- [scripts/convert_ckpt/llamafy_qwen.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/convert_ckpt/llamafy_qwen.py) · blob `599b0f1226cde2e3de6f009c056b8b89c84838b4`
- [scripts/convert_ckpt/tiny_llama4.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/convert_ckpt/tiny_llama4.py) · blob `2a96cfa60f30660e572baa436c7f7b67e2c907f1`
- [scripts/convert_ckpt/tiny_qwen3.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/convert_ckpt/tiny_qwen3.py) · blob `902c0ec09b10d456f8936cbdef60fffac1678720`
- [scripts/dcp2hf.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/dcp2hf.py) · blob `8e3256bbb7c2fb9c47ffcbf76b85822f39b28c2f`
- [scripts/eval_bleu_rouge.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/eval_bleu_rouge.py) · blob `4ff96dd8ecbdd15946020dbcd15625ba801d43c4`
- [scripts/hf2dcp.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/hf2dcp.py) · blob `da51580b6203efd6060ec5c5c94d3c9fa798a027`
- [scripts/llama_pro.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/llama_pro.py) · blob `7e4b9448505769104f5155ce7bc4c3ef9ec01bc6`
- [scripts/loftq_init.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/loftq_init.py) · blob `3a7933889be55a254b2417e9dca2ce2b7d691401`
- [scripts/megatron_merge.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/megatron_merge.py) · blob `e8e9e12a316942375a0a2dde3d2e2637992ed963`
- [scripts/pissa_init.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/pissa_init.py) · blob `405a1472b42b8981a8ae52b612acdf07c60c66ad`
- [scripts/qwen_omni_merge.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/qwen_omni_merge.py) · blob `7236d23c3c023d4d454dfefeaaa96229ddb0afa5`
- [scripts/stat_utils/cal_flops.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/stat_utils/cal_flops.py) · blob `3dc049959bb057737d4320a1960b1a43465b4662`
- [scripts/stat_utils/cal_lr.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/stat_utils/cal_lr.py) · blob `eb35c47e7ab6b196e5b95e9310e0ad7d27e12899`
- [scripts/stat_utils/cal_mfu.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/stat_utils/cal_mfu.py) · blob `f1d4446eef71daa3ffa143fc456a0f58c928d491`
- [scripts/stat_utils/cal_ppl.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/stat_utils/cal_ppl.py) · blob `56b3c8d1177c4eb8139eb2b38de329a190ca3023`
- [scripts/stat_utils/length_cdf.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/stat_utils/length_cdf.py) · blob `c459c8fa0911b86bcce5a6b47ae5b2da1b670b2f`
- [scripts/vllm_infer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/scripts/vllm_infer.py) · blob `44bdbed83422cbd9616d5e9af47b2e6f3a0966fc`

## src

- [src/api.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/api.py) · blob `61215459ed91c6fa529a719cb9dac57223754d2e`
- [src/llamafactory/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/__init__.py) · blob `b1567ef572714881cc464db25d3da3d08a460963`
- [src/llamafactory/api/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/api/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/api/app.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/api/app.py) · blob `8ec0679cb7e053058f52bdbf947cb13e554c5ca8`
- [src/llamafactory/api/chat.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/api/chat.py) · blob `06e15251872cb49180587c89c2ed504807de39be`
- [src/llamafactory/api/common.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/api/common.py) · blob `7b4e9602de7ebc10b4f15c68ad9167cb9d80d8ef`
- [src/llamafactory/api/protocol.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/api/protocol.py) · blob `19e5279dcbd387cca14c76058a4acf8f5155a221`
- [src/llamafactory/chat/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/chat/__init__.py) · blob `15d8b9ba2d77d6f300d59300da5a49abd3ed4e57`
- [src/llamafactory/chat/base_engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/chat/base_engine.py) · blob `6d497c1ae927f94f396c18833b18cdb894cbd59d`
- [src/llamafactory/chat/chat_model.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/chat/chat_model.py) · blob `9ffd8647c7f5233957be9379f697a4818b3026e0`
- [src/llamafactory/chat/hf_engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/chat/hf_engine.py) · blob `a7ef1e2cb6f5d40a0e3f7278660d9080434af3c9`
- [src/llamafactory/chat/sglang_engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/chat/sglang_engine.py) · blob `342dea45544f0e6b259ceae0b41c27aec3dd8553`
- [src/llamafactory/chat/vllm_engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/chat/vllm_engine.py) · blob `5e2b625a396160dc9c9bec1018157da716af912b`
- [src/llamafactory/cli.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/cli.py) · blob `d574bf1db543f5379f074e276898826234708037`
- [src/llamafactory/data/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/__init__.py) · blob `11c8c9fcecd10e736e240196fde98f833c9df3dc`
- [src/llamafactory/data/collator.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/collator.py) · blob `16b41452ed8fbf71003948ac4779b6ef2905e03a`
- [src/llamafactory/data/converter.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/converter.py) · blob `ad49deded441318e722cd07bfe331feff6c498a5`
- [src/llamafactory/data/data_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/data_utils.py) · blob `144dbde1d8efa55fe1e9ff350110242678aaa223`
- [src/llamafactory/data/formatter.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/formatter.py) · blob `1c080f8812d0d9feb320e949d39bfcb1a0e1e582`
- [src/llamafactory/data/loader.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/loader.py) · blob `d3d44e6f3c25de0fa46c333be6a3a39d5f1dcfee`
- [src/llamafactory/data/mm_plugin.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/mm_plugin.py) · blob `a299c93f06b6a2937ef51a752cc2f1ee70ff15ad`
- [src/llamafactory/data/parser.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/parser.py) · blob `5209da64954a363c59d232010111139b7b37fdfe`
- [src/llamafactory/data/processor/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/processor/__init__.py) · blob `357ab7899f9eecbd29344482d109b89af274ea2e`
- [src/llamafactory/data/processor/feedback.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/processor/feedback.py) · blob `871615b9266e501f25f68e84e4536c0d24617803`
- [src/llamafactory/data/processor/pairwise.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/processor/pairwise.py) · blob `94101deb8e75af73c1851720604994a11f2eb87d`
- [src/llamafactory/data/processor/pretrain.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/processor/pretrain.py) · blob `3fa6b1ca58a8d59493cd4b43c51cb268080cc506`
- [src/llamafactory/data/processor/processor_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/processor/processor_utils.py) · blob `db44b19cf6fc84d6551fb7cce82283774ae72030`
- [src/llamafactory/data/processor/supervised.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/processor/supervised.py) · blob `26f14c69a7a708fe8a0be712c8b4e27d939bde1f`
- [src/llamafactory/data/processor/unsupervised.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/processor/unsupervised.py) · blob `256174b6dd38696b5b180501102af40ff395d0a9`
- [src/llamafactory/data/template.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/template.py) · blob `d499b4e00e5d0da5b933448f637a0f1adc6a98a9`
- [src/llamafactory/data/tool_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/data/tool_utils.py) · blob `b74fdc65c8459ef9bfb9fdb975f8074bb3f0ef62`
- [src/llamafactory/eval/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/eval/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/eval/evaluator.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/eval/evaluator.py) · blob `7729c59bf413cb66054a3e06f2e42d6794cb495d`
- [src/llamafactory/eval/template.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/eval/template.py) · blob `5742469787a5001001a2702f183306bd2a312aef`
- [src/llamafactory/extras/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/extras/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/extras/constants.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/extras/constants.py) · blob `f3a521fefb7e2a7d6a642a8501003213f2b1d45b`
- [src/llamafactory/extras/env.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/extras/env.py) · blob `2f0de31f509bddd77dc8c3fee6fec7b4bd504749`
- [src/llamafactory/extras/logging.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/extras/logging.py) · blob `35ff65bb6b5d93e03383ed19fb265815318e4c52`
- [src/llamafactory/extras/misc.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/extras/misc.py) · blob `f95ab9f49b06f45b79ef6f01cf9d7b0d539f90a8`
- [src/llamafactory/extras/packages.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/extras/packages.py) · blob `1039bdec2599374709bee7dfce9794f1d64bc692`
- [src/llamafactory/extras/ploting.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/extras/ploting.py) · blob `be89bcc5cb30429b60e13e71eba465f83de90e74`
- [src/llamafactory/hparams/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/__init__.py) · blob `1803c4c3fc3f92363d2a22eb44c64b3b934cc043`
- [src/llamafactory/hparams/data_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/data_args.py) · blob `68ee772cc62fb4e92fbf638e34b2567a41527fd9`
- [src/llamafactory/hparams/evaluation_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/evaluation_args.py) · blob `4826ec5d6dd812f5b90df418cfd56992066c6549`
- [src/llamafactory/hparams/finetuning_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/finetuning_args.py) · blob `007b9674edfc9e3a945c69c349a20cf8f48358be`
- [src/llamafactory/hparams/generating_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/generating_args.py) · blob `7eacb14763ac972a08ea59b74a799e704e4f9bc9`
- [src/llamafactory/hparams/megatron_bridge_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/megatron_bridge_args.py) · blob `b1137ba049dca75efcb8f5e3588eca051a755ecc`
- [src/llamafactory/hparams/model_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/model_args.py) · blob `f99f39e0f5bdcc3695ce19b3ae3f2ca9948ca9f3`
- [src/llamafactory/hparams/parser.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/parser.py) · blob `1f686d641423887b20a0d88a0a7e4f89e2fa6505`
- [src/llamafactory/hparams/training_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/training_args.py) · blob `84f4d8e6cca1c26b9311780248d552f25639cffa`
- [src/llamafactory/launcher.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/launcher.py) · blob `7366b9789040f954776b19a57e0dfdb87b6f1c5c`
- [src/llamafactory/model/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/__init__.py) · blob `71d4f47f43273457d15e38e3454c5f4bc156da3d`
- [src/llamafactory/model/adapter.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/adapter.py) · blob `ce4a8d1b356ef93dd477780d1e18501b2f1cd9c4`
- [src/llamafactory/model/loader.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/loader.py) · blob `b162c8820affadf7e673076717f6c88919ee4f83`
- [src/llamafactory/model/model_utils/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/model/model_utils/attention.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/attention.py) · blob `f3ab25df62a9c22eb72ebf40cb96b346614c359a`
- [src/llamafactory/model/model_utils/checkpointing.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/checkpointing.py) · blob `a77dce010e9956017a347d2cdaad63f50d05a0b8`
- [src/llamafactory/model/model_utils/embedding.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/embedding.py) · blob `2af9964697da33a07ed2bcd5bbcf12cab40519ce`
- [src/llamafactory/model/model_utils/kv_cache.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/kv_cache.py) · blob `4f622f73f30017868f55e8503a968593c309b204`
- [src/llamafactory/model/model_utils/liger_kernel.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/liger_kernel.py) · blob `0eece68f83b75d69bd47b93e940d1b128f9bf542`
- [src/llamafactory/model/model_utils/longlora.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/longlora.py) · blob `f7c36ee0cb89959fa692d57cc9f85bb162ca58a0`
- [src/llamafactory/model/model_utils/misc.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/misc.py) · blob `e0a62566c8e6fec20cebb882a69fed491880c6c8`
- [src/llamafactory/model/model_utils/mod.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/mod.py) · blob `5f67cd50dbc9016fc2cd650ae496501e8c594e76`
- [src/llamafactory/model/model_utils/moe.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/moe.py) · blob `339e9dc99f3e5bebf23e1f7b75fe2d3a519a44c6`
- [src/llamafactory/model/model_utils/packing.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/packing.py) · blob `edbb30a6cb70314eaf89b20aa1f3bee80beaee5e`
- [src/llamafactory/model/model_utils/quantization.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/quantization.py) · blob `745237553c13d4ca07fd4dea406b3f60e2759193`
- [src/llamafactory/model/model_utils/rope.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/rope.py) · blob `b217735b76d847296471336fe615db9d325520d8`
- [src/llamafactory/model/model_utils/unsloth.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/unsloth.py) · blob `7340d751dfb4d5175397dba22ab76356e2461a99`
- [src/llamafactory/model/model_utils/valuehead.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/valuehead.py) · blob `7409a22edd3a66f08b9b9c3b99d2e9354e32c4c3`
- [src/llamafactory/model/model_utils/visual.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/model_utils/visual.py) · blob `98b712db13510ac09eea7b2ef3e72c91ea1411f4`
- [src/llamafactory/model/patcher.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/model/patcher.py) · blob `a3e2d54b64ae7b218c18ae77a7f40482cacbc45a`
- [src/llamafactory/third_party/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/third_party/muon/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/muon/__init__.py) · blob `afa615d0df2163ea271fff8e128aa8c81224dd8f`
- [src/llamafactory/third_party/muon/muon.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/muon/muon.py) · blob `d7482c36b8196cf1dfaa8b0ae441b1cfd7ae5dc3`
- [src/llamafactory/third_party/triton/chunk_delta_h.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/triton/chunk_delta_h.py) · blob `ddbf1c6a68087ffd9a05884626aa5407e8425f2e`
- [src/llamafactory/third_party/triton/chunk_gated_delta_rule.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/triton/chunk_gated_delta_rule.py) · blob `b1d5e83c0fc4d93f6205ad00f0baa626e4582ef9`
- [src/llamafactory/third_party/triton/chunk_o.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/triton/chunk_o.py) · blob `96cd84138c87a3121b20bb8f4c0caa8efe0a66ba`
- [src/llamafactory/third_party/triton/chunk_scaled_dot_kkt.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/triton/chunk_scaled_dot_kkt.py) · blob `0b3dec4bd3d8beaf353811e5fa4111736f7608f7`
- [src/llamafactory/third_party/triton/cumsum.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/triton/cumsum.py) · blob `5c5068d32a6c932b0411c5082327cd526f557df4`
- [src/llamafactory/third_party/triton/solve_tril.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/triton/solve_tril.py) · blob `4ffa3bdc346a85a260b3c2df9233868b040aee96`
- [src/llamafactory/third_party/triton/utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/triton/utils.py) · blob `e817e2eb6891fc853bd7453b462f7acde77272ec`
- [src/llamafactory/third_party/triton/wy_fast.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/third_party/triton/wy_fast.py) · blob `d22c12f6e44fec7afda52a1d72d9072218b46fde`
- [src/llamafactory/train/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/train/callbacks.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/callbacks.py) · blob `b3826a7a9db17ab706c48fdea9756d20978ff3f9`
- [src/llamafactory/train/dpo/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/dpo/__init__.py) · blob `73c1a4a6bd8a6c68c6875f19fdf8eb9899e70826`
- [src/llamafactory/train/dpo/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/dpo/trainer.py) · blob `5b800a72b75c9e1f047733aa9b5f9902fd86e477`
- [src/llamafactory/train/dpo/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/dpo/workflow.py) · blob `2094493657a17dfd787da3c138239dc3e709efd4`
- [src/llamafactory/train/fp8_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/fp8_utils.py) · blob `33728feadc3d9b1b4e22306b99f22130c0eff7c4`
- [src/llamafactory/train/hyper_parallel/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/hyper_parallel/__init__.py) · blob `88bbf20ddca803bc3c3aa272605d508efc1f0c43`
- [src/llamafactory/train/hyper_parallel/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/hyper_parallel/trainer.py) · blob `c0509962256caf75aa4d0ffa50d6e1251515e572`
- [src/llamafactory/train/hyper_parallel/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/hyper_parallel/workflow.py) · blob `7f2efcd9062f23ebc3fabbb6569024b50dd394ed`
- [src/llamafactory/train/kto/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/kto/__init__.py) · blob `491b067e41c53641f989d7dc17a22d6765f5684d`
- [src/llamafactory/train/kto/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/kto/trainer.py) · blob `cb9b73b39ad949b4052b5e6bc66c3543d4fea135`
- [src/llamafactory/train/kto/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/kto/workflow.py) · blob `df0794e3e986e0a0b55d667b255ee8c714fb8911`
- [src/llamafactory/train/mca/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/mca/__init__.py) · blob `2b3fb6eba7260ff5b6a01e19f9f05fc172a64df4`
- [src/llamafactory/train/mca/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/mca/trainer.py) · blob `ad537588ac2d7fbdae55f764b7130ec67cbb3b63`
- [src/llamafactory/train/mca/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/mca/workflow.py) · blob `f4b9d8df7e1aa6f5031ee9d1af11be2d973673e1`
- [src/llamafactory/train/megatron_bridge/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/megatron_bridge/__init__.py) · blob `88bbf20ddca803bc3c3aa272605d508efc1f0c43`
- [src/llamafactory/train/megatron_bridge/config_builder.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/megatron_bridge/config_builder.py) · blob `a84fd27a9ed4527834b9aa3349a307fde894ad6b`
- [src/llamafactory/train/megatron_bridge/dataset_export.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/megatron_bridge/dataset_export.py) · blob `0a4397291b55afca4893b1787d69fc3685840474`
- [src/llamafactory/train/megatron_bridge/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/megatron_bridge/workflow.py) · blob `eb49ec9988a2bdfb3bcc423bd464e568b1a2c16c`
- [src/llamafactory/train/ppo/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/ppo/__init__.py) · blob `ed9bc4d274d2b0a5cc16074858cd552348620ceb`
- [src/llamafactory/train/ppo/ppo_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/ppo/ppo_utils.py) · blob `9d462e77b74e88d66af8e60f3483786c11607bea`
- [src/llamafactory/train/ppo/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/ppo/trainer.py) · blob `eaa74bb33966c9c3d50150d44006936512397a69`
- [src/llamafactory/train/ppo/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/ppo/workflow.py) · blob `282a2f683672c2047dca4ce8362622e6e48c04aa`
- [src/llamafactory/train/pt/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/pt/__init__.py) · blob `1f5c2898372d7dc2563472741fe76bba04de5479`
- [src/llamafactory/train/pt/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/pt/trainer.py) · blob `ffb040fdd65ce2c39acf47d3d3fa8da907a89956`
- [src/llamafactory/train/pt/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/pt/workflow.py) · blob `17ea604bf76dc05cade1810c230791cb654e7056`
- [src/llamafactory/train/rm/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/rm/__init__.py) · blob `f0e8a45c0f6a4e426c459f0d3e353b8b5e3ebce7`
- [src/llamafactory/train/rm/metric.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/rm/metric.py) · blob `ae334cd9a27540ef07050161b22714947b7a4c8b`
- [src/llamafactory/train/rm/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/rm/trainer.py) · blob `7ee1ab7d25a26fa6e997ce2369948d137c019480`
- [src/llamafactory/train/rm/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/rm/workflow.py) · blob `326561c462bc490d845117a84f234dd194a12a72`
- [src/llamafactory/train/sft/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/sft/__init__.py) · blob `6107a9ae741be83e0b3038015316f5ca7510fa76`
- [src/llamafactory/train/sft/metric.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/sft/metric.py) · blob `76ef1dec054916b8046e713478f84c44731076af`
- [src/llamafactory/train/sft/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/sft/trainer.py) · blob `993cba8393a58bfea712148c4f231ae03d48a97b`
- [src/llamafactory/train/sft/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/sft/workflow.py) · blob `b50f53ffd29041370ffa331332d4dc0bdf4284ed`
- [src/llamafactory/train/test_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/test_utils.py) · blob `f31b3d2fc8b7b27fc60ec82a472d9da74ad519c4`
- [src/llamafactory/train/trainer_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/trainer_utils.py) · blob `a0e898e399e7d77d4dbe66f4327e9e04c390f4c2`
- [src/llamafactory/train/tuner.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/tuner.py) · blob `97a6ef725d32fe519b5591f339674e666e8bb5eb`
- [src/llamafactory/v1/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/accelerator/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/accelerator/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/accelerator/helper.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/accelerator/helper.py) · blob `b83e7f2f574e525be2ba423ea1f3846ca6ada380`
- [src/llamafactory/v1/accelerator/interface.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/accelerator/interface.py) · blob `530685551ff81ca93705d2dd30dd61cf4b872291`
- [src/llamafactory/v1/accelerator/profiler.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/accelerator/profiler.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/config/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/config/__init__.py) · blob `4bb5fc32cc1d267ced8745b6c2409187e1eacadd`
- [src/llamafactory/v1/config/arg_parser.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/config/arg_parser.py) · blob `9aa160644d303066278b393577efbd3c12921b6f`
- [src/llamafactory/v1/config/arg_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/config/arg_utils.py) · blob `db52f970097ebd6637bf053871a1a093b7725c24`
- [src/llamafactory/v1/config/data_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/config/data_args.py) · blob `8693df429ebb2be2a1a447cbdc634aea64e39c1b`
- [src/llamafactory/v1/config/model_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/config/model_args.py) · blob `8c6542162a047bb2c7839b50d421961da17f7288`
- [src/llamafactory/v1/config/sample_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/config/sample_args.py) · blob `3971ee71edecb61eb5c02046ca863d5833fac596`
- [src/llamafactory/v1/config/training_args.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/config/training_args.py) · blob `5c01d93e07909bb6d596d1ad9061cd5dbb6d1ac3`
- [src/llamafactory/v1/core/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/core/base_sampler.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/base_sampler.py) · blob `4e044952d902ace1c82d749fca5f40c0b5beb88f`
- [src/llamafactory/v1/core/base_trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/base_trainer.py) · blob `e04e8a9b2c73925f0ef4ab9f57288b86eaed837e`
- [src/llamafactory/v1/core/data_engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/data_engine.py) · blob `810cb43adfec955de34517b2cc1771c8fcf8e06a`
- [src/llamafactory/v1/core/model_engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/model_engine.py) · blob `00124d48735d1df683b54dca16019f9ead9b5902`
- [src/llamafactory/v1/core/rendering/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/rendering/__init__.py) · blob `825b9920cbe713f7cccf3ba947fc385b2607367c`
- [src/llamafactory/v1/core/rendering/escape.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/rendering/escape.py) · blob `a4c7d1fbdaee2286075c25f17a4839c759534119`
- [src/llamafactory/v1/core/rendering/format.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/rendering/format.py) · blob `81cc3323f5b1c9eb3fc85ad349e06383ef7f5f50`
- [src/llamafactory/v1/core/rendering/rendering.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/rendering/rendering.py) · blob `87f7d6a7664e1d4ad7cbdc7d0a295080cd665ccd`
- [src/llamafactory/v1/core/utils/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/utils/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/core/utils/batching.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/utils/batching.py) · blob `6009bac94934e501707a589786b3c0b502130444`
- [src/llamafactory/v1/core/utils/callback.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/utils/callback.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/core/utils/checkpoint.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/utils/checkpoint.py) · blob `8b6127db13304dd4a9b6017c51c143bbe1779679`
- [src/llamafactory/v1/core/utils/collation.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/utils/collation.py) · blob `6f33f85f6e603949d1b3071d02a3542e01d2c939`
- [src/llamafactory/v1/core/utils/inference_engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/core/utils/inference_engine.py) · blob `dc07f11953d4c4a3bad7fdca9d955c5d86b2fee8`
- [src/llamafactory/v1/launcher.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/launcher.py) · blob `b20988b24fe8bcbb36e9853a16901c2818ad7be9`
- [src/llamafactory/v1/plugins/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/data_plugins/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/data_plugins/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/data_plugins/converter.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/data_plugins/converter.py) · blob `0882e03396d492446d80a2b92e7d3f380f40d573`
- [src/llamafactory/v1/plugins/data_plugins/loader.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/data_plugins/loader.py) · blob `eb24ca614ae749bd497c6c4fde935885af44a831`
- [src/llamafactory/v1/plugins/model_plugins/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/model_plugins/add_token.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/add_token.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/model_plugins/chunk_loss.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/chunk_loss.py) · blob `8a4dd01aa653c249a2a69a5d884bd24cc55917f4`
- [src/llamafactory/v1/plugins/model_plugins/deepspeed_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/deepspeed_utils.py) · blob `d31a2dad71fb706386aa8851b6354171d60f6b32`
- [src/llamafactory/v1/plugins/model_plugins/initialization.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/initialization.py) · blob `efb8f22f79f6c6e5abbb2d0410cd928abbf1d120`
- [src/llamafactory/v1/plugins/model_plugins/kernels/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/model_plugins/kernels/base.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/base.py) · blob `2174f0de4c8ceaf54204600e5ac2e347f261c46a`
- [src/llamafactory/v1/plugins/model_plugins/kernels/interface.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/interface.py) · blob `33c9b129090c9127173955e243440567c3cbfd0f`
- [src/llamafactory/v1/plugins/model_plugins/kernels/liger_kernel_ops.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/liger_kernel_ops.py) · blob `7447354156518cb653d19988a8aaa25879ffa972`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/linear_attention/fla.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/linear_attention/fla.py) · blob `fe24d28ef94b0102a3d10703815203bcc27747f8`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/cuda_fused_moe.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/cuda_fused_moe.py) · blob `cfc75fd0281ca195a3f282420878552a19601a63`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/npu_fused_moe.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/npu_fused_moe.py) · blob `e377acca9a75329b99ca868c77c030bbfa1af897`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/npu_swiglu.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/npu_swiglu.py) · blob `e56e09fe2367645c1cc9dead546a3e71db9ba1f4`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/triton_grouped_gemm.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/mlp/triton_grouped_gemm.py) · blob `c75b8f5ce1fad9ebd0a8b48748918a7a0a58fa1e`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/rms_norm/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/rms_norm/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/rms_norm/npu_rms_norm.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/rms_norm/npu_rms_norm.py) · blob `b6c2cf8ce17b4e513ca93a552c38f9d77b3567a7`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/rope/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/rope/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/model_plugins/kernels/ops/rope/npu_rope.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/kernels/ops/rope/npu_rope.py) · blob `74fdefde064dca2647b1c812c136eabbd0b0aff8`
- [src/llamafactory/v1/plugins/model_plugins/parallelization/batch.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/parallelization/batch.py) · blob `745d2bffeae87ac3bd5fc44ba98961f21a7c7c09`
- [src/llamafactory/v1/plugins/model_plugins/parallelization/gdn_attention.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/parallelization/gdn_attention.py) · blob `4edb4056d4025c1a8b2bfb8d1f1739c467f5fae2`
- [src/llamafactory/v1/plugins/model_plugins/parallelization/hook.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/parallelization/hook.py) · blob `fff388dfa3f660ec722ae4f602ac0b3d270082c0`
- [src/llamafactory/v1/plugins/model_plugins/parallelization/seq_comm.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/parallelization/seq_comm.py) · blob `3460c139497d1f2c59bdd5dff89ebd1022b70851`
- [src/llamafactory/v1/plugins/model_plugins/parallelization/sequence_parallel.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/parallelization/sequence_parallel.py) · blob `fd2f53ef69f1b58aa6ec3765788684e4f030053b`
- [src/llamafactory/v1/plugins/model_plugins/parallelization/ulysses.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/parallelization/ulysses.py) · blob `3c8bfe9b2c866a085e4058f43e77b8902d4da9cf`
- [src/llamafactory/v1/plugins/model_plugins/peft.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/peft.py) · blob `9030a6363d18b7a01834e772a951db1e9a7ad422`
- [src/llamafactory/v1/plugins/model_plugins/quantization.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/model_plugins/quantization.py) · blob `b889b5cf72704bb6f82a88da112b3572956762e9`
- [src/llamafactory/v1/plugins/sampler_plugins/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/sampler_plugins/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/sampler_plugins/vllm.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/sampler_plugins/vllm.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/trainer_plugins/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/trainer_plugins/batching.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/batching.py) · blob `2425d7c195026a79302b6db1ca728564ed238bc5`
- [src/llamafactory/v1/plugins/trainer_plugins/distributed/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/distributed/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/trainer_plugins/distributed/base.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/distributed/base.py) · blob `2b05f76eb2cd65aeb65cd974566ece948caf1240`
- [src/llamafactory/v1/plugins/trainer_plugins/distributed/deepspeed.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/distributed/deepspeed.py) · blob `b7e72ddd1706eb2d66b2ea19d2b0702d6d993355`
- [src/llamafactory/v1/plugins/trainer_plugins/distributed/fsdp2.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/distributed/fsdp2.py) · blob `ee539ac01a8efbdb6f07f1b95bb2dc9bf0e444ee`
- [src/llamafactory/v1/plugins/trainer_plugins/distributed/fsdpturbo.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/distributed/fsdpturbo.py) · blob `7b2ce9acd0b2ac30bcaa7c8769d3709569242878`
- [src/llamafactory/v1/plugins/trainer_plugins/distributed/interface.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/distributed/interface.py) · blob `7bad851305d0ea58c3458f0af4f001ee3ef9a028`
- [src/llamafactory/v1/plugins/trainer_plugins/lr_scheduler.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/lr_scheduler.py) · blob `02c9e8b034a20870ed3b2e67f15e2ac45fe3ef1f`
- [src/llamafactory/v1/plugins/trainer_plugins/optimizers/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/optimizers/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/plugins/trainer_plugins/optimizers/muon_optimizer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/optimizers/muon_optimizer.py) · blob `6fc692ef6d3b005fda92857994b0c0f2641aa12a`
- [src/llamafactory/v1/plugins/trainer_plugins/optimizers/optimizer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/plugins/trainer_plugins/optimizers/optimizer.py) · blob `dbc634d5789a14b4c5e6d505cc983ced3c84e77b`
- [src/llamafactory/v1/samplers/cli_sampler.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/samplers/cli_sampler.py) · blob `a40ddf4a77c576221ae3d2adc56a3bfc1c64069a`
- [src/llamafactory/v1/trainers/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/trainers/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/trainers/dpo_trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/trainers/dpo_trainer.py) · blob `b2251237325264c41b96c2c5a4641b0e2550446f`
- [src/llamafactory/v1/trainers/rm_trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/trainers/rm_trainer.py) · blob `2a32ae2c6a4e34a4b25a3b9558d841ed6ffe466b`
- [src/llamafactory/v1/trainers/sft_trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/trainers/sft_trainer.py) · blob `cc92bac049e8f09177d2f0dad573736c337c3068`
- [src/llamafactory/v1/utils/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/v1/utils/callbacks/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/callbacks/__init__.py) · blob `0da31ed3fce2147fbfcf8972fbef5ec7a8ccd4d7`
- [src/llamafactory/v1/utils/callbacks/logging_callback.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/callbacks/logging_callback.py) · blob `6c6278f09fef07ae9c791fc5d132f390a0776b0f`
- [src/llamafactory/v1/utils/callbacks/trainer_callback.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/callbacks/trainer_callback.py) · blob `400514d29538d4160549d37c974b4b46bc733782`
- [src/llamafactory/v1/utils/constants.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/constants.py) · blob `caf2715d04bb1149bd4b6c96dc908993cdb1d486`
- [src/llamafactory/v1/utils/dtype.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/dtype.py) · blob `331c9bddf2be56eae17ea414fc95b4f5de36edca`
- [src/llamafactory/v1/utils/env.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/env.py) · blob `fc17d7cc92f60149f48f9b74d693956f12be8218`
- [src/llamafactory/v1/utils/helper.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/helper.py) · blob `3f04d8e88225b373aee6276a62ef10178681856c`
- [src/llamafactory/v1/utils/logging.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/logging.py) · blob `4d38927ff9edaa7797bd1e06143d29b5ba213a07`
- [src/llamafactory/v1/utils/objects.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/objects.py) · blob `fc7ea1da5eb7ae6ad4ea5e73d9bcd7a78fef3abc`
- [src/llamafactory/v1/utils/packages.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/packages.py) · blob `b2b76aa651ab1c59da3f8bfdd7caccf37de9bba9`
- [src/llamafactory/v1/utils/plugin.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/plugin.py) · blob `8debd5e7ffd4ebacafd26ed3df43a4c80c2ebe82`
- [src/llamafactory/v1/utils/pytest.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/pytest.py) · blob `bbbaa08cf0aaf8180d9fe02f56d236e40d64b3bd`
- [src/llamafactory/v1/utils/types.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/v1/utils/types.py) · blob `b259e3277d02ea58e1bc5f2843ebd8f957972873`
- [src/llamafactory/webui/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [src/llamafactory/webui/chatter.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/chatter.py) · blob `1ac8c42d8cbf3f2519d191e9967675bb2da165e8`
- [src/llamafactory/webui/common.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/common.py) · blob `cacf15182b8d9e7898facd26fb4c06d632a2aee7`
- [src/llamafactory/webui/components/__init__.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/__init__.py) · blob `e2c64ea739b881b0908e476343ea55e59f56e373`
- [src/llamafactory/webui/components/chatbot.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/chatbot.py) · blob `4095f8d8cd46e13f82c8e1a2384be0e8cfd2ff01`
- [src/llamafactory/webui/components/data.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/data.py) · blob `8f27bd19674735662f88ff53b267b772fcc2f44e`
- [src/llamafactory/webui/components/eval.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/eval.py) · blob `95773a8fd0a18b24047611fccc0a29c92521c4e0`
- [src/llamafactory/webui/components/export.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/export.py) · blob `9597aa61b8c5bab286200d1d235e50b655518faa`
- [src/llamafactory/webui/components/footer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/footer.py) · blob `6ee9bbce4b9f3ac24e48f911d27b78577f1f821c`
- [src/llamafactory/webui/components/infer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/infer.py) · blob `ef508cdf6eeff3d8f541100257c602b596161c6c`
- [src/llamafactory/webui/components/top.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/top.py) · blob `12275f1610acd89e2df6a765ca449c023aae38f3`
- [src/llamafactory/webui/components/train.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/components/train.py) · blob `f0ea0734bd05ae8759f069f18762f6d8bcb6afa9`
- [src/llamafactory/webui/control.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/control.py) · blob `2dbbdbd83d6f8b37e58c297a2ebde777f238d3f0`
- [src/llamafactory/webui/css.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/css.py) · blob `b7e4c3572907b4d2419b68f87513cc89db21ed06`
- [src/llamafactory/webui/engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/engine.py) · blob `eb1aa443d6130726a0791088f200ce12fdf80655`
- [src/llamafactory/webui/interface.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/interface.py) · blob `1cb989b296ccca0c7fbace473f48ed5f3176a529`
- [src/llamafactory/webui/locales.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/locales.py) · blob `874f41404886d85783cbb8cd0db4474f65464ff9`
- [src/llamafactory/webui/manager.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/manager.py) · blob `e762fa6b5e427a5b0a77e4faa7e28f413c243863`
- [src/llamafactory/webui/runner.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/webui/runner.py) · blob `096b50d59dd1f3ecca93b1a3d8db36bcb81bc0b3`
- [src/train.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/train.py) · blob `eba846a024a72853948ee2757e69b44551c63b12`
- [src/webui.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/webui.py) · blob `f13d2f26c30dd259baf6394d9b293e87a7664450`

## tests

- [tests/check_license.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/check_license.py) · blob `3680c939a38d33a98919ed65fb28d5975d21a346`
- [tests/conftest.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/conftest.py) · blob `dc1302df1bab7530f78003f052a756325bc6ae1e`
- [tests/data/processor/test_feedback.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/processor/test_feedback.py) · blob `f384d8dac0539d8d593ec517d39cc4e912541df2`
- [tests/data/processor/test_pairwise.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/processor/test_pairwise.py) · blob `628c25c63de4b36d7ca15d6ff56a02961d0fb38d`
- [tests/data/processor/test_processor_utils.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/processor/test_processor_utils.py) · blob `97d18d4b33456ee0c93bee96538bc06ee5b7b813`
- [tests/data/processor/test_supervised.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/processor/test_supervised.py) · blob `edc7f75e3d81029776634513093359af755f06f7`
- [tests/data/processor/test_unsupervised.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/processor/test_unsupervised.py) · blob `ef527ad2ef17a13585f010afcaf2ee2f69be400c`
- [tests/data/test_collator.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/test_collator.py) · blob `4c801fde627c4199297197108a56ccd0ef6909fe`
- [tests/data/test_converter.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/test_converter.py) · blob `0ceb5a661a497cd3a147b5c809009a553ef1b01b`
- [tests/data/test_formatter.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/test_formatter.py) · blob `1d9e9ef2ec83043e8f529695af7109f5aad098ce`
- [tests/data/test_loader.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/test_loader.py) · blob `f589cc85858fed309d4ecfc20ef1f64d2695d62d`
- [tests/data/test_mm_plugin.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/test_mm_plugin.py) · blob `4c4dda47fba2e922c6681b6391fb67c8c97e172d`
- [tests/data/test_moss_vl_plugin.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/test_moss_vl_plugin.py) · blob `ef9ff9ed1d58a3e20f54ebf7ac5467c099bae5e4`
- [tests/data/test_moss_vl_training_configs.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/test_moss_vl_training_configs.py) · blob `4d55732e5daf63f8f9ca5e0b2a67faaac266a4b1`
- [tests/data/test_template.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/data/test_template.py) · blob `9549f80a61647caedae8b5d673e34d3c6dcb5ea8`
- [tests/e2e/test_chat.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/e2e/test_chat.py) · blob `3ba41c97941df9b829677dc6face8878fd27c939`
- [tests/e2e/test_sglang.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/e2e/test_sglang.py) · blob `7182ed382c331c5103211688e3b9747f1427052e`
- [tests/e2e/test_train.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/e2e/test_train.py) · blob `16b7002ef798bf57bf721a4d5726a5911568e013`
- [tests/eval/test_eval_template.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/eval/test_eval_template.py) · blob `d0a477c09a9164aaeafc04d9989ebfe652bc2fc6`
- [tests/model/model_utils/test_add_tokens.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/model_utils/test_add_tokens.py) · blob `cb1c414abd3b812083b91fd77d7214e0f6b72783`
- [tests/model/model_utils/test_attention.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/model_utils/test_attention.py) · blob `075caeaee25dd4ea52f568acacb26a764d5677e6`
- [tests/model/model_utils/test_checkpointing.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/model_utils/test_checkpointing.py) · blob `2402e6fb741a15cfd23dda9cae600e26c473869c`
- [tests/model/model_utils/test_embedding.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/model_utils/test_embedding.py) · blob `b7e01e1adfdba55aae481e8f4529ef9c7c52cd07`
- [tests/model/model_utils/test_misc.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/model_utils/test_misc.py) · blob `b2c8b3bf916fe745e2ed93b68ba87d5cafa9c15a`
- [tests/model/model_utils/test_packing.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/model_utils/test_packing.py) · blob `81e0d66a5bf4397f818d1a108e7cb78b76e64708`
- [tests/model/model_utils/test_visual.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/model_utils/test_visual.py) · blob `091bb7ddcc508d787f38588203d2eed72663f70b`
- [tests/model/test_base.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/test_base.py) · blob `14afff633bc6ecd5bd9df1db55ee88f35e5fa78d`
- [tests/model/test_freeze.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/test_freeze.py) · blob `b82ec88d5ac39465fbe0862221337d49d270bf79`
- [tests/model/test_full.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/test_full.py) · blob `9058b6acf2a2db5e579fdb4ddd361d087a1fc310`
- [tests/model/test_lora.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/test_lora.py) · blob `38b6b505d0f2a9dde70e172f3a3023191fcfe9d9`
- [tests/model/test_pissa.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/model/test_pissa.py) · blob `3b6101f84be30bc99fd085b20bcee6cbc638bc7c`
- [tests/train/megatron_bridge/conftest.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/train/megatron_bridge/conftest.py) · blob `ae9f3ad2f8b25f6c42d338518a63ae5393376e57`
- [tests/train/megatron_bridge/test_config_builder.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/train/megatron_bridge/test_config_builder.py) · blob `0b20c60b272eeaf4ace05f4a200cd2ca50115245`
- [tests/train/megatron_bridge/test_dataset_export.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/train/megatron_bridge/test_dataset_export.py) · blob `671174008dbd79204b75e94bef7324b96e9e3661`
- [tests/train/megatron_bridge/test_megatron_bridge_gpu.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/train/megatron_bridge/test_megatron_bridge_gpu.py) · blob `0275792a112dcb08c9f90330ca794582304045b5`
- [tests/train/megatron_bridge/test_model_support.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/train/megatron_bridge/test_model_support.py) · blob `6d7b5bc4e786c8ad0aa827f3fba9a0d10c98b9c9`
- [tests/train/test_sft_trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/train/test_sft_trainer.py) · blob `9f6ebe418383309190b735c22dd0d61b42397370`
- [tests/version.txt](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/version.txt) · blob `702f7e0928d71abde2ec068574f63cb9bc97daea`

## tests_v1

- [tests_v1/accelerator/test_interface.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/accelerator/test_interface.py) · blob `cda01130e484e85ce07f1451dc02a76b94682155`
- [tests_v1/config/test_args_parser.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/config/test_args_parser.py) · blob `33f5824a49466165fc7156b12805006d1e8df1a4`
- [tests_v1/conftest.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/conftest.py) · blob `3d8f70a095fe306cdbc0b329466c9214c35f6da3`
- [tests_v1/core/rendering/test_rendering.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/core/rendering/test_rendering.py) · blob `fd487e9914ad615c746a8563d81e5cd588b01980`
- [tests_v1/core/test_data_engine.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/core/test_data_engine.py) · blob `aef337d433d0d00183dec3bc631649ef01267c47`
- [tests_v1/core/test_model_loader.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/core/test_model_loader.py) · blob `e354a28e861114810a81cfe85c8118214e34c3dc`
- [tests_v1/core/utils/test_batching.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/core/utils/test_batching.py) · blob `9da38ef8a626cacfa4482acb9f35cfc2b64371a6`
- [tests_v1/plugins/data_plugins/test_converter.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/data_plugins/test_converter.py) · blob `7d836477b261d6257524a1cc2faef0241bc56cf8`
- [tests_v1/plugins/model_plugins/test_chunk_loss.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/model_plugins/test_chunk_loss.py) · blob `b9a5736eabc6f4fc6f281afa2f534ae8d8946adb`
- [tests_v1/plugins/model_plugins/test_init_plugin.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/model_plugins/test_init_plugin.py) · blob `ddfb03303f97d4ceaa1e02314a5579b6a42aef05`
- [tests_v1/plugins/model_plugins/test_kernel_plugin.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/model_plugins/test_kernel_plugin.py) · blob `074b9a53d3e9ebca369b55c24b1a7a399916eee5`
- [tests_v1/plugins/model_plugins/test_peft.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/model_plugins/test_peft.py) · blob `fb2332ceff32d9b260d9a79c416b6d10ea7cb184`
- [tests_v1/plugins/model_plugins/test_quantization_plugin.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/model_plugins/test_quantization_plugin.py) · blob `019580d506239ac3b67995d815abac7d6d083ecf`
- [tests_v1/plugins/model_plugins/test_ulysses_cp.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/model_plugins/test_ulysses_cp.py) · blob `228e676f2ec5d38f35c21ea663cf2bde61bb89f6`
- [tests_v1/plugins/trainer_plugins/distributed/test_fsdp2.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/trainer_plugins/distributed/test_fsdp2.py) · blob `cf4e6718fd12b01651d00fb3a8d233d840a2a773`
- [tests_v1/plugins/trainer_plugins/distributed/test_fsdp2_weight_convert.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/trainer_plugins/distributed/test_fsdp2_weight_convert.py) · blob `a3bb0a474582ece7b183cb5ffc6eda0ee7e62616`
- [tests_v1/plugins/trainer_plugins/distributed/test_fsdpturbo_ep.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/plugins/trainer_plugins/distributed/test_fsdpturbo_ep.py) · blob `cd7b3315a14f17501e626a336e29cb277a4fdaa0`
- [tests_v1/sampler/test_cli_sampler.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/sampler/test_cli_sampler.py) · blob `16dee6d67711daa42bbb46deab470456896ef5bb`
- [tests_v1/trainers/test_dpo_loss_precision.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/trainers/test_dpo_loss_precision.py) · blob `96cbf100b533663741e0497691a531b82fce68fd`
- [tests_v1/trainers/test_fsdp2_dpo_trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/trainers/test_fsdp2_dpo_trainer.py) · blob `0d242e91a54d8fe0a532d0abbbe30f485b69ae33`
- [tests_v1/trainers/test_fsdp2_sft_trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests_v1/trainers/test_fsdp2_sft_trainer.py) · blob `30e14e05b5f30498c9667d88d8945f99bcd83172`
