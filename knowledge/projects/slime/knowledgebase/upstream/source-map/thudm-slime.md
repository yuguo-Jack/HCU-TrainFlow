---
id: thudm-slime-source-map
title: THUDM/slime source directory map
kind: source-map
engine: slime
review_level: inventory-only
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
sources: []
generated_body_sha256: 148348382cf0cb1bbf41f1b20a5d7e600f30d22fc667324cfc8a4260774bfed3
---

# THUDM/slime: fixed source directory map

Commit `a4202e0595467d9374d9a68d45a34f45c3f8d230` · ref `main`. Full paths are discoverable; listing a file does not imply its contents were read.

Use `wiki-code THUDM/slime a4202e0595467d9374d9a68d45a34f45c3f8d230 PATH` to inspect exact files, then follow callers/tests. A gitlink entry pins a child SHA, not its latest branch.

## .agents

- [.agents/skills](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.agents/skills) · blob `454b8427cd757f30dc7fdb9a325d19c399770417`

## .claude

- [.claude/skills/add-dynamic-filter/SKILL.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.claude/skills/add-dynamic-filter/SKILL.md) · blob `be8461a0edb44597e95d83f5ad02e3319f70d202`
- [.claude/skills/add-eval-dataset-config/SKILL.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.claude/skills/add-eval-dataset-config/SKILL.md) · blob `f59360687ffa342c7f2214de8fee4b3692a07236`
- [.claude/skills/add-reward-function/SKILL.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.claude/skills/add-reward-function/SKILL.md) · blob `f6ba3f9a79bf8755351de2e33a608de4a28a19de`
- [.claude/skills/add-rollout-function/SKILL.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.claude/skills/add-rollout-function/SKILL.md) · blob `c8623a135b77e787d3725211ee61034e2bcf59bb`
- [.claude/skills/add-tests-and-ci/SKILL.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.claude/skills/add-tests-and-ci/SKILL.md) · blob `000ea983b91922bfccec231a25a5ce7045737b71`
- [.claude/skills/release/SKILL.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.claude/skills/release/SKILL.md) · blob `b4fcdaa2d239e9f5e7d1caa18ef402a050f409f8`
- [.claude/skills/release/scripts/check_release.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.claude/skills/release/scripts/check_release.py) · blob `9d2cbe10fd242db9ba2f18a93283514ef67839de`
- [.claude/skills/slime-code-review-preferences/SKILL.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.claude/skills/slime-code-review-preferences/SKILL.md) · blob `cbe0eb628fda46eca379f1ed3a2b31d777457a45`

## .dockerignore

- [.dockerignore](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.dockerignore) · blob `937a820df0f139586d42b85c2bf1955f662e8595`

## .github

- [.github/ISSUE_TEMPLATE/bug_report.yml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/ISSUE_TEMPLATE/bug_report.yml) · blob `36ff4770cf1acbbd7c6f440056d847509bc61d2b`
- [.github/ISSUE_TEMPLATE/config.yml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/ISSUE_TEMPLATE/config.yml) · blob `04d024a2c2ea0f119eddf905b3e5282c1fb0c1bd`
- [.github/ISSUE_TEMPLATE/question.yml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/ISSUE_TEMPLATE/question.yml) · blob `7c9c4dac2ee9f9912f5601c73ddb58a2900eaf1a`
- [.github/workflows/bot-slash-lint.yaml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/workflows/bot-slash-lint.yaml) · blob `85ae508c268d4a3f65c24bff46a7bc1a3bec0f0b`
- [.github/workflows/conda-ci.yml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/workflows/conda-ci.yml) · blob `f698067365e98144590811b86568c65843ac4623`
- [.github/workflows/generate_github_workflows.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/workflows/generate_github_workflows.py) · blob `ee98bfcb5d6794c2c5372f835aa7e05a2542e0bf`
- [.github/workflows/pr-test.yml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/workflows/pr-test.yml) · blob `a5fb00400b3d03ef9688a44e9d64cf04eb75067e`
- [.github/workflows/pr-test.yml.j2](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/workflows/pr-test.yml.j2) · blob `d183a3d4b88e5111b2d114c433762ab4d491b219`
- [.github/workflows/pre-commit.yml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/workflows/pre-commit.yml) · blob `9c6de3c5b71bf40c95dc0d703512a4467df99650`
- [.github/workflows/release-docs.yaml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.github/workflows/release-docs.yaml) · blob `353e1df709ecf9bd17b8d13888cd06688f82df3b`

## .gitignore

- [.gitignore](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.gitignore) · blob `40dfe47ffb48b1856479be25e8b320488adce233`

## .pre-commit-config.yaml

- [.pre-commit-config.yaml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/.pre-commit-config.yaml) · blob `7d0d57ac49bace39a4a47216edb070e159844efb`

## CONTRIBUTING.md

- [CONTRIBUTING.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/CONTRIBUTING.md) · blob `839956f743b03b171fe02bfbcd749c375ee71554`

## LICENSE

- [LICENSE](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/LICENSE) · blob `456e53742c2559a96f834c77daafd58c895db5cb`

## README.md

- [README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/README.md) · blob `97b30a825b281a1a348e445f3f89f3b53e786940`

## README_zh.md

- [README_zh.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/README_zh.md) · blob `3fe91178df0df13889f6391de47d0ef2c1fe89bc`

## build_conda.sh

- [build_conda.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/build_conda.sh) · blob `f5bc72519935476f1ebcb2d384a016df6840c9be`

## docker

- [docker/Dockerfile](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/Dockerfile) · blob `f8b5440dbb39b93fe371b8e65b8e25064c98b6d1`
- [docker/Dockerfile.gb10](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/Dockerfile.gb10) · blob `2844b946b5de4e2262ff54fc7083c348e71d1ec1`
- [docker/Dockerfile.rocm](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/Dockerfile.rocm) · blob `a3d6001d3e620f7bb2c1fc0a65f03e14216da240`
- [docker/Dockerfile.rocm_MI350-5](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/Dockerfile.rocm_MI350-5) · blob `f6974d69b446623ac1c363a668166a2df0cb42b8`
- [docker/Dockerfile_20250810_9a48ba0.rocm](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/Dockerfile_20250810_9a48ba0.rocm) · blob `176c1ee61b2a34e9fecdaf206302ec5ad890ee1a`
- [docker/Dockerfile_20250810_c22f55b.rocm](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/Dockerfile_20250810_c22f55b.rocm) · blob `2bc78501266226d34c4a1a8fd399a8f505fa3f43`
- [docker/NOTES_GB10.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/NOTES_GB10.md) · blob `4901b5a7904a43aac013d09a35faf3862d80f7aa`
- [docker/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/README.md) · blob `3e35cee00e929b541c6b905ebd2da3b7bbb7b031`
- [docker/amd_patch/latest/amd_megatron_fused_kernels_init.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/amd_patch/latest/amd_megatron_fused_kernels_init.patch) · blob `f6efca346dcebcd52ac8a7a611e6c7c02a074a59`
- [docker/amd_patch/latest/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/amd_patch/latest/megatron.patch) · blob `c840133cefd62824cb5610d15a1847e7ff28aff1`
- [docker/amd_patch/latest/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/amd_patch/latest/sglang.patch) · blob `990c2e628994734ef61edb3ad47c4ae0b3943f2f`
- [docker/amd_patch/sglv0.5.0rc0/amd_megatron_fused_kernels_init.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/amd_patch/sglv0.5.0rc0/amd_megatron_fused_kernels_init.patch) · blob `f6efca346dcebcd52ac8a7a611e6c7c02a074a59`
- [docker/amd_patch/sglv0.5.0rc0/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/amd_patch/sglv0.5.0rc0/megatron.patch) · blob `c840133cefd62824cb5610d15a1847e7ff28aff1`
- [docker/amd_patch/sglv0.5.0rc0/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/amd_patch/sglv0.5.0rc0/sglang.patch) · blob `990c2e628994734ef61edb3ad47c4ae0b3943f2f`
- [docker/cuda-compat.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/cuda-compat.sh) · blob `ba374935c83de6f463ba5bd672be6cf9d7702444`
- [docker/entrypoint.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/entrypoint.sh) · blob `253376e99a5be741fd37fa17107eb19e264a1144`
- [docker/justfile](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/justfile) · blob `947e9675e9aed0eb8422d7dae5cd0912c033f6a9`
- [docker/npu_patch/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/npu_patch/README.md) · blob `db93b67633f897c2466f5cb116b6cc7abd45e3fc`
- [docker/npu_patch/megatron-bridge.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/npu_patch/megatron-bridge.patch) · blob `3817097f4041aff5f6ecd1c96386ae6fe8b25dc5`
- [docker/npu_patch/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/npu_patch/megatron.patch) · blob `7687827db6b860a4e514434e9de72b93b2488aba`
- [docker/npu_patch/mindspeed.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/npu_patch/mindspeed.patch) · blob `0cf1c848403f0834d90a3243458e4d90091c3e55`
- [docker/npu_patch/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/npu_patch/sglang.patch) · blob `b684d3c0eb017fd65bbd8dae977c2498d4d2fe0f`
- [docker/npu_patch/slime.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/npu_patch/slime.patch) · blob `7b6222170403ea18b72a389168db88460335f7e5`
- [docker/patch/gb10/cuda_profiler_api.h](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/gb10/cuda_profiler_api.h) · blob `276b80b656fdc29638b4ef5769ac77887e1d94b8`
- [docker/patch/gb10/patch_sgl_kernel.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/gb10/patch_sgl_kernel.py) · blob `a6dc3bbebf5d4860c088139c31989989a1ffdbe3`
- [docker/patch/gb10/sgl-kernel-arch.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/gb10/sgl-kernel-arch.patch) · blob `a507e04c09f083943f114e8371c71ffcbf0604fe`
- [docker/patch/latest/megatron-sglang-aligned.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/latest/megatron-sglang-aligned.patch) · blob `8a688aa6fe3c034069eeac29eeceebb09bbd1738`
- [docker/patch/latest/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/latest/megatron.patch) · blob `5a9a98515efe09a58e660596b9d44b6ab94d2f89`
- [docker/patch/latest/sglang-deterministic.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/latest/sglang-deterministic.patch) · blob `b85c90d3efafaafb11c5006096b7e53a417ffcdc`
- [docker/patch/latest/sglang-pull_weights.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/latest/sglang-pull_weights.patch) · blob `afd9db51771cfde352bffebd43f36e9da99e2dd0`
- [docker/patch/latest/sglang-release_hicache.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/latest/sglang-release_hicache.patch) · blob `d66af453e92120c0399b438778bad5dc7969555b`
- [docker/patch/latest/sglang-top_p.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/latest/sglang-top_p.patch) · blob `24a3e4630b68d8107ac642752ab0fd0af15ca36f`
- [docker/patch/latest/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/latest/sglang.patch) · blob `53e58256d357c50f62ac1cc4674dbee1f6088437`
- [docker/patch/v0.5.0rc0-cu126/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.0rc0-cu126/megatron.patch) · blob `95d59d284a05a21f464ea5afff9260f87fb8ea11`
- [docker/patch/v0.5.0rc0-cu126/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.0rc0-cu126/sglang.patch) · blob `990c2e628994734ef61edb3ad47c4ae0b3943f2f`
- [docker/patch/v0.5.12.post1/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.12.post1/megatron.patch) · blob `4b4c74d28e0144b144989ba1dc8a726125bc80ce`
- [docker/patch/v0.5.12.post1/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.12.post1/sglang.patch) · blob `861f2524606c5558165b3cf2fa3672e8b83a3bfe`
- [docker/patch/v0.5.15.post1/megatron-sglang-aligned.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.15.post1/megatron-sglang-aligned.patch) · blob `8a688aa6fe3c034069eeac29eeceebb09bbd1738`
- [docker/patch/v0.5.15.post1/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.15.post1/megatron.patch) · blob `f732021de498ceb8ecf7f4b0123f37108626ebb7`
- [docker/patch/v0.5.15.post1/sglang-deterministic.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.15.post1/sglang-deterministic.patch) · blob `ad31f7a454eded660430dfdb596f288c83746dda`
- [docker/patch/v0.5.15.post1/sglang-pull_weights.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.15.post1/sglang-pull_weights.patch) · blob `f308c4819ccf9b0f1a2c784211dc4d486664cab8`
- [docker/patch/v0.5.15.post1/sglang-release_hicache.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.15.post1/sglang-release_hicache.patch) · blob `c8f6f9473fd3bc5929f9ec885f63a8a0a37a7850`
- [docker/patch/v0.5.15.post1/sglang-top_p.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.15.post1/sglang-top_p.patch) · blob `16898a9e7ac827da1694ef684727bce8c2c40bd2`
- [docker/patch/v0.5.15.post1/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.15.post1/sglang.patch) · blob `967585629a284dd5c89b735207477e19f8dd02e3`
- [docker/patch/v0.5.21/megatron-sglang-aligned.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.21/megatron-sglang-aligned.patch) · blob `8a688aa6fe3c034069eeac29eeceebb09bbd1738`
- [docker/patch/v0.5.21/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.21/megatron.patch) · blob `5a9a98515efe09a58e660596b9d44b6ab94d2f89`
- [docker/patch/v0.5.21/sglang-deterministic.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.21/sglang-deterministic.patch) · blob `b85c90d3efafaafb11c5006096b7e53a417ffcdc`
- [docker/patch/v0.5.21/sglang-pull_weights.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.21/sglang-pull_weights.patch) · blob `afd9db51771cfde352bffebd43f36e9da99e2dd0`
- [docker/patch/v0.5.21/sglang-release_hicache.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.21/sglang-release_hicache.patch) · blob `d66af453e92120c0399b438778bad5dc7969555b`
- [docker/patch/v0.5.21/sglang-top_p.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.21/sglang-top_p.patch) · blob `24a3e4630b68d8107ac642752ab0fd0af15ca36f`
- [docker/patch/v0.5.21/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.21/sglang.patch) · blob `53e58256d357c50f62ac1cc4674dbee1f6088437`
- [docker/patch/v0.5.5.post1/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.5.post1/megatron.patch) · blob `cca054d1e6c5220dcd4a0dd460cba17f370d2cbe`
- [docker/patch/v0.5.5.post1/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.5.post1/sglang.patch) · blob `5e0e72150d99b4dce5067748aee260b161817a40`
- [docker/patch/v0.5.6/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.6/megatron.patch) · blob `9d0d6011ce3c6e9a211625adebc40d084b1b3f24`
- [docker/patch/v0.5.6/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.6/sglang.patch) · blob `78bf161bc4f34fe6585f9245e31a990db2461989`
- [docker/patch/v0.5.7/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.7/megatron.patch) · blob `6d2a233949dffb96d167b3e5c5c4c23443c9b62a`
- [docker/patch/v0.5.7/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.7/sglang.patch) · blob `8c2b46fb739b40256b2e9c70eeb01b50d47380d7`
- [docker/patch/v0.5.9/megatron.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.9/megatron.patch) · blob `2e6ae436b1f1375d5dd7f87ba989ec951ae0efe1`
- [docker/patch/v0.5.9/sglang.patch](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/patch/v0.5.9/sglang.patch) · blob `e9145702e1a6c506cd1b10abf4871d5d6c080fc6`
- [docker/version.txt](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docker/version.txt) · blob `b42e1abb0ac8cf71630cba6267087e234c9bc9b1`

## docs

- [docs/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/README.md) · blob `ff1faddcb528a9c29a3b4ff5aa40202d1efd94d0`
- [docs/_static/css/custom_log.css](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/css/custom_log.css) · blob `2e4ce75ddaff67bc88e4babecbbf705aa68e0357`
- [docs/_static/css/experiment.css](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/css/experiment.css) · blob `dac529fcf0cc6bf7275e295f4b359943cbd5204b`
- [docs/_static/css/readthedocs.css](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/css/readthedocs.css) · blob `aca6649b436a35cf39b2c924ce2f74ed2cdc8b90`
- [docs/_static/image/arch.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/arch.png) · blob `b809bd3ffee17e4c361c73a9cca454a849c3a8e8`
- [docs/_static/image/blogs/release_v0.1.0/cuda_vmm.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/blogs/release_v0.1.0/cuda_vmm.png) · blob `5bc852b9ed901dbadd6c4156ebad3f6c10d3164e`
- [docs/_static/image/blogs/release_v0.1.0/overrall.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/blogs/release_v0.1.0/overrall.png) · blob `ff0293ceb696fa8252dbd3626753069b02121b94`
- [docs/_static/image/logo.ico](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/logo.ico) · blob `78153d1e2f773763690ca0d60efb4328059f576b`
- [docs/_static/image/logo.jpg](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/logo.jpg) · blob `c1257d72b355bbee4172b77c07713bd968deba4f`
- [docs/_static/image/rl-world-en.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/rl-world-en.png) · blob `cad2dfb8fe49ace500c185590c2dfd42bd63286e`
- [docs/_static/image/rl-world-zh.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/rl-world-zh.png) · blob `7eadc0669f1a0877cabe5adccff81f5aef0f8a84`
- [docs/_static/image/sglang_config.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/sglang_config.png) · blob `c4cde43ab238a708c8debd3eb40c71297ee5d9d9`
- [docs/_static/image/trace.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/image/trace.png) · blob `847f4009cbcb735719ecb3181266bb039cf22a9d`
- [docs/_static/js/experiment-diagrams.js](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/js/experiment-diagrams.js) · blob `4c42af62f8f035ad91445f140b78d3b1b3e2f37c`
- [docs/_static/js/experiment-engine.js](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/js/experiment-engine.js) · blob `840462d694ab444cc749d0760bbfb78ebc3a537c`
- [docs/_static/js/experiment-reader.js](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/js/experiment-reader.js) · blob `7c4f1f2575b5f133637cbab037d8e1e378fd4435`
- [docs/_static/js/experiment-ui.js](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/js/experiment-ui.js) · blob `88bf644acea4b528ee58e38b1b970ab3bdaae2aa`
- [docs/_static/js/lang-toggle.js](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_static/js/lang-toggle.js) · blob `9618e126a804090004860d113970d6cf2e4a10a0`
- [docs/_templates/experiment.html](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/_templates/experiment.html) · blob `b99bc920a8f621eb22ea056cf19cd99a7e66bd9a`
- [docs/build.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/build.sh) · blob `4b896cf4d9d205bb2b828f47b2ad1ef9e28664bf`
- [docs/build_all.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/build_all.sh) · blob `27283f426156a1cb2392322bbd607bbefaabd0e2`
- [docs/conf.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/conf.py) · blob `171fcbcac15ae5459351b462c7c9e76c158b869b`
- [docs/en/advanced/arch-support-beyond-megatron.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/arch-support-beyond-megatron.md) · blob `d704a4267ceb3f4a91f34a3fb410cb3de0b91cf9`
- [docs/en/advanced/delta-weight-sync.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/delta-weight-sync.md) · blob `59d4b7b08cc0a4253dad8e56639651c32169d170`
- [docs/en/advanced/external-rollout-engines.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/external-rollout-engines.md) · blob `9a64c506424ead43f26c4092def7aa3efa033c26`
- [docs/en/advanced/fault-tolerance.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/fault-tolerance.md) · blob `2aa92a58a99937cd52be6653346559ad8ea425d1`
- [docs/en/advanced/low-precision.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/low-precision.md) · blob `5e365845d4bb5b349ec85087545b207b04da7aee`
- [docs/en/advanced/megatron-config.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/megatron-config.md) · blob `831082d64ebcfa634e788a13a64d23a9126308a4`
- [docs/en/advanced/observability.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/observability.md) · blob `3a4941dbc2a05ae94716801a57253724292aaf44`
- [docs/en/advanced/on-policy-distillation.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/on-policy-distillation.md) · blob `d5932b230f54a8353e8c503e6d4dd5dae386f306`
- [docs/en/advanced/parallelism-memory.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/parallelism-memory.md) · blob `932d5a743659f6862914ca58fbca78fde468d459`
- [docs/en/advanced/pd-disaggregation.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/pd-disaggregation.md) · blob `085e1657b9ad6071d851e11a51ea7da684e59763`
- [docs/en/advanced/policy-mismatch.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/policy-mismatch.md) · blob `0e6b9d0743eddebfc1eabb25758c94b0fd9f1474`
- [docs/en/advanced/reproducibility.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/reproducibility.md) · blob `cf4ae67d3d1afd2576854915a5f2f139113a4ee6`
- [docs/en/advanced/rl-systems.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/rl-systems.md) · blob `5ddd76d4fe0bb0f560c83b779edc3ba8e05b8a7c`
- [docs/en/advanced/rollout-scheduling.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/rollout-scheduling.md) · blob `a6d09fcec2f29cd8c8aee5528d70badc8c7f4625`
- [docs/en/advanced/sglang-config.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/sglang-config.md) · blob `a9bcc2128baa35b191a9fba73a2249606991cf67`
- [docs/en/advanced/speculative-decoding.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/speculative-decoding.md) · blob `2aa0263b34ae5d097710f2afbb83de363572a00c`
- [docs/en/advanced/straw.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/straw.md) · blob `148c855623c489770c11442a9b4e1f5d6fb4c326`
- [docs/en/blogs/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/blogs/index.rst) · blob `ebf917be05985903fb24669717d8f68fa2112ca6`
- [docs/en/blogs/introducing_slime.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/blogs/introducing_slime.md) · blob `6f9dae7c2902d754f1bc52793b4a5dd4fc018166`
- [docs/en/blogs/release_v0.1.0.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/blogs/release_v0.1.0.md) · blob `2a1b93e6e82eaad7577a8a68ed31ad9e4b1d6ae0`
- [docs/en/developer_guide/ci.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/developer_guide/ci.md) · blob `69d2641d1af00f86b2bcbfccc3f82069364447b0`
- [docs/en/developer_guide/debug.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/developer_guide/debug.md) · blob `e09a3751cda4e9ff0bbcc2ad3bd1c266fb9f552a`
- [docs/en/developer_guide/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/developer_guide/index.rst) · blob `7c056e85d6f0f71284f5ef82b94db6faece98713`
- [docs/en/developer_guide/install_flashqla.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/developer_guide/install_flashqla.md) · blob `ee728ce372007152d913dd6594d57a2db0af02e6`
- [docs/en/developer_guide/profiling.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/developer_guide/profiling.md) · blob `93b8ea5b39b908b54c41718dee28aeebe6e816af`
- [docs/en/developer_guide/trace.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/developer_guide/trace.md) · blob `604efa6564c620a10374253fb0150f2b25cf6a01`
- [docs/en/examples/agents/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/examples/agents/index.rst) · blob `afe1df707c8827435faf6174c244041e7fcd66b9`
- [docs/en/examples/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/examples/index.rst) · blob `e923877e622ec782439c49b49d561a761db5e2b4`
- [docs/en/examples/multimodal/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/examples/multimodal/index.rst) · blob `42a45630ba3a03f3ed425339f8b2366cdec08d72`
- [docs/en/examples/qwen3-4b-base-openhermes.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/examples/qwen3-4b-base-openhermes.md) · blob `ceda8ba83538bab9716c1eb6e4c270a5cae3d3c3`
- [docs/en/examples/workflows/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/examples/workflows/index.rst) · blob `d80da17ba72f1a5ef04ac5240b8ae78ca1c0bca8`
- [docs/en/get_started/agent.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/get_started/agent.md) · blob `f45b88e04b711465a2b33d10b99da299ca67002d`
- [docs/en/get_started/customization.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/get_started/customization.md) · blob `f1d15b39adb966f7c32482387079fb12a850f766`
- [docs/en/get_started/experiment-guide.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/get_started/experiment-guide.md) · blob `cc1b6ef528f659e71e9906bfb9bfac4427ec322d`
- [docs/en/get_started/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/get_started/index.rst) · blob `f791e3b05e18ad4aabe384bcfdd0b29efc7e9e13`
- [docs/en/get_started/qa.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/get_started/qa.md) · blob `2344e4b1c962fec2345af177135342f9709f5a00`
- [docs/en/get_started/quick_start.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/get_started/quick_start.md) · blob `989f31fcb4ff5a0eac5ac32ddb47305d74800a9e`
- [docs/en/get_started/usage.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/get_started/usage.md) · blob `b17cadd31b22d38665e04c8454bd08e19ee17dd2`
- [docs/en/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/index.rst) · blob `e5a3e0246d1258ef5b3388466c39f8d4a0de43f3`
- [docs/en/library.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/library.rst) · blob `e643d1399ed2b88d88cb4ce0cb1d461d54c6f28e`
- [docs/en/operations/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/operations/index.rst) · blob `a83c35c33ca6fe87eeb1dbb21ee42b6bb622f079`
- [docs/en/platform_support/amd_tutorial.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/platform_support/amd_tutorial.md) · blob `8597ac17012233986dc7872bb18770b777c9355f`
- [docs/en/platform_support/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/platform_support/index.rst) · blob `123abab1700f18051cedba393f1998c84cbef3d8`
- [docs/en/rollout/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/rollout/index.rst) · blob `7a6868678f6bcb7d82def03b06f47795ed5e50b4`
- [docs/en/training/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/training/index.rst) · blob `1d3290cfb977df4130a840835e09e9bf6b6127f7`
- [docs/requirements.txt](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/requirements.txt) · blob `e67e7366956ae76342c84c6b8e5c8fe0bec34a10`
- [docs/serve.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/serve.sh) · blob `ae739852824d483138459e73e8f706c995e327b5`
- [docs/tests/experiment.test.cjs](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/tests/experiment.test.cjs) · blob `e51050f9b471ec97b4f063da82c545edd6be7f20`
- [docs/tests/requirements.txt](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/tests/requirements.txt) · blob `c94eb78cbe25f0dee66a628a02c3e4cad9775686`
- [docs/tests/test_browser.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/tests/test_browser.py) · blob `fa26a814e3d5b45629c89e9bf7217e9b5ac1630f`
- [docs/zh/advanced/arch-support-beyond-megatron.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/arch-support-beyond-megatron.md) · blob `4e3c3c87699c75126ae2b6bc77bf8e124cf3b645`
- [docs/zh/advanced/delta-weight-sync.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/delta-weight-sync.md) · blob `f384f475e0d7d91b3efe9695d81899eb30c2a689`
- [docs/zh/advanced/external-rollout-engines.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/external-rollout-engines.md) · blob `172ac5348c04d988d0057df8ecb398399e58d4d1`
- [docs/zh/advanced/fault-tolerance.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/fault-tolerance.md) · blob `dd9f3b8be1b3cb88df657c17197f5d619a24e6eb`
- [docs/zh/advanced/low-precision.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/low-precision.md) · blob `d61e0833f2b5076b4014103952e40d58e2571306`
- [docs/zh/advanced/megatron-config.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/megatron-config.md) · blob `d873ab1bc12aec52c2265c8f555e13812774a762`
- [docs/zh/advanced/observability.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/observability.md) · blob `01a10f35cdcab03229d6f8b6ef47f17537a1b879`
- [docs/zh/advanced/on-policy-distillation.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/on-policy-distillation.md) · blob `1f0c368460f069b30d5d6faef9128e48ac360ac2`
- [docs/zh/advanced/parallelism-memory.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/parallelism-memory.md) · blob `eca273d37d1a70beb19cb4be250ac7f809019525`
- [docs/zh/advanced/pd-disaggregation.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/pd-disaggregation.md) · blob `d9d9e2ddb89f371b21323b530556a452698db0c8`
- [docs/zh/advanced/policy-mismatch.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/policy-mismatch.md) · blob `62d112924da39cb81b4b11a406797728bebd68ea`
- [docs/zh/advanced/reproducibility.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/reproducibility.md) · blob `65b93607ff7d9f843763fc361e3a957217ced48e`
- [docs/zh/advanced/rl-systems.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/rl-systems.md) · blob `ea492dfe40e7fb987ccf84c940c6436b4023944b`
- [docs/zh/advanced/rollout-scheduling.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/rollout-scheduling.md) · blob `fc9d76af17fa77910ccc5b8beda3ced44a321058`
- [docs/zh/advanced/sglang-config.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/sglang-config.md) · blob `ba11f558d2986156d90fa103e84abeed49b7a9d7`
- [docs/zh/advanced/speculative-decoding.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/speculative-decoding.md) · blob `e98c14ef441f6dbe51b985c1c5d7b0354c0624ce`
- [docs/zh/advanced/straw.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/advanced/straw.md) · blob `a9e99c7a7677032d6605393c9f18b80c10b8c5cd`
- [docs/zh/blogs/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/blogs/index.rst) · blob `7c591c62e9cef1c5f6b96eb85e282de01d4618fa`
- [docs/zh/blogs/introducing_slime.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/blogs/introducing_slime.md) · blob `5c779e394aeeed65a69be0734d87fa889374925f`
- [docs/zh/blogs/release_v0.1.0.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/blogs/release_v0.1.0.md) · blob `ff95a7e3cbe73a9b172b6ff9972452ea4edc51ca`
- [docs/zh/developer_guide/ci.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/developer_guide/ci.md) · blob `29935132b0fb5653b650160c06bd47f0ae3f05ca`
- [docs/zh/developer_guide/debug.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/developer_guide/debug.md) · blob `2e8674cbbe6ea00db0af220fe832365789be3646`
- [docs/zh/developer_guide/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/developer_guide/index.rst) · blob `8105d2a3536d5dee0d6a71615f9441c2119988df`
- [docs/zh/developer_guide/install_flashqla.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/developer_guide/install_flashqla.md) · blob `f2cf9f71960d789e903004fca967bb49f6d0382f`
- [docs/zh/developer_guide/profiling.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/developer_guide/profiling.md) · blob `11609ec555ed9d5fb67367877095ebf8da61a16e`
- [docs/zh/developer_guide/trace.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/developer_guide/trace.md) · blob `ab2afe016dc4ec3866d7d153d04cfaf27b8087a0`
- [docs/zh/examples/agents/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/examples/agents/index.rst) · blob `21d523a1e9b37504c3a5a0b6d3c6c4dd7f8d8952`
- [docs/zh/examples/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/examples/index.rst) · blob `c6b682453bd7bf98a08ffe94973ef3e9373c6c0d`
- [docs/zh/examples/multimodal/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/examples/multimodal/index.rst) · blob `cb31acbc400abbcc004c4c26d304e3d286282af0`
- [docs/zh/examples/qwen3-4b-base-openhermes.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/examples/qwen3-4b-base-openhermes.md) · blob `31cc0ad87652d5a2ba499d948535315fedf443a6`
- [docs/zh/examples/workflows/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/examples/workflows/index.rst) · blob `9c972be16dc1ed784ad6f0bdd91ac98c95ddfd2c`
- [docs/zh/get_started/agent.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/get_started/agent.md) · blob `975ac6812fb9ddf229aef024cd6ca9ad55e8a814`
- [docs/zh/get_started/customization.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/get_started/customization.md) · blob `8977f472eba06a8337ca16ad54c466a277075643`
- [docs/zh/get_started/experiment-guide.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/get_started/experiment-guide.md) · blob `0285c4b271bdaa44294910081290874aa66ce1ff`
- [docs/zh/get_started/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/get_started/index.rst) · blob `6607e672f805a4d75c6b134a0f8de285da098c9c`
- [docs/zh/get_started/qa.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/get_started/qa.md) · blob `05c73890bc7faa19fbdf68cdd4032486edca0683`
- [docs/zh/get_started/quick_start.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/get_started/quick_start.md) · blob `7a39bffae32d1cf7ff1bee4b1ab5d8b464331d91`
- [docs/zh/get_started/usage.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/get_started/usage.md) · blob `6364678b920770fb654f27c973dd99ca7b3e1a03`
- [docs/zh/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/index.rst) · blob `b160b3aeba9b93a34b26d9a076ca9f5af670e5f0`
- [docs/zh/library.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/library.rst) · blob `ca72078d07ae839ed866ccb5834f415879c208b2`
- [docs/zh/operations/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/operations/index.rst) · blob `1135e6165350e936c8d7a3165281aae6ab06f6cb`
- [docs/zh/platform_support/amd_tutorial.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/platform_support/amd_tutorial.md) · blob `c142fe6b4f60d5d25920d5c87707c22c468098de`
- [docs/zh/platform_support/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/platform_support/index.rst) · blob `114ec647dc2bab2ce6be0b4b8166230f91c225ee`
- [docs/zh/rollout/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/rollout/index.rst) · blob `53be08e28dae77dca5b0d1a685a89dccc1976257`
- [docs/zh/training/index.rst](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/zh/training/index.rst) · blob `1b5a15afbf109088ef0a8bfdbe0853c77d42e38f`

## examples

- [examples/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/README.md) · blob `14265bef2eb3ded1a16ab492511b0a81b9d2e518`
- [examples/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [examples/coding_agent_rl/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/README.md) · blob `f8117b61a83702f06c1cf8974407f9a0ecda8ee6`
- [examples/coding_agent_rl/check_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/check_rollout.py) · blob `1d066dec59940551aa787a1fda59839280c51408`
- [examples/coding_agent_rl/generate.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/generate.py) · blob `3b8beb004a1c5b712aad859cffcb4d688f92e156`
- [examples/coding_agent_rl/prepare_mimo.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/prepare_mimo.py) · blob `36fe2c7a8d1e03e97f49a77dbd0147caba5c399f`
- [examples/coding_agent_rl/prepare_sunabako_images.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/prepare_sunabako_images.py) · blob `dd7bab964e6687eb028829d32521b36f19b53779`
- [examples/coding_agent_rl/requirements-sunabako.txt](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/requirements-sunabako.txt) · blob `bcec212b28635d5c2e68a640f8cc1d6c8dcd13bc`
- [examples/coding_agent_rl/run_qwen38_27b_fully_async.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/run_qwen38_27b_fully_async.sh) · blob `c13a8e9df043799752362e51418356b0464cb175`
- [examples/coding_agent_rl/sandbox.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/sandbox.py) · blob `acf5df984a4f4e7e9fc7b4c71d8cdbd4daa2b9e9`
- [examples/coding_agent_rl/sunabako_sandbox.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/sunabako_sandbox.py) · blob `a9b3a230b597dd71ce866abb817b21e78ac4a28f`
- [examples/coding_agent_rl/swe.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/coding_agent_rl/swe.py) · blob `b29af2659b8dacd982fad128b305d6141c2be523`
- [examples/delta_weight_sync/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/delta_weight_sync/README.md) · blob `60d826153ba3f7ccf2b3f8edb35935a8115ca4a9`
- [examples/delta_weight_sync/run-glm4.7-30B-A3B-delta.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/delta_weight_sync/run-glm4.7-30B-A3B-delta.sh) · blob `8d7227bfd2e93d83647382187e800ea7b1319822`
- [examples/eval_multi_task/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/eval_multi_task/README.md) · blob `0bf61ec7294e7f5dfb44710f02eade5f4465fb8e`
- [examples/eval_multi_task/multi_task.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/eval_multi_task/multi_task.sh) · blob `d780ee82123a60c53b6f4c01c4b0161bb741a69b`
- [examples/eval_multi_task/multi_task.yaml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/eval_multi_task/multi_task.yaml) · blob `37cdc34066cd12777fc8632da353b9ea1b510bf2`
- [examples/eval_multi_task/requirements_ifbench.txt](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/eval_multi_task/requirements_ifbench.txt) · blob `78f13fac47749ca3ec7ad4f7c1af9197d7274ac9`
- [examples/fully_async/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/fully_async/README.md) · blob `c6c4f912d8883f4fcc3ca866f37d84a18544a2c2`
- [examples/fully_async/run-qwen3-4B-fully_async.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/fully_async/run-qwen3-4B-fully_async.sh) · blob `ac17b40589448f7f07c77c4debdfc5bdc69924b3`
- [examples/fully_async/run-qwen3.5-9B-fully_async.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/fully_async/run-qwen3.5-9B-fully_async.sh) · blob `245daba8a0d7e3eecc383dfce0d6ee89792e0c9d`
- [examples/geo3k_vlm/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm/README.md) · blob `a073e03f1078a404f80e71f11bdfd15160ca9a68`
- [examples/geo3k_vlm/fsdp_vs_megatron.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm/fsdp_vs_megatron.png) · blob `5c32e414b84f4ea43b94c55f0f2081abfd0b407c`
- [examples/geo3k_vlm/run_geo3k_qwen35.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm/run_geo3k_qwen35.sh) · blob `3c8b59fb3fc266c5ce9870b31c5b6c9c3789e1c4`
- [examples/geo3k_vlm_multi_turn/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/README.md) · blob `dad14e354f729c6d68ce2886bb2c42b346d58b31`
- [examples/geo3k_vlm_multi_turn/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/__init__.py) · blob `526e3ae7c68160bbb147ce00121c876b6e76ec70`
- [examples/geo3k_vlm_multi_turn/base_env.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/base_env.py) · blob `05d9632b37e001d83630c40c600f4c095f053d20`
- [examples/geo3k_vlm_multi_turn/env_geo3k.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/env_geo3k.py) · blob `3fdf0cfd56374e65ede779f9f2ac766ef8689919`
- [examples/geo3k_vlm_multi_turn/geo3k_vlm_multi_turn_config.yaml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/geo3k_vlm_multi_turn_config.yaml) · blob `ad2dd6feff40f805006ea76a5f2253bcff4ceaf9`
- [examples/geo3k_vlm_multi_turn/geo3k_vlm_multi_turn_reward.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/geo3k_vlm_multi_turn_reward.png) · blob `88851bb461bda64034846c98c3f37e29fd76ebe8`
- [examples/geo3k_vlm_multi_turn/rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/rollout.py) · blob `f0cc076c5db37e77b9f0965d6c8f34a2dd86f99d`
- [examples/geo3k_vlm_multi_turn/rollout_experiment_result_megatron.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/rollout_experiment_result_megatron.png) · blob `dd249de2952016e460aa946cd28b7bd3f757d848`
- [examples/geo3k_vlm_multi_turn/run_geo3k_vlm_multi_turn.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/geo3k_vlm_multi_turn/run_geo3k_vlm_multi_turn.py) · blob `c6486cf0db733a783e513706fc8d43d926b8ed51`
- [examples/multi_agent/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/multi_agent/README.md) · blob `f613e519fb983e583d178881d06a46d1a9759e86`
- [examples/multi_agent/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/multi_agent/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [examples/multi_agent/agent_system.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/multi_agent/agent_system.py) · blob `e83b12b369a6882f2d205ac52c4c473aa3da21df`
- [examples/multi_agent/prompts.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/multi_agent/prompts.py) · blob `a79047258fd8ac597a9799a3a8e0bfed241902ac`
- [examples/multi_agent/rollout_with_multi_agents.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/multi_agent/rollout_with_multi_agents.py) · blob `4b57d74881e29450ec06378eeb533625cc50ee35`
- [examples/multi_agent/run-qwen3-30B-A3B-multi-agent.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/multi_agent/run-qwen3-30B-A3B-multi-agent.sh) · blob `7f8449ad1fe56d501c438b2eaa6b8f040d5e32ad`
- [examples/on_policy_distillation/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/on_policy_distillation/README.md) · blob `0f05c4bd40df9a9c161a716afb36b1f8d2e5910a`
- [examples/on_policy_distillation/run-qwen3-4B-opd-megatron.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/on_policy_distillation/run-qwen3-4B-opd-megatron.sh) · blob `69f410dbbf4acfa05d87e0b4be7b2525694870b5`
- [examples/on_policy_distillation/run-qwen3-4B-opd.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/on_policy_distillation/run-qwen3-4B-opd.sh) · blob `a31d1c285124ec0112443ece1d2cf4888367263d`
- [examples/retool/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/retool/README.md) · blob `73a0e736219e5a832ac0c0e9a9f442e3351be23a`
- [examples/retool/generate_with_retool.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/retool/generate_with_retool.py) · blob `ebb5c4f1a64baa1e1569952df96f6e1634de3989`
- [examples/retool/requirements.txt](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/retool/requirements.txt) · blob `154747336b3c93587090f7eb16ca5b63cb99d3cb`
- [examples/retool/retool_qwen3_4b_rl.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/retool/retool_qwen3_4b_rl.sh) · blob `cfbde5234670de7a328c4d8e15e2bccbadabfb6b`
- [examples/retool/retool_qwen3_4b_sft.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/retool/retool_qwen3_4b_sft.sh) · blob `d204a34fce012609e7a39bea9682fb7fbd99a699`
- [examples/retool/rl_data_preprocess.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/retool/rl_data_preprocess.py) · blob `548b74468576bc1ace53aed90a587f8845bd7990`
- [examples/retool/sft_data_processing.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/retool/sft_data_processing.py) · blob `96790af1e9c73f30cf657fae78da6251334c9ec3`
- [examples/retool/tool_sandbox.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/retool/tool_sandbox.py) · blob `cdf68aa020714d206791d4fb257e45999f0cfdc6`
- [examples/search-r1/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/README.md) · blob `ba166f88e4b24cd38e705a6838a8a0c65e135203`
- [examples/search-r1/README_zh.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/README_zh.md) · blob `be48ef22514928e76a622760560351e2a738fcf9`
- [examples/search-r1/generate_with_search.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/generate_with_search.py) · blob `ae0f18dd15be8fd78715cc1be43b1df637032b9d`
- [examples/search-r1/google_search_server.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/google_search_server.py) · blob `3ddfff8142e9d8464217baf40074be6c4f0b9ed7`
- [examples/search-r1/local_dense_retriever/download.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/local_dense_retriever/download.py) · blob `6fe554936fafc57ada63198fadd4f30af0de8b8a`
- [examples/search-r1/local_dense_retriever/retrieval_server.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/local_dense_retriever/retrieval_server.py) · blob `f8733582ea00d729014e063f452b223f7298e4d2`
- [examples/search-r1/local_search_server.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/local_search_server.py) · blob `0e5c814a7bca2c7376432d31bcbc9b61784c98b7`
- [examples/search-r1/qa_em_format.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/qa_em_format.py) · blob `330f9c9256909c71e4f87ed0e34656f829c08eab`
- [examples/search-r1/run_qwen3_4B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/search-r1/run_qwen3_4B.sh) · blob `43f24d4bfc24c3567e1747caed49e98e013f1eef`
- [examples/strands_sglang/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/strands_sglang/README.md) · blob `bebb196a44021c35be445df1a7f7f325b411f6bb`
- [examples/strands_sglang/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/strands_sglang/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [examples/strands_sglang/generate_with_strands.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/strands_sglang/generate_with_strands.py) · blob `d62ee79780112369ab0e5876892a7180c8916b1a`
- [examples/strands_sglang/strands_qwen3_4b.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/strands_sglang/strands_qwen3_4b.sh) · blob `74586b0bc468e68c5d536da5f7e1b530e5127e5a`
- [examples/strands_sglang/subprocess_interpreter.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/strands_sglang/subprocess_interpreter.py) · blob `b6e04937672b09879e0cd23d1618581e669d674b`
- [examples/tau-bench/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/tau-bench/README.md) · blob `f9e3879800775b58700003ba22b45db0c669ee62`
- [examples/tau-bench/generate_with_tau.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/tau-bench/generate_with_tau.py) · blob `42e69cd9738326bcf73ed04f84de3dc45a3361f8`
- [examples/tau-bench/openai_tool_adapter.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/tau-bench/openai_tool_adapter.py) · blob `b580f28b20534d77e26fd7f41b98034ff9140d2b`
- [examples/tau-bench/run_qwen3_4B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/tau-bench/run_qwen3_4B.sh) · blob `5ed4bfa8803985c0e9f347ef54fc3dd009e5d355`
- [examples/tau-bench/sglang_tool_parser.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/tau-bench/sglang_tool_parser.py) · blob `ea4f380ba1aec8dc84f30c7a2ef5af030954dd87`
- [examples/tau-bench/tau1_mock.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/tau-bench/tau1_mock.py) · blob `74ed424a75c5a56c852d76a06f1a8a3f61e55c6b`
- [examples/tau-bench/token_delta.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/tau-bench/token_delta.py) · blob `b78023d8cec3a38959711baa5512b99f3161240b`
- [examples/tau-bench/trainable_agents.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/tau-bench/trainable_agents.py) · blob `effc5d7a661ce328c40bedb3e9a39a594dc07735`
- [examples/train_infer_mismatch_helper/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/train_infer_mismatch_helper/README.md) · blob `e9430711483c109f3617fbc2d55960e1cb637578`
- [examples/train_infer_mismatch_helper/mis.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/train_infer_mismatch_helper/mis.py) · blob `3bbf5cf26edb36eb6581627ea64ff3542e5726e0`
- [examples/train_infer_mismatch_helper/mis.yaml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/train_infer_mismatch_helper/mis.yaml) · blob `bd285979edb2ab47cfafe57d62bfa44903b0b745`
- [examples/train_infer_mismatch_helper/run-qwen3-4b-mis.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/examples/train_infer_mismatch_helper/run-qwen3-4b-mis.sh) · blob `84ecd1c711978fba862cf53bf58ba38ff7dbe970`

## imgs

- [imgs/arch.png](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/imgs/arch.png) · blob `b809bd3ffee17e4c361c73a9cca454a849c3a8e8`

## pyproject.toml

- [pyproject.toml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/pyproject.toml) · blob `28cf1de9dd3543fcc4b68df4b689992462929a63`

## requirements.txt

- [requirements.txt](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/requirements.txt) · blob `e3089b0d58d9411e51b1f762f6ef3b69fa54a88b`

## scripts

- [scripts/low_precision/run-kimi-k2-Thinking-int4.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/low_precision/run-kimi-k2-Thinking-int4.sh) · blob `7fde109d1489c81559b4a5096f1d6eb93218b0a8`
- [scripts/low_precision/run-qwen3-235B-A22B-int4.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/low_precision/run-qwen3-235B-A22B-int4.sh) · blob `788d6dce9ed04c85b4ad1d6b7ccfb48e43ebd924`
- [scripts/low_precision/run-qwen3-30B-A3B-int4.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/low_precision/run-qwen3-30B-A3B-int4.sh) · blob `e11b7b28f4b750e2addfb845bc455895ee7d243f`
- [scripts/low_precision/run-qwen3-30b-a3b-fp8.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/low_precision/run-qwen3-30b-a3b-fp8.sh) · blob `fbdf31b296c88a144b12a917bc45feab89b71da8`
- [scripts/low_precision/run-qwen3-4b-fp8.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/low_precision/run-qwen3-4b-fp8.sh) · blob `589819fc9f0273e0b29cefbd3af2dda47d12e472`
- [scripts/models/deepseek-v3.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/deepseek-v3.sh) · blob `8c50d2c9405ce2553b4174ad541cc10b02b4669b`
- [scripts/models/glm4-32B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/glm4-32B.sh) · blob `a9c3e00616248e0807dbaebb3e876d897aee8494`
- [scripts/models/glm4-9B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/glm4-9B.sh) · blob `d1e02936549a00ebb81b3a6d0c87d5901e69d61f`
- [scripts/models/glm4.5-106B-A12B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/glm4.5-106B-A12B.sh) · blob `6bab15b77f70d4863e32246590db555cb371ee6a`
- [scripts/models/glm4.5-355B-A32B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/glm4.5-355B-A32B.sh) · blob `8aca21fd47566cf408e289b1cdd3c3ff69b1f9a1`
- [scripts/models/glm4.7-30B-A3B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/glm4.7-30B-A3B.sh) · blob `696eb9bcfe54724dde2b2a2fd9152c2ac64f4767`
- [scripts/models/glm5-744B-A40B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/glm5-744B-A40B.sh) · blob `0afd676a7e6fcbc47b4775a87ba0ecacafcd9d56`
- [scripts/models/glm5.2-744B-A40B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/glm5.2-744B-A40B.sh) · blob `bd39c9359475d37438dc36d5c376b49272929035`
- [scripts/models/glm5.3-flash-300B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/glm5.3-flash-300B.sh) · blob `cf373d67effb7deecd86405f3adeec9ef332b937`
- [scripts/models/kimi-k2-thinking.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/kimi-k2-thinking.sh) · blob `b7fceda5913f48aaea287733b1b4ed447d445ae7`
- [scripts/models/kimi-k2.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/kimi-k2.sh) · blob `eafb7acadd11b2d470265ca845000b943e87cee3`
- [scripts/models/llama3.1-8B-Instruct.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/llama3.1-8B-Instruct.sh) · blob `0815b3e0a343bf644e7b8629aec6743f53a12b39`
- [scripts/models/llama3.2-3B-Instruct-amd.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/llama3.2-3B-Instruct-amd.sh) · blob `654de5a38652675918c5669d2f9375d40f7b2779`
- [scripts/models/llama3.2-3B-Instruct.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/llama3.2-3B-Instruct.sh) · blob `ff50130c8a706af8c0560b848e43cd0dad63261d`
- [scripts/models/mimo-7B-rl.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/mimo-7B-rl.sh) · blob `22366935f9913e125f8976b66998d2e60006ee2c`
- [scripts/models/minimax-m2.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/minimax-m2.sh) · blob `390eb03fab51f77ff2491d47f28550dec719d957`
- [scripts/models/moonlight.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/moonlight.sh) · blob `bcce99892a790eee372880d40024939c7b141800`
- [scripts/models/qwen2.5-0.5B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen2.5-0.5B.sh) · blob `66d5b29a024d52dfc6ca9cfe0bb3aa18391089cf`
- [scripts/models/qwen2.5-1.5B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen2.5-1.5B.sh) · blob `b046a95c66b4015ff9212ef1aa5d964bd8f07a12`
- [scripts/models/qwen2.5-32B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen2.5-32B.sh) · blob `26b49845a417baa9ff74c1b1eb3db0dc61eaa49c`
- [scripts/models/qwen2.5-3B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen2.5-3B.sh) · blob `9da5a9e0339ffba6d162acd8c4dffa88a263778f`
- [scripts/models/qwen2.5-7B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen2.5-7B.sh) · blob `eba912b1d7c93e242ba7d4909583916815be1a67`
- [scripts/models/qwen3-0.6B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-0.6B.sh) · blob `f484ec9519bc7615d2e4a3497ad1292c65e4dc6e`
- [scripts/models/qwen3-1.7B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-1.7B.sh) · blob `7435996337e97b341ec93160ac7caf510ed93a0d`
- [scripts/models/qwen3-14B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-14B.sh) · blob `11b9377da005fb482a651d4aa531d05cfdeebd7d`
- [scripts/models/qwen3-235B-A22B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-235B-A22B.sh) · blob `1f6635526539b310a2162be4b57f440b6a258009`
- [scripts/models/qwen3-30B-A3B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-30B-A3B.sh) · blob `dfab8682abb2489e24c67748581399000247e030`
- [scripts/models/qwen3-32B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-32B.sh) · blob `e7407e327c9ca416f999db35d8e1dad25e6619b9`
- [scripts/models/qwen3-4B-Instruct-2507.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-4B-Instruct-2507.sh) · blob `67d13c0c82384d5eafc361a0a52202aef0cef7a1`
- [scripts/models/qwen3-4B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-4B.sh) · blob `51f9e47581e8d113711e8f5026f6d27d908ce8be`
- [scripts/models/qwen3-8B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-8B.sh) · blob `fc573adb37bb42f0837aabb6cdbb9525f44a581f`
- [scripts/models/qwen3-next-80B-A3B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3-next-80B-A3B.sh) · blob `74e4e02ed84b485e18ef8eb2785c16f70cecbece`
- [scripts/models/qwen3.5-0.8B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3.5-0.8B.sh) · blob `c235c4c1f67b455d6519a636d3e62cebecbe034d`
- [scripts/models/qwen3.5-27B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3.5-27B.sh) · blob `ffa6ab178745c5fe197f123fd48c2ef6ec2f55dc`
- [scripts/models/qwen3.5-35B-A3B-vl.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3.5-35B-A3B-vl.sh) · blob `381d577723daa9b902e3422883134d647210ee0a`
- [scripts/models/qwen3.5-35B-A3B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3.5-35B-A3B.sh) · blob `c3cb7219bba7f4df25ee800dfbefc781d3f6c204`
- [scripts/models/qwen3.5-4B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3.5-4B.sh) · blob `18bea47c9c41d2ec0b5afe1b64337d57e4fc820f`
- [scripts/models/qwen3.5-9B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/models/qwen3.5-9B.sh) · blob `cca6d6c29dca73b025c3e572687d0575398133fe`
- [scripts/run-glm4.7-30B-A3B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-glm4.7-30B-A3B.sh) · blob `ea2dbc49eba19fccc779b4f631a2f3253fa1b5b0`
- [scripts/run-glm4.7-355B-A32B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-glm4.7-355B-A32B.sh) · blob `abb5dbbd5cfd5443b6ab483fa65fb1164cc4eab2`
- [scripts/run-glm5.3-744B-A40B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-glm5.3-744B-A40B.sh) · blob `1c49acd562dd6a45c44f39b32b139e198b7dd623`
- [scripts/run-glm5.3-flash-300B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-glm5.3-flash-300B.sh) · blob `94db4dea4f6cbbada10d389f3546871b85180e41`
- [scripts/run-kimi-k2-Thinking.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-kimi-k2-Thinking.sh) · blob `63b05ef2c026ef90410558524cb93d9803be703f`
- [scripts/run-minimax-m2.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-minimax-m2.sh) · blob `ddfc07ad1dc13c47c343e55d4645337c6e2d2260`
- [scripts/run-qwen2.5-0.5B-gb10-smoke.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-qwen2.5-0.5B-gb10-smoke.sh) · blob `7a379b9614d288d1bd0fc1e8e725da18ca526433`
- [scripts/run-qwen3-30B-A3B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-qwen3-30B-A3B.sh) · blob `13f5871b53c1ed1042d879e5a8492fa42f532513`
- [scripts/run-qwen3-4B-amd.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-qwen3-4B-amd.sh) · blob `04bef49dc277c7f436960a74ea4fdb4ff0cb5fd0`
- [scripts/run-qwen3-4B-base-sft.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-qwen3-4B-base-sft.sh) · blob `a66fd1eee19ff89a7bbde4428cddc4e0c7cf6d02`
- [scripts/run-qwen3-4B-reproducibility.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-qwen3-4B-reproducibility.sh) · blob `7e21b9eb80e15f069dfbc91c6fa418f2a0c0efc1`
- [scripts/run-qwen3-4B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-qwen3-4B.sh) · blob `d20f78623dfe24f2a07c0e37aca30298322d8d9f`
- [scripts/run-qwen3.5-27B.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-qwen3.5-27B.sh) · blob `93223b67c1d82904663c21d38cb6508342ef87bf`
- [scripts/run-qwen3.5-35B-A3B-sft.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/scripts/run-qwen3.5-35B-A3B-sft.sh) · blob `2ddb3e7e24d6b47d31a70088d1c0865b6e07c496`

## setup.py

- [setup.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/setup.py) · blob `56fb62d9802bd5330f70a936af86a5cc3527866c`

## slime

- [slime/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/agent/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/__init__.py) · blob `1048d52b8a7c1f70fdec3483219ffbe8c75e46f3`
- [slime/agent/adapters/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/adapters/__init__.py) · blob `692a3b09a58b19f4f663cf21a7ca3b4525090e71`
- [slime/agent/adapters/anthropic.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/adapters/anthropic.py) · blob `64903b2f1702796e257a21d63dbc8ac0e83bea5a`
- [slime/agent/adapters/common.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/adapters/common.py) · blob `2d3c31becee5e2fae454c31be56973920a5d13b3`
- [slime/agent/adapters/openai.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/adapters/openai.py) · blob `485266c38dd76bfe82c3d423cf3f33a522c3d06a`
- [slime/agent/adapters/responses.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/adapters/responses.py) · blob `4bd2dbeb7b3e37cf9b4d3a7d32077ee829bcee9c`
- [slime/agent/aiohttp_threaded.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/aiohttp_threaded.py) · blob `ad5fa0ccb841e0b47c3be1ffafa3f7ba1d3d8bdb`
- [slime/agent/harness/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/harness/__init__.py) · blob `caac42b06679134c9b271c5ade6e05db29045f61`
- [slime/agent/harness/claude_code.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/harness/claude_code.py) · blob `3f40a47c69992b89691ddafb8ed799ad8b2fec2d`
- [slime/agent/harness/codex.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/harness/codex.py) · blob `e797dd9e487fdea5eadd903abb2f23183e766709`
- [slime/agent/harness/common.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/harness/common.py) · blob `ed4dae183fe26ff19a71c83ebb8f5125898be8cb`
- [slime/agent/harness/compaction.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/harness/compaction.py) · blob `0df00ea38e34d31487c0525b78cc96670797516f`
- [slime/agent/parsing.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/parsing.py) · blob `56bc85a4bc78634c18f59eb9c5c630cd4343550a`
- [slime/agent/sandbox.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/sandbox.py) · blob `e0902324f7862f9c6fc66a90b24850bae45f8ac6`
- [slime/agent/trajectory.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/agent/trajectory.py) · blob `3cf81476edcb0f724a8afa03250850f5ae49f8bd`
- [slime/backends/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/__init__.py) · blob `8b137891791fe96927ad78e64b0aad7bded08bdc`
- [slime/backends/megatron_utils/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/__init__.py) · blob `55372a8641487dafd01b4a7e51fa1e226710f6cc`
- [slime/backends/megatron_utils/actor.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/actor.py) · blob `f4851ef5cf68b74ed833284117d122adaeac146e`
- [slime/backends/megatron_utils/alignment/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/alignment/__init__.py) · blob `682d8170be9696def3c57473c38ecef535da6ce9`
- [slime/backends/megatron_utils/alignment/deepgemm_forward.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/alignment/deepgemm_forward.py) · blob `0f493158e0ee9144aa2041731e3cdaf19441b3a0`
- [slime/backends/megatron_utils/alignment/deepgemm_moe_forward.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/alignment/deepgemm_moe_forward.py) · blob `25bf5970710de57caa1fca543a9f45fbe123ba09`
- [slime/backends/megatron_utils/alignment/deterministic_route_kernels.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/alignment/deterministic_route_kernels.py) · blob `1bd2127a1b9804a56c378ab3982a4c78d9b48499`
- [slime/backends/megatron_utils/alignment/env.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/alignment/env.py) · blob `5a249d2828865a688afe67bca62aa37c9c3270a2`
- [slime/backends/megatron_utils/alignment/layerwise_alignment.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/alignment/layerwise_alignment.py) · blob `a9eaf477603da203d5fdef97f9b7bfa1e507e428`
- [slime/backends/megatron_utils/arguments.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/arguments.py) · blob `ab8e569a44bb7778b77c7b0b0d668ad9bf058c73`
- [slime/backends/megatron_utils/checkpoint.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/checkpoint.py) · blob `4b0e372eb04761b7bae1e4ef13549d70fe05874b`
- [slime/backends/megatron_utils/ci_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/ci_utils.py) · blob `e6ce784ca2a37bed71091f6223217e7333b7d4c0`
- [slime/backends/megatron_utils/cp_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/cp_utils.py) · blob `cddc361d7b4798751cdd3f68f3bcbcbd719be4aa`
- [slime/backends/megatron_utils/data.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/data.py) · blob `3737453bdbe0770c60c8ff2d2e694f3417bc79d6`
- [slime/backends/megatron_utils/hf_checkpoint_saver.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_checkpoint_saver.py) · blob `c961518fa43cd7cdfcac842c31f22e2267fe61eb`
- [slime/backends/megatron_utils/hf_to_megatron/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_to_megatron/__init__.py) · blob `a43ed8653e5654b12cc743d9d2b3f3b5c122159d`
- [slime/backends/megatron_utils/hf_to_megatron/common.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_to_megatron/common.py) · blob `da51d46b4330b7e282836e5ac2af772f372bfb83`
- [slime/backends/megatron_utils/hf_to_megatron/deepseek.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_to_megatron/deepseek.py) · blob `e7f8fbe379c4ac59096061abbf23d148b35c505a`
- [slime/backends/megatron_utils/hf_to_megatron/glm.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_to_megatron/glm.py) · blob `a7e973394fb1103dfcada0d2aed1badab519ed1f`
- [slime/backends/megatron_utils/hf_to_megatron/glm5_next.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_to_megatron/glm5_next.py) · blob `73ff4f572b8235e12c8e224b65fe5665809865bf`
- [slime/backends/megatron_utils/hf_to_megatron/qwen.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_to_megatron/qwen.py) · blob `29cebc7602a1daacc4264c1086b1139c532f428e`
- [slime/backends/megatron_utils/hf_to_megatron/qwen3_5.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_to_megatron/qwen3_5.py) · blob `2e616255a4ad6c8937c07444202f7fca2bea7407`
- [slime/backends/megatron_utils/hf_to_megatron/qwen3_next.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/hf_to_megatron/qwen3_next.py) · blob `f14d4222756f6167656da5ec7222b56f1329f4e1`
- [slime/backends/megatron_utils/initialize.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/initialize.py) · blob `50081f82f9d6ab645c2e0a840372e61737a740d4`
- [slime/backends/megatron_utils/kernels/fp8_kernel.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/kernels/fp8_kernel.py) · blob `0cfa6042695fc73d00019e3391aed650f80103d2`
- [slime/backends/megatron_utils/kernels/int4_qat/fake_int4_quant_cuda.cu](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/kernels/int4_qat/fake_int4_quant_cuda.cu) · blob `f7df09987e63cd4fba5115d3c95de8e92395b858`
- [slime/backends/megatron_utils/kernels/int4_qat/setup.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/kernels/int4_qat/setup.py) · blob `2db4683f9854d492ce800cfb49abaa71cef62310`
- [slime/backends/megatron_utils/loss.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/loss.py) · blob `917a2b66986fba917614a07d4d81a55ed0f9d0b1`
- [slime/backends/megatron_utils/megatron_to_hf/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/__init__.py) · blob `88a94c2372917a8e85c3a042314c5410cb6eaf50`
- [slime/backends/megatron_utils/megatron_to_hf/deepseekv3.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/deepseekv3.py) · blob `205b025556e9a7e8a936ee57d0eed00cb2431cb6`
- [slime/backends/megatron_utils/megatron_to_hf/glm4.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/glm4.py) · blob `cb82edac99a044a2f908498d1e2e4aaf76a6de64`
- [slime/backends/megatron_utils/megatron_to_hf/glm4moe.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/glm4moe.py) · blob `33a64e6e8f0fe5d22045c996b83e1fe45c8c807c`
- [slime/backends/megatron_utils/megatron_to_hf/glm5_next.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/glm5_next.py) · blob `14aa296a72aeec5b867ab4614b0fad55762e71f8`
- [slime/backends/megatron_utils/megatron_to_hf/llama.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/llama.py) · blob `6d89cb868358aa38b9a29261e6803debf16bd8cf`
- [slime/backends/megatron_utils/megatron_to_hf/mimo.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/mimo.py) · blob `5efafb29befcdac1b0f2d361ff35e50e62c6c3b5`
- [slime/backends/megatron_utils/megatron_to_hf/minimax_m2.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/minimax_m2.py) · blob `3701e30f2f433ada5dbbc08b083bdf3b517802ad`
- [slime/backends/megatron_utils/megatron_to_hf/processors/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/processors/__init__.py) · blob `6efe6bdadfb4fc57ecb8eb940ff9b9e87a570d78`
- [slime/backends/megatron_utils/megatron_to_hf/processors/padding_remover.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/processors/padding_remover.py) · blob `ada08a6a8b62696f2cdc13398db2169d496ca339`
- [slime/backends/megatron_utils/megatron_to_hf/processors/quantizer_compressed_tensors.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/processors/quantizer_compressed_tensors.py) · blob `5f953f91791952c44ccf653b24bd1fbb6967b735`
- [slime/backends/megatron_utils/megatron_to_hf/processors/quantizer_fp8.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/processors/quantizer_fp8.py) · blob `9e50fa8974a8a4bd3e9a46041f19365e1f89886c`
- [slime/backends/megatron_utils/megatron_to_hf/qwen2.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/qwen2.py) · blob `f7b72935cf512ed9aab70faa03f7c0458acd2e4f`
- [slime/backends/megatron_utils/megatron_to_hf/qwen3_5.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/qwen3_5.py) · blob `2829ff254e98e636e2ff372a9e2406a8ac8fecd8`
- [slime/backends/megatron_utils/megatron_to_hf/qwen3_next.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/qwen3_next.py) · blob `f12f31195f0fa4cad8968c37383085d3cbe9bd28`
- [slime/backends/megatron_utils/megatron_to_hf/qwen3_vl.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/qwen3_vl.py) · blob `97c5bc7ced849d7afc438d3f6717014987a87ab9`
- [slime/backends/megatron_utils/megatron_to_hf/qwen3moe.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/megatron_to_hf/qwen3moe.py) · blob `9f5b5b81a63e1a4311a5fbebefc3b7d1552c6886`
- [slime/backends/megatron_utils/memory.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/memory.py) · blob `e39b3256baaaf554d1acdac71625b571ba606cc7`
- [slime/backends/megatron_utils/misc_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/misc_utils.py) · blob `f101111d683f739b16be972a88da097b00cb2501`
- [slime/backends/megatron_utils/model.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/model.py) · blob `1d208dc73fe3da2573d34577128171a7760ab7bd`
- [slime/backends/megatron_utils/model_provider.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/model_provider.py) · blob `80fea81ddf015ea87d0e0bc1a313a65bea95578f`
- [slime/backends/megatron_utils/server/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/server/__init__.py) · blob `53b132ab0fafeff62e0d512bc8b90aaf8f1cdc38`
- [slime/backends/megatron_utils/server/arguments.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/server/arguments.py) · blob `32c9ba6b6619519a720ad27eb741e6db1034631c`
- [slime/backends/megatron_utils/server/logprob_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/server/logprob_utils.py) · blob `3772056dbddc1d34b4cbd18b8ce817b3eb874c43`
- [slime/backends/megatron_utils/server/megatron_server.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/server/megatron_server.py) · blob `d086a5f39307a694735ee133c9e99fbd8cc910c0`
- [slime/backends/megatron_utils/sglang.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/sglang.py) · blob `b72d9802f154c7302b0f76e780cbc30eb15ab459`
- [slime/backends/megatron_utils/stateless_adam.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/stateless_adam.py) · blob `4c49ab92b682591c5d8ca97791badcae37374845`
- [slime/backends/megatron_utils/transformer_engine.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/transformer_engine.py) · blob `9f22401cfe971c5270c3943738cbca8e8e349a40`
- [slime/backends/megatron_utils/update_weight/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/__init__.py) · blob `dc40d630e53a00ccfb899cdf696de2e730a96c84`
- [slime/backends/megatron_utils/update_weight/common.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/common.py) · blob `d13ed44420add866c32446d70ba0fb8382fab6aa`
- [slime/backends/megatron_utils/update_weight/expert_routing.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/expert_routing.py) · blob `520613553b8d11e62bb66f9fa373d649da7cc5ba`
- [slime/backends/megatron_utils/update_weight/hf_weight_iterator_direct.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/hf_weight_iterator_direct.py) · blob `3afa4bafea1d206bdc621db334afd6b937be63a0`
- [slime/backends/megatron_utils/update_weight/update_weight_from_disk.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/update_weight_from_disk.py) · blob `d9bd74b23119fcc4883916bfe6ab1075b5032e26`
- [slime/backends/megatron_utils/update_weight/update_weight_from_disk_delta.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/update_weight_from_disk_delta.py) · blob `6c3d33ab7dbeaf781e62e75b26d4085f26740eef`
- [slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py) · blob `f1e2fa153e2a27fdd1210bfc1005444d40d2a20f`
- [slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py) · blob `dd06316b37992ee31d78875b04552e35bce2a479`
- [slime/backends/sglang_utils/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/__init__.py) · blob `1a15621488c7086ab0cec0a7187a2cfb7ae66949`
- [slime/backends/sglang_utils/arguments.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/arguments.py) · blob `81dc52b3ce3a021a44bc0cba6264324e173dddb6`
- [slime/backends/sglang_utils/deployment.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/deployment.py) · blob `3ed2eca0338245d90bcfee5d7feb0d9a20bf9a4e`
- [slime/backends/sglang_utils/disaggregation.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/disaggregation.py) · blob `87492f591c62e4c1320958225bf4b8cef9aa2009`
- [slime/backends/sglang_utils/engine_group.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/engine_group.py) · blob `1da05c4d223ca64497136610c4eda1498f8d2c2e`
- [slime/backends/sglang_utils/external.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/external.py) · blob `41efc86fb49c4930749c8c96b7ea44282e4acd79`
- [slime/backends/sglang_utils/jit_kernels/csrc/gemm/glm5_router_gemm.cuh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/jit_kernels/csrc/gemm/glm5_router_gemm.cuh) · blob `fc972c060c688d3c24211305ffc5f257801c2ae6`
- [slime/backends/sglang_utils/runtime.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/runtime.py) · blob `b8031fa7c48a31cd546915c5096f6a02e7a37110`
- [slime/backends/sglang_utils/server_control.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/server_control.py) · blob `60a598f9b02f82effbd61b79237e09d549c53f63`
- [slime/backends/sglang_utils/sglang_config.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/sglang_config.py) · blob `3504e5593c5db175028ec060ac4cb4b866eaf469`
- [slime/backends/sglang_utils/sglang_engine.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/sglang_utils/sglang_engine.py) · blob `32a5ba9561d119cf071960f8a5e708983e195f84`
- [slime/data/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/__init__.py) · blob `7bc880e115bd3b346d711d23c60b50f25e0f3fb2`
- [slime/data/archive.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/archive.py) · blob `0850911ba1c3244e380107d15045575026ca55c7`
- [slime/data/batch_builder.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/batch_builder.py) · blob `3e178b7007c14b3874172789d3ff19af4dc327a5`
- [slime/data/checkpoint.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/checkpoint.py) · blob `03b1eede3e7c61cce7a6841bda812fdc77e4fde0`
- [slime/data/codec.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/codec.py) · blob `a42fee477fea05db090c883506767cf4a420722a`
- [slime/data/data_source.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/data_source.py) · blob `96e8a308bfe556778deb6d97cbb357b10e5425d4`
- [slime/data/queue_data_source.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/queue_data_source.py) · blob `3913338cb3f53dad1c835a99e3525939fd607694`
- [slime/data/rewind.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/rewind.py) · blob `e1e053461f8e18672797b93c4602fb4a478f62c2`
- [slime/data/sample_metadata.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/sample_metadata.py) · blob `fba8f479e71738279501c488e34d6bf53d2f70b6`
- [slime/data/tensor.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/tensor.py) · blob `9baa19ad0de50bf326d442617121bae09fe32c32`
- [slime/data/transport.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/transport.py) · blob `b47746c7e42f4bcda032e892781cd39ce39158a0`
- [slime/observability/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/__init__.py) · blob `3dab479228218908bf5cc0f84b6da523df7cca1d`
- [slime/observability/logging_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/logging_utils.py) · blob `2ae2a222ce607cb6a42caa27f72b8996f42fab74`
- [slime/observability/metric_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/metric_utils.py) · blob `46e42d73b0df51060307410fb00e602d3cde3901`
- [slime/observability/profile_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/profile_utils.py) · blob `68569bac8997f900f1d1dfe79f3cc4f6f8c38929`
- [slime/observability/rollout_data_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/rollout_data_utils.py) · blob `06f9f387f92ccab386e0ad46280ffd0b2cb5ae1f`
- [slime/observability/rollout_metrics.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/rollout_metrics.py) · blob `2482fa2302d3898256c253289e8e02c38d70b5e7`
- [slime/observability/tensorboard_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/tensorboard_utils.py) · blob `250864636c4873d8c21b48811b33a5317476ec20`
- [slime/observability/timer.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/timer.py) · blob `b0a89a53892dc9ee0a4eb65de66f8b33bb090d42`
- [slime/observability/trace_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/trace_utils.py) · blob `7fef1d1b99c247747b0f3f87d4cc9cc49a8766c5`
- [slime/observability/train_data_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/train_data_utils.py) · blob `bf1372570821f5b47cefaacdc2d9ff53efb6b87f`
- [slime/observability/train_metric_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/train_metric_utils.py) · blob `07ddd931c5e3fb3147ed8bb86e25bf9c676a478b`
- [slime/observability/wandb_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/observability/wandb_utils.py) · blob `093be4d3518f398cf725f87660b6a1945a3c82b4`
- [slime/ray/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/ray/actor_group.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/actor_group.py) · blob `ce6e6d03955416f65fbe928e85534268ec258b7e`
- [slime/ray/placement_group.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/placement_group.py) · blob `bbee464c9034b641502031e881b20d405abb1385`
- [slime/ray/ray_actor.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/ray_actor.py) · blob `e44322a7117710a486500ad6c3531c79716ebc09`
- [slime/ray/rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/rollout.py) · blob `07c83ab439b074ec2359833a172b5bb50f7af365`
- [slime/ray/serving.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/serving.py) · blob `b7e979b49e924c80b54d15dda1bd083fa21fcc36`
- [slime/ray/train_actor.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/train_actor.py) · blob `e91bc5a2cd95df829ca77b2594e88edd38625c3f`
- [slime/ray/training_recovery.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/training_recovery.py) · blob `5f706c9f088bc19a584ed029313f1f2673927584`
- [slime/ray/utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/ray/utils.py) · blob `6275058f5b26865bcf6a04b77aadfeaf13c38605`
- [slime/rollout/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/rollout/base_types.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/base_types.py) · blob `012d5c52bd67b5e21ef5c68cab3c3b09d51b4b26`
- [slime/rollout/filter_hub/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/filter_hub/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/rollout/filter_hub/base_types.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/filter_hub/base_types.py) · blob `c6aeae60998a787a01b39845492d07dde7643a6a`
- [slime/rollout/filter_hub/dynamic_sampling_filters.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/filter_hub/dynamic_sampling_filters.py) · blob `5e074a3873085036fe07a3184de9f3de6890512d`
- [slime/rollout/forge_load.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/forge_load.py) · blob `4f4aef7ec678a05760596b2c786e144149ccd684`
- [slime/rollout/fully_async_distributed.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/fully_async_distributed.py) · blob `7192036fbd15e63c713751a9341f3ff5d4b7129d`
- [slime/rollout/fully_async_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/fully_async_rollout.py) · blob `7a4ed8d13d6df8eb87cb557898a62466a29c3b89`
- [slime/rollout/on_policy_distillation.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/on_policy_distillation.py) · blob `eb52a0821de0fa4b47548ec5763698997507cc75`
- [slime/rollout/rm_hub/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/rm_hub/__init__.py) · blob `a2739fbec763ad28cead5b205c27f50bf14a5d07`
- [slime/rollout/rm_hub/deepscaler.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/rm_hub/deepscaler.py) · blob `39d4de383a1bdce9fc2558455469d41ab5bf99eb`
- [slime/rollout/rm_hub/f1.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/rm_hub/f1.py) · blob `ed98553f7b372e17947f1f3850f7d4b83a5178d7`
- [slime/rollout/rm_hub/gpqa.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/rm_hub/gpqa.py) · blob `affb7a22ad888ae9734a9cbc9c584dc1b31dd6d6`
- [slime/rollout/rm_hub/ifbench.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/rm_hub/ifbench.py) · blob `fc31d43eb83fafecb75ca8582b3e5405b705a7cd`
- [slime/rollout/rm_hub/math_dapo_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/rm_hub/math_dapo_utils.py) · blob `915c3aa480b1f9812c18fd3255b5c03e774a81f2`
- [slime/rollout/rm_hub/math_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/rm_hub/math_utils.py) · blob `fe4a8009551d74ea9c7a71476c46c562a4b50930`
- [slime/rollout/sample_hooks.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/sample_hooks.py) · blob `e72638ec9bc20846a97e8195cb0f1d9502a02ceb`
- [slime/rollout/sft_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/sft_rollout.py) · blob `4df55ff08da822c43afb2e48d84cbff650022f21`
- [slime/rollout/sglang_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/sglang_rollout.py) · blob `9ee9778bfd31c6d9061141f82986089ef931ddd9`
- [slime/rollout/sglang_streaming_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/sglang_streaming_rollout.py) · blob `911ff3ba269b08bfdaa7cdd667c4687a1be570d6`
- [slime/rollout/sleep_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/sleep_rollout.py) · blob `563b4138d0fd953713620151310a20031c95d914`
- [slime/rollout/streaming_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/rollout/streaming_utils.py) · blob `42793f471f14f6674212a8a51faefc2ea84cd4e9`
- [slime/utils/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/__init__.py) · blob `0745576620155d995c66f31f3d223d48b8e8b99f`
- [slime/utils/accelerator/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/accelerator/__init__.py) · blob `98127eacd6e4413cea949e2560d1f85085a64481`
- [slime/utils/accelerator/base.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/accelerator/base.py) · blob `9d760c619e2d57843112ecaaedda491117a106a3`
- [slime/utils/accelerator/cuda.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/accelerator/cuda.py) · blob `c9fca2afe0b39aeb7a9897559aa2a92185381e16`
- [slime/utils/accelerator/musa.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/accelerator/musa.py) · blob `62b398dfaa2d3f2e967978d1546a92df5594ed96`
- [slime/utils/accelerator/npu.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/accelerator/npu.py) · blob `5fc613e22b3925f2c41ab88bab7b898f848a07f3`
- [slime/utils/accelerator/supa.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/accelerator/supa.py) · blob `534604d427f5c83878f57aea0f9f346b2c4fad13`
- [slime/utils/accelerator/torch_accelerator.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/accelerator/torch_accelerator.py) · blob `d961ebe3d8d215ebf29f19bff40c7c600b732c06`
- [slime/utils/arguments.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/arguments.py) · blob `683f925ab68ae72ceb8757b196e718263270718b`
- [slime/utils/async_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/async_utils.py) · blob `26a752431c4485ed9fedd24836ff71414ffbd7d4`
- [slime/utils/cleanup.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/cleanup.py) · blob `df057f530d16c128978e290faacddb3b22e782f0`
- [slime/utils/data.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/data.py) · blob `bc7c855b3e5129aa0fb42c1a415e5ca86a2016b8`
- [slime/utils/disk_delta.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/disk_delta.py) · blob `7907a82171dfd6e0decd0aa644c6db1d80152241`
- [slime/utils/distributed_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/distributed_utils.py) · blob `af97bc14daa84f10bcbeeb3624e18708cb02a1fe`
- [slime/utils/dp_schedule.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/dp_schedule.py) · blob `1735fad3b48cd52ada98912ff2440481beaebf64`
- [slime/utils/eval_config.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/eval_config.py) · blob `f45f2be08662748d1f0ec44f5eabbc623212a3fa`
- [slime/utils/external_utils/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/external_utils/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/utils/external_utils/command_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/external_utils/command_utils.py) · blob `656bc4a8500334f560c4118148932f32c8fc3ba0`
- [slime/utils/external_utils/typer_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/external_utils/typer_utils.py) · blob `ece4f5fd9f96dd56532890f3a3bbde5e0d4bca6b`
- [slime/utils/flops_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/flops_utils.py) · blob `7ac90fe8309f560ee375fec29c81962aee420206`
- [slime/utils/health_monitor.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/health_monitor.py) · blob `3e4af2d77dbf1e0b060c1caf70d4596963ccba1d`
- [slime/utils/http_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/http_utils.py) · blob `20d327a54622743b20fcbf8fdc66ba562b489359`
- [slime/utils/mask_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/mask_utils.py) · blob `51cb43c0b9988283028a1a73d651ac23dd3e7d95`
- [slime/utils/memory_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/memory_utils.py) · blob `4bcb6759bfa0d5894a1485a66f7efd24abf13b25`
- [slime/utils/misc.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/misc.py) · blob `090845569cfba6bf8c845017dec4653038f32728`
- [slime/utils/model_config.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/model_config.py) · blob `b25d56a5658f3c980144e93535ddc8d51a8d7d5a`
- [slime/utils/ppo_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/ppo_utils.py) · blob `c5f28878d39dca159725bbc0d7905aaf1ede4bee`
- [slime/utils/processing_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/processing_utils.py) · blob `fb652e73d0fbf3d73ce9355e5e960c6f32d5aad2`
- [slime/utils/reloadable_process_group.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/reloadable_process_group.py) · blob `6f2978acac3577b26eb124fdff48dd10fa04738d`
- [slime/utils/rocm_checkpoint_writer.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/rocm_checkpoint_writer.py) · blob `7a8a1be2cee9840380bd3fcf05af32b703a33fe8`
- [slime/utils/routed_experts.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/routed_experts.py) · blob `798bea78ec85190f6936f3c24d9f11c1d64bb164`
- [slime/utils/routing_replay.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/routing_replay.py) · blob `7d0b7627ec952d82248ea96ae86fdb2957d159b9`
- [slime/utils/score_centering.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/score_centering.py) · blob `06dd4a7d1ae7f9119258cd09fd17a519fcb7abd4`
- [slime/utils/seqlen_balancing.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/seqlen_balancing.py) · blob `57cf47f3cd20e67c8f0ab34d5841cd708ee451fa`
- [slime/utils/staleness.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/staleness.py) · blob `8e51536c7f0ddb3c15bce1a726ff1368ba81afb9`
- [slime/utils/tensor_backper.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/tensor_backper.py) · blob `3b0c3a64bf8fd0d125ff20d48fe7711c804c69d4`
- [slime/utils/types.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/types.py) · blob `d92e438f5ea7b8cd20f008d8eba2a667f91f14e4`
- [slime/utils/weight_sync.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/utils/weight_sync.py) · blob `6d83bc19e50298bade0dc42b07e998fec5f600eb`

## slime_plugins

- [slime_plugins/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime_plugins/models/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime_plugins/models/flash_dot_product_attention.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/flash_dot_product_attention.py) · blob `fd89bdc4645f040d44ab1fc943d4798d81a66135`
- [slime_plugins/models/glm4.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm4.py) · blob `cc8efbad22dc8c492ad4b4df5ef3d355d8314eb4`
- [slime_plugins/models/glm5/glm5.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5/glm5.py) · blob `5cc89deee3e47467d84a36604e0bd5c02a1733df`
- [slime_plugins/models/glm5/ops/indexer.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5/ops/indexer.py) · blob `2f785b96038985ef1e96d9c73da86868ff89d99d`
- [slime_plugins/models/glm5/ops/sparse_mla.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5/ops/sparse_mla.py) · blob `2e3ce2628b4486d812558a2f7f0f6d79db1a2ca0`
- [slime_plugins/models/glm5/ops/tilelang_indexer_bwd.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5/ops/tilelang_indexer_bwd.py) · blob `737800f0348451e39f52fb3d630c3e2e8760b45e`
- [slime_plugins/models/glm5/ops/tilelang_indexer_fwd.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5/ops/tilelang_indexer_fwd.py) · blob `cc1b7a3ce4055bd95819e4f5edcf970f8e05782d`
- [slime_plugins/models/glm5/ops/tilelang_sparse_mla_bwd.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5/ops/tilelang_sparse_mla_bwd.py) · blob `bcab4064c31f21fc031a74d94478cd25c5abf367`
- [slime_plugins/models/glm5/ops/tilelang_sparse_mla_fwd.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5/ops/tilelang_sparse_mla_fwd.py) · blob `864b14939330ac90b2d898c3251db6bec9db0a90`
- [slime_plugins/models/glm5_next/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5_next/README.md) · blob `8e8e528f293a44cd02bb98c3dd0d678e81cc48cf`
- [slime_plugins/models/glm5_next/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5_next/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime_plugins/models/glm5_next/attention.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5_next/attention.py) · blob `d2a3ae071639c8dbb01c67aec0cb67d8e57f8153`
- [slime_plugins/models/glm5_next/glm5_next.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5_next/glm5_next.py) · blob `b3e59938cf3c8ddff4d6ab2a34991f9896aa21f5`
- [slime_plugins/models/glm5_next/model.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5_next/model.py) · blob `f308643c834e09a63c51713d920ad5864940dfa3`
- [slime_plugins/models/glm5_next/ops.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5_next/ops.py) · blob `46adb03403f887fb2fb41432367cd90fb3c1b442`
- [slime_plugins/models/glm5_next/vision.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/glm5_next/vision.py) · blob `4098d0ec1ea8d6f3174f64392cf10d854604b787`
- [slime_plugins/models/hf_attention.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/hf_attention.py) · blob `99b7a01fa409fe839b845fae557bb7796fd935a5`
- [slime_plugins/models/learnable_softmax_attention.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/learnable_softmax_attention.py) · blob `6dd515782fae59243b828bac9ddc87e8813458ee`
- [slime_plugins/models/minimax_m2.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/minimax_m2.py) · blob `ec43af26d907fdc1acdf57a70edcd7b571c84577`
- [slime_plugins/models/qwen3_5.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/qwen3_5.py) · blob `1c30ceef8bbcc600d86a69758f7f3e2dce9bb325`
- [slime_plugins/models/qwen3_5_native.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/qwen3_5_native.py) · blob `c5e6603725e875fe8e711632451cb2876f7d9170`
- [slime_plugins/models/qwen3_5_vl.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/qwen3_5_vl.py) · blob `cdc1ad7622a9857123fb68130d34c0c61f382855`
- [slime_plugins/models/qwen3_5_vl_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/qwen3_5_vl_utils.py) · blob `26f59d1f7e96841132e5be6c91f889e239fded6f`
- [slime_plugins/models/qwen3_next.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/qwen3_next.py) · blob `cc2937228eb4c8f38fb6bfa3c0b8d1706722fb71`
- [slime_plugins/models/qwen_gdn_backend.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/models/qwen_gdn_backend.py) · blob `a95bc8a0d05a08ca78bbef9a1b6284333991fbf2`
- [slime_plugins/rollout_buffer/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/rollout_buffer/README.md) · blob `e85e68d89c6d1192999bd9df5fbfb87ee85b8940`
- [slime_plugins/rollout_buffer/README_zh.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/rollout_buffer/README_zh.md) · blob `cfa689fe716b7d4f6bce02073057fc378c52d05a`
- [slime_plugins/rollout_buffer/buffer.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/rollout_buffer/buffer.py) · blob `db4e561124b54598c7788636291ab34c9cef33e0`
- [slime_plugins/rollout_buffer/generator/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/rollout_buffer/generator/__init__.py) · blob `87090b103846e53a0d1ffa318408f3a1d96d4657`
- [slime_plugins/rollout_buffer/generator/base_generator.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/rollout_buffer/generator/base_generator.py) · blob `5c6cb1d269883da5cb96228cf4c3bec7ef75d52f`
- [slime_plugins/rollout_buffer/rollout_buffer_example.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/rollout_buffer/rollout_buffer_example.py) · blob `ac1fb6998f9eb0bd50e2d4aaa410abc715cc62f9`
- [slime_plugins/rollout_buffer/rollout_buffer_example.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime_plugins/rollout_buffer/rollout_buffer_example.sh) · blob `345660b5ef6fb86bfdc1d5a50a25a3fc4b736f64`

## tests

- [tests/_cp_dist_helpers.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/_cp_dist_helpers.py) · blob `351dadfc28d80ad20b810eeeafac5cf0bd123417`
- [tests/agent_e2e_helpers.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/agent_e2e_helpers.py) · blob `30fad6610c6379365e6efb6310760969d8cf518d`
- [tests/ci/README.md](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/ci/README.md) · blob `2b58be3d4c78a57ec8c5794c5852dbcb9069d8a1`
- [tests/ci/github_runner/.env.example](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/ci/github_runner/.env.example) · blob `1692a83a38f74fbeb314af605b365334df7e80cd`
- [tests/ci/github_runner/.gitignore](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/ci/github_runner/.gitignore) · blob `2eea525d885d5148108f6f3a9a8613863f783d36`
- [tests/ci/github_runner/docker-compose.yml](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/ci/github_runner/docker-compose.yml) · blob `c6d0fb63c8de5ec1a18bd3a7622c2dac6eadff75`
- [tests/ci/gpu_lock_exec.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/ci/gpu_lock_exec.py) · blob `e61593170c1f934c5d70bfea1de649d64b081b96`
- [tests/ci/oci_cache.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/ci/oci_cache.py) · blob `dc134c4ad7c3d302041393c590de9461ca9aacf8`
- [tests/ci/setup_agent_e2e.sh](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/ci/setup_agent_e2e.sh) · blob `97a71e56daa428fa4da5c6258eb926da37bb9d20`
- [tests/fanout_test_helpers.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/fanout_test_helpers.py) · blob `8f3470796efbfe628b86febb4d0621b9a0becd75`
- [tests/glm52_layerwise_comparator.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/glm52_layerwise_comparator.py) · blob `4235da6463172c1bd6a77f111aab29302cc2821f`
- [tests/observability/test_trace_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/observability/test_trace_utils.py) · blob `fa2dab7d1f7b821138ecd72386474970dd9fbe59`
- [tests/pipeline_rl_test_helpers.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/pipeline_rl_test_helpers.py) · blob `0dda5cf5fb2b49cc4297eb030282b08ff8d7e382`
- [tests/plugin_contracts/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/plugin_contracts/__init__.py) · blob `87f1598bf0b17a9cd2a07c095656f41e7c0cba6e`
- [tests/plugin_contracts/_shared.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/plugin_contracts/_shared.py) · blob `9efa1b9072f59af768924bd983cbbad3034f6d9a`
- [tests/plugin_contracts/test_plugin_generate_contracts.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/plugin_contracts/test_plugin_generate_contracts.py) · blob `d9db1b2f43f94b60f5b48a9f0c92f5e2f980c9bf`
- [tests/plugin_contracts/test_plugin_path_loading_contracts.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/plugin_contracts/test_plugin_path_loading_contracts.py) · blob `87aba819768dcbddb4bfa4c0c96fc9818ec4180c`
- [tests/plugin_contracts/test_plugin_rollout_contracts.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/plugin_contracts/test_plugin_rollout_contracts.py) · blob `a4f31310d5b1d48b74e3eada14ffe834ffaf75de`
- [tests/plugin_contracts/test_plugin_runtime_hook_contracts.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/plugin_contracts/test_plugin_runtime_hook_contracts.py) · blob `18343409cafa0b01295c8d944c7c7a23c8f73641`
- [tests/rollout_health_test_helpers.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/rollout_health_test_helpers.py) · blob `88f05d0d6a01d27dcc9c5749713d79f8f21ea42a`
- [tests/test_accelerator.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_accelerator.py) · blob `4273b632540c0090fe0535feb7d1ddcd7153e4cc`
- [tests/test_advantage_whiten_cp.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_advantage_whiten_cp.py) · blob `e33c0ed7fe6e43411a696b6c364a77e1bfa34cd5`
- [tests/test_agent/__init__.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [tests/test_agent/_dump_helpers.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/_dump_helpers.py) · blob `3a4519d835834186f5515ad3abe9061b9900587d`
- [tests/test_agent/_fakes.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/_fakes.py) · blob `24c3f85f42c6769a93d4581c5e8568863ef33a8a`
- [tests/test_agent/test_adapters.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_adapters.py) · blob `be346b2ec6df421e984c947be8ded9c1b315338d`
- [tests/test_agent/test_agent_rollout_cpu.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_agent_rollout_cpu.py) · blob `f4282e723ad1c0c8cfc248d071ad94dcee63e5b3`
- [tests/test_agent/test_e2e_asset_cache.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_e2e_asset_cache.py) · blob `d2de67d4e0bb328b52c0cf8b01067d0b9938c444`
- [tests/test_agent/test_e2e_grpo_contract.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_e2e_grpo_contract.py) · blob `b043e3a826c86a12ea311c180b02bd494ef8fff0`
- [tests/test_agent/test_harness.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_harness.py) · blob `9b4a14d8b4d080299aef9a7ac47bfbcb4cfeffdc`
- [tests/test_agent/test_prompt_continuity.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_prompt_continuity.py) · blob `aefd12ff65e9f9fcb6b3bef5eb89a5112185dfcc`
- [tests/test_agent/test_responses.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_responses.py) · blob `e20586fa64609d53cc61838c0ac8a20014f9de5b`
- [tests/test_agent/test_sampler_replay.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_sampler_replay.py) · blob `561ec89e6b16662c33f76ab83b38f8a9a8225023`
- [tests/test_agent/test_sandbox_exec_and_wait.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_sandbox_exec_and_wait.py) · blob `670a1f7122584bdfef3a961e8e8a901aa1539eed`
- [tests/test_agent/test_sunabako_provider.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_sunabako_provider.py) · blob `4403a889bb48bd83d7516e101a190c2fd7b50e29`
- [tests/test_agent/test_swe_workspace_diff.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_swe_workspace_diff.py) · blob `2316b951514ad1dc173f1a2a63b0787dc9badb0b`
- [tests/test_agent/test_token_contract.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_token_contract.py) · blob `160aff120768433ee58df3692e66f20d450326ef`
- [tests/test_agent/test_trajectory_manager_branching.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent/test_trajectory_manager_branching.py) · blob `13ba81f485e09e9b9c751db583c810a5d354081b`
- [tests/test_agent_sunabako_codex_e2e.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_agent_sunabako_codex_e2e.py) · blob `c1d8069f689e88915e6dc0d7595746edfec48238`
- [tests/test_block_fp8_zero_block.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_block_fp8_zero_block.py) · blob `16885d25c61d51109bf68525f2f450cde48ad99f`
- [tests/test_cispo_loss.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_cispo_loss.py) · blob `9f2e86c89cb6f4ed707aa6b8915793b5b9d6f1f1`
- [tests/test_cp_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_cp_utils.py) · blob `c7d3abe9a2c21fbc3bd3952f01c1ac9dc5a3056c`
- [tests/test_cuda_stack_offload.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_cuda_stack_offload.py) · blob `fa52ff64a114ec8c15ff613f21f62fd939622a4c`
- [tests/test_deep_ep_tms_patch.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_deep_ep_tms_patch.py) · blob `b1aee804782cf253b007212dfb732ef63f14d56b`
- [tests/test_discounted_returns.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_discounted_returns.py) · blob `8e1caae82e93c1bb37b347b016413519d52fe113`
- [tests/test_disk_delta_checkpoint_index.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_disk_delta_checkpoint_index.py) · blob `52087704952a72be3a582e111fa03de24608eac7`
- [tests/test_disk_delta_recovery.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_disk_delta_recovery.py) · blob `429c404d3f30ec4d135420f2aefdddd30ef21082`
- [tests/test_distributed_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_distributed_rollout.py) · blob `660c614935757e4e61ec2074c3c0002580cf11cf`
- [tests/test_docs_consistency.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_docs_consistency.py) · blob `217a29884fe26ef0fbef7b085ea804d4294d0802`
- [tests/test_dp_schedule.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_dp_schedule.py) · blob `33a8be53b5ea8aef7a4ea53af7049aacaea352c4`
- [tests/test_empty_colocated_weight_bucket.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_empty_colocated_weight_bucket.py) · blob `c7683e10bc034592901eb8647fcafb3b7011cd04`
- [tests/test_eval_config.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_eval_config.py) · blob `a51270e01205be500130d8d07aed73a8995a03b7`
- [tests/test_expert_routing.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_expert_routing.py) · blob `9c29ec079b5d141c19125301e26eaffb280f1772`
- [tests/test_external_sglang_engines.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_external_sglang_engines.py) · blob `61b32c460d350277d4faccff1ad09edae9179026`
- [tests/test_filter_long_prompt.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_filter_long_prompt.py) · blob `9ec9462337217cf4daf844f3b7177e08742ef904`
- [tests/test_full_disk_weight_update.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_full_disk_weight_update.py) · blob `978175d5642d7334db32243cb2ea9c6641f4af20`
- [tests/test_fully_async_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_fully_async_rollout.py) · blob `bcee257335a609e642fc7f25a99c7e87194ae2c6`
- [tests/test_glm4.7_30B_A3B_pd_mooncake.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm4.7_30B_A3B_pd_mooncake.py) · blob `75614e48cef460d113dc28658b2c58e5e3b5fb43`
- [tests/test_glm52_6layer_deterministic_e2e.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm52_6layer_deterministic_e2e.py) · blob `752a53993966c4df6ecbbf420cf125ecb0e56612`
- [tests/test_glm52_layerwise_comparison.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm52_layerwise_comparison.py) · blob `5ca5f679268aacbae4c4e60e7f0b00e8ae325cac`
- [tests/test_glm52_layerwise_zero_e2e.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm52_layerwise_zero_e2e.py) · blob `93a7ffc5717a6aed4327911c63ef9e4cb76f0954`
- [tests/test_glm5_indexer_q_norm.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm5_indexer_q_norm.py) · blob `30201f36a30713264824bfe383ace3f7153d1afb`
- [tests/test_glm5_indexer_short_context.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm5_indexer_short_context.py) · blob `fb189d122624ef0289a92eab9f2eed5de12b35eb`
- [tests/test_glm5_next_cp.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm5_next_cp.py) · blob `d5ac10f4c61293fe16ed4e0d517fff7c3010c1aa`
- [tests/test_glm5_next_gpu.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm5_next_gpu.py) · blob `d300b79245200729b04fac81bbf3d82a5fce3c0c`
- [tests/test_glm5_next_ops.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_glm5_next_ops.py) · blob `8c014f41c4cdc37dbbb629c953069c625cedd5fa`
- [tests/test_grouped_rewards.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_grouped_rewards.py) · blob `eec8c4587a4b5706439d6c7e3f3c8f301ceaeb04`
- [tests/test_hf_to_megatron.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_hf_to_megatron.py) · blob `267f87fda1af6fef68c5e5efeb0caa28ab52e445`
- [tests/test_layerwise_alignment.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_layerwise_alignment.py) · blob `d84e78fe3ffd72816de0c2596e1c0024e449685e`
- [tests/test_logprob_response_spans.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_logprob_response_spans.py) · blob `297b0292114168e4a3504ffe7d512dc1b6dcab5a`
- [tests/test_loss_cp_invariance.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_loss_cp_invariance.py) · blob `4f2ca9559b251fd5fa419786504db57bed60b104`
- [tests/test_megatron_argument_validation.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_megatron_argument_validation.py) · blob `a2f245c1c77ba5e4931e228b41530872abacf713`
- [tests/test_megatron_checkpoint.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_megatron_checkpoint.py) · blob `4af344ebcd5abb46c854fe9ce9b2bab90793b094`
- [tests/test_megatron_grad_sync_memory.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_megatron_grad_sync_memory.py) · blob `e6e832197a26c7a54252b0195c4d84b3e59583cf`
- [tests/test_megatron_tokenizer_init.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_megatron_tokenizer_init.py) · blob `3d2efedeb2b1c00088c974fd4f98dc937242cfeb`
- [tests/test_metric_report.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_metric_report.py) · blob `9ba8f29f653e126c7c06f873579336698f3cf249`
- [tests/test_metric_report_dist.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_metric_report_dist.py) · blob `466ad3b72974394f8a8c46266cdc8b7e5f3e6478`
- [tests/test_mimo_7B_mtp_only_grad.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_mimo_7B_mtp_only_grad.py) · blob `e1bee49d1cfe02efe4ec7ece7ebbecbc49bd81fa`
- [tests/test_model_provider_critic.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_model_provider_critic.py) · blob `1cc954d832b092c8320656edf8416e3903f7f02f`
- [tests/test_model_provider_freeze.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_model_provider_freeze.py) · blob `cd238c8ff7883ea5923fef994eab5c66146f005a`
- [tests/test_mooncake_memory_reregister.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_mooncake_memory_reregister.py) · blob `52b37189ed27f2819a6784d91bce8a505f55e288`
- [tests/test_moonlight_16B_A3B.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_moonlight_16B_A3B.py) · blob `bc63dbdbbdb0cedb3ff5c05a226f1590f1c1a43b`
- [tests/test_moonlight_16B_A3B_r3.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_moonlight_16B_A3B_r3.py) · blob `157795812128047d011e369f69126bc8b9f019b4`
- [tests/test_optional_straw.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_optional_straw.py) · blob `ebecc16f1add2809f23efa743e62e731cefc5964`
- [tests/test_pipeline_rl.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_pipeline_rl.py) · blob `97570e1e35a2562db6a7f9a2b60aefe4c1a42d6c`
- [tests/test_placement_group.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_placement_group.py) · blob `537b883d7a95b02b18c53e57d2ad3ffd9cbcc6c0`
- [tests/test_policy_loss.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_policy_loss.py) · blob `0e947b93920fa83559617057ae50fb9a5dae986f`
- [tests/test_ppo_kl_metric.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_ppo_kl_metric.py) · blob `eb3e1855982fb66236be7b7a2e23d9c5d6f215e4`
- [tests/test_ppo_logprob_entropy.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_ppo_logprob_entropy.py) · blob `ba29d4713fe055623689f49b0d776e593164a42e`
- [tests/test_ppo_logprob_entropy_gpu.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_ppo_logprob_entropy_gpu.py) · blob `ff6b8d6247391b2c9ac07c6fc08b1bbfccb8bf9e`
- [tests/test_process_rollout_data.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_process_rollout_data.py) · blob `b8090c95fa7645baecebd061097d66da6b9b8d47`
- [tests/test_published_payload_retry.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_published_payload_retry.py) · blob `bed5f40e5d4dc9ebb02842bb4886f3203a2d55bb`
- [tests/test_queue_sample_codec.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_queue_sample_codec.py) · blob `23e55dde8da8d56a38827bd01aebcd0b65a0df75`
- [tests/test_quick_start_glm4_9B.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_quick_start_glm4_9B.py) · blob `e1b71bd5175b646498279e59c5e4862f736901f3`
- [tests/test_qwen2.5_0.5B_debug_rollout_then_train.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_debug_rollout_then_train.py) · blob `783bb6ac0da30da70c6fc5bb758c28478e371e21`
- [tests/test_qwen2.5_0.5B_debug_train_dump_e2e.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_debug_train_dump_e2e.py) · blob `76c1411964cbc648dea40e153743d9b4c055adaf`
- [tests/test_qwen2.5_0.5B_fanout_short.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_fanout_short.py) · blob `c624e4b9b20e7583be1c57568a2840b300b87e54`
- [tests/test_qwen2.5_0.5B_fully_async_short.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_fully_async_short.py) · blob `1d83b00a12cadd6bce93ab0bc396fe7c3f651255`
- [tests/test_qwen2.5_0.5B_opd_sglang.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_opd_sglang.py) · blob `4ac42172563f48c877bae27f6609d086d6d34bd7`
- [tests/test_qwen2.5_0.5B_pipeline_rl.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_pipeline_rl.py) · blob `0b4d73c4ad8db35c034c9d0299aa0775e343b314`
- [tests/test_qwen2.5_0.5B_rollout_health.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_rollout_health.py) · blob `85434712c3a80155f8b6f04a59b227ca77fa91fe`
- [tests/test_qwen2.5_0.5B_score_centering.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_score_centering.py) · blob `d5a75288c84e828bd37254dfb369757703117c78`
- [tests/test_qwen2.5_0.5B_sglang_config.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_sglang_config.py) · blob `6229a91604050f9573de7c0a2589d6c9b5f76cac`
- [tests/test_qwen2.5_0.5B_sglang_config_distributed.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_sglang_config_distributed.py) · blob `aee1ae19678f4f5a2e238eef475477c7fd337ba1`
- [tests/test_qwen2.5_0.5B_training_recovery.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen2.5_0.5B_training_recovery.py) · blob `9bb0a25b8391caf012398f5ab43a2b2459587c88`
- [tests/test_qwen3.5_0.8B_gsm8k_short.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3.5_0.8B_gsm8k_short.py) · blob `93306eadd32fbdbac93d3d715d1d7309ec4babc0`
- [tests/test_qwen3.6_35B_A3B_pd_mooncake.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3.6_35B_A3B_pd_mooncake.py) · blob `2a4cee57b0485517da3da15d2d7fa2d7b4b0a75d`
- [tests/test_qwen3_0.6B_parallel_check.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_0.6B_parallel_check.py) · blob `0a1438a1258a9fb3b6b16155672ede2f178399a3`
- [tests/test_qwen3_30B_A3B.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_30B_A3B.py) · blob `cdb9ebbe5199c281d80e0c3663686644fef89981`
- [tests/test_qwen3_30B_A3B_r3.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_30B_A3B_r3.py) · blob `c36613fcc45d28eae0784336c0c94292ca0b9875`
- [tests/test_qwen3_30B_A3B_training_recovery.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_30B_A3B_training_recovery.py) · blob `69c9cb22ccf57894f0ffcc77572cb18c3b46dd39`
- [tests/test_qwen3_4B_ckpt.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_4B_ckpt.py) · blob `c9803bfb16f98f0f277b51ca8a0f047861040e83`
- [tests/test_qwen3_4B_external_pd.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_4B_external_pd.py) · blob `5c87592b8b87609b12a0704de301f610b9441609`
- [tests/test_qwen3_4B_ppo.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_4B_ppo.py) · blob `f261e9781a8396e3f5c81f16db8dd1afa2b26f58`
- [tests/test_qwen3_4B_ppo_disaggregate.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_4B_ppo_disaggregate.py) · blob `bafb6260ff1ad9db4fe1b4b40e37b7225c9a6269`
- [tests/test_qwen3_4B_ppo_train_critic_only.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_4B_ppo_train_critic_only.py) · blob `50b5072e4fbd0fe939fbda1092749be2651558f5`
- [tests/test_qwen3_4B_streaming_partial_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_4B_streaming_partial_rollout.py) · blob `85b4b7d2ab518bc710a4a71191502cc5ad6f7bd7`
- [tests/test_qwen3_5_native_weights.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_5_native_weights.py) · blob `22c8d764b28ffe3e1e131e27d2a671c2558dc438`
- [tests/test_qwen3_5_vl_native.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_5_vl_native.py) · blob `d1c63e009e9385984c58cb9ac594c2140886fe68`
- [tests/test_qwen3_linear_attention_cu_seqlens.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_qwen3_linear_attention_cu_seqlens.py) · blob `c9784ccbe5afd1962afd65023e65e7b10d8a12dd`
- [tests/test_read_file_slicing.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_read_file_slicing.py) · blob `363af1b2b047d6d9fac7dc3f03e9ea01bba2f79e`
- [tests/test_reference_top_p_replay.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_reference_top_p_replay.py) · blob `25fa0aac02cd05317ffa02f7bbe086ec4adf2276`
- [tests/test_release_train.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_release_train.py) · blob `9e6a3b7527542e95f28c06a567a7ea97f8544c20`
- [tests/test_reloadable_process_group_megatron_bindings.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_reloadable_process_group_megatron_bindings.py) · blob `a3f172b47b71a494c8a2e45678172fbf26e7c00c`
- [tests/test_reloadable_process_group_memory_check.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_reloadable_process_group_memory_check.py) · blob `69abee7b9ab8a53932690880745ddcd6bd59368f`
- [tests/test_reloadable_process_group_world.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_reloadable_process_group_world.py) · blob `289b0bebf0eee5cf419af677cce09a581480799d`
- [tests/test_rm_deepscaler.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rm_deepscaler.py) · blob `0883a606228a74b7fae74081b0dda5a5c5aaf467`
- [tests/test_rm_f1.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rm_f1.py) · blob `f6ba8140f07fc2675dd9b2b648dc0fa321554530`
- [tests/test_rm_gpqa.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rm_gpqa.py) · blob `6e7ac1009f24bab8cd91616fb8182a391424cf32`
- [tests/test_rm_math.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rm_math.py) · blob `6ec589485574967ee17edbfbeb49c43aea4428f7`
- [tests/test_rm_math_dapo.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rm_math_dapo.py) · blob `3a5e9a28b96680505848783ed114ece15936271e`
- [tests/test_rollout_buffer_order.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rollout_buffer_order.py) · blob `f4f8b17a12bcd237d95fcf142d4d8fab87548a0d`
- [tests/test_rollout_data_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rollout_data_utils.py) · blob `c6d9cb8abd92d6ffff2eb13471ac1c517cf8b0f5`
- [tests/test_rollout_manager_recovery.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rollout_manager_recovery.py) · blob `7b55b4aba55ab6183a5a15893cab4490dfe5d385`
- [tests/test_rollout_metadata_index.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rollout_metadata_index.py) · blob `4123129ba3f46a65a7855c8ac361c3ea768b1e2d`
- [tests/test_rollout_metrics.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rollout_metrics.py) · blob `b460c24538de50336f58c5e715ae3d3da577eb73`
- [tests/test_rollout_sample_hooks.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rollout_sample_hooks.py) · blob `ec5f2926705f26870010e6ac117740c1980dad67`
- [tests/test_rollout_straw_transport.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_rollout_straw_transport.py) · blob `c6dc5a165714f12a87b8622940c390ef01afa7e6`
- [tests/test_routed_experts_disk_layout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_routed_experts_disk_layout.py) · blob `aba7aa896a69dd50e66b70f50953ff8b014dba7e`
- [tests/test_sample.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_sample.py) · blob `e61326377493adcc221270b4876b5edeac6c29b4`
- [tests/test_score_centering.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_score_centering.py) · blob `0367ca795b39f803d78ccbde10346710d084149d`
- [tests/test_score_centering_binary.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_score_centering_binary.py) · blob `b936f3064161aea57921c81ad06713111d86d673`
- [tests/test_score_centering_transport.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_score_centering_transport.py) · blob `be005d16a7f7e24243544173518bddd977cfa919`
- [tests/test_server_control.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_server_control.py) · blob `33a35a61e2d7d0adc35c0afd836a7c343842be2b`
- [tests/test_sglang_config_mixed_offload.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_sglang_config_mixed_offload.py) · blob `edcd460791b096d228aa53b1ade80097358d8604`
- [tests/test_sglang_config_mixed_offload_ft.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_sglang_config_mixed_offload_ft.py) · blob `525ea6bfb972f2228c9c15a888de6b4375aa361a`
- [tests/test_sglang_runtime.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_sglang_runtime.py) · blob `13f156553a0b5b3f1530ddac53aa5ab58fe119e6`
- [tests/test_sglang_top_p_copy.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_sglang_top_p_copy.py) · blob `0549d00a073413e0f170173342f2c3121b8d5857`
- [tests/test_sglang_weight_update_compat.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_sglang_weight_update_compat.py) · blob `1fccd566a9797d8a2851b2f864ef83cbdd5f3f4b`
- [tests/test_stateless_adam.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_stateless_adam.py) · blob `a981d096716952294ea34739e14b65a6cd397b2c`
- [tests/test_straw_checkpoint_rewind.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_straw_checkpoint_rewind.py) · blob `5a2fd9745fbdcb8275fa803a0413dd48eb8ec207`
- [tests/test_straw_fully_async_recovery.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_straw_fully_async_recovery.py) · blob `1fd4b02b0f06b3d082b18f7a80861592df5f0121`
- [tests/test_straw_r3.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_straw_r3.py) · blob `57b081d93f24990c062a025ba0a971339ae0b0e3`
- [tests/test_streaming_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_streaming_rollout.py) · blob `22a93588d9fdbfcd65df94de78ced5d994ff81d1`
- [tests/test_tau_bench_token_delta.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_tau_bench_token_delta.py) · blob `4e677ef27d50f8731d0f105dcd6ce90e5c07c21e`
- [tests/test_train_data_utils.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_train_data_utils.py) · blob `6b94ff29ac7f334ce6beb6f326336f4b794cd566`
- [tests/test_training_recovery.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_training_recovery.py) · blob `5db087054ac8ee3ced16a3db473dfba0fd8eba58`
- [tests/test_update_weight_factory.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_update_weight_factory.py) · blob `ef4968daa1d9399084319c4c81469ce8ff73a152`
- [tests/test_value_temperature.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_value_temperature.py) · blob `195d89e88f985d635a85ca8b095c0710abb3bc47`
- [tests/training_recovery_test_helpers.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/training_recovery_test_helpers.py) · blob `a5ea377e4d4b8d56ea6ab8bb708f8bc72cc770bd`
- [tests/utils/test_hf_checkpoint_saver.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/utils/test_hf_checkpoint_saver.py) · blob `ab73061349f893f87ac0037645fe130d78aac787`
- [tests/utils/test_loss_mask_type_qwen35.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/utils/test_loss_mask_type_qwen35.py) · blob `18457ccc26b8cd01430f331b7d03c25183056b3b`
- [tests/utils/test_megatron_role_config.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/utils/test_megatron_role_config.py) · blob `093b33519487f4fe5482cf9db2f5d2ce295cef78`
- [tests/utils/test_megatron_server_arguments.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/utils/test_megatron_server_arguments.py) · blob `ebf837c6e7af206bf0ad8d3ff066e63bd76b3b0b`
- [tests/utils/test_sglang_arguments.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/utils/test_sglang_arguments.py) · blob `b7584abdf50accf981982353f837e1554297cf12`
- [tests/utils/test_sglang_config.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/utils/test_sglang_config.py) · blob `617ff833f18466054ad2a0a0f8474c361829733d`

## tools

- [tools/analyze_profile.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/analyze_profile.py) · blob `de511744f279402b4fddbdef2bb1e923434d45a1`
- [tools/convert_hf_to_fp8.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/convert_hf_to_fp8.py) · blob `bcc4306b9d829bc8bc282d488e6a46270d9ee345`
- [tools/convert_hf_to_int4.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/convert_hf_to_int4.py) · blob `3dbf075ebf6d8a08cfa875cc08ab88f7be6af66c`
- [tools/convert_hf_to_int4_direct.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/convert_hf_to_int4_direct.py) · blob `7eaffc7272f381d0def7cb755765724ce0f7438a`
- [tools/convert_hf_to_torch_dist.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/convert_hf_to_torch_dist.py) · blob `62207788951cdd23d130500dce35fdccae00e0dc`
- [tools/convert_k2_thinking_int4_to_bf16.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/convert_k2_thinking_int4_to_bf16.py) · blob `78c0effc043dd0f39bdd4a871aee399595855d74`
- [tools/convert_to_hf.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/convert_to_hf.py) · blob `201e35bf9c4c9faa2f7bb734b2fef6cf92f8b435`
- [tools/convert_torch_dist_to_hf.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/convert_torch_dist_to_hf.py) · blob `8049d77437024d9b381a911e96b846a48f8098a2`
- [tools/convert_torch_dist_to_hf_parallel.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/convert_torch_dist_to_hf_parallel.py) · blob `763254d42cfc2cc7bbe3fe46d4e614ecbb035729`
- [tools/fp8_cast_bf16.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/fp8_cast_bf16.py) · blob `edc8485d90f278dacea3adece1668dc18b4d5d50`
- [tools/profile_rollout.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/profile_rollout.py) · blob `8869a199360a89fb985289657d45161f97edb555`
- [tools/trace_timeline_viewer.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tools/trace_timeline_viewer.py) · blob `1690ac46d0b9399061abf022de9c2babfe7f7357`

## train.py

- [train.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/train.py) · blob `ffbb5d743096e68bb8a66f00418bdd173291dd1b`
