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
generated_body_sha256: 2ba295393a0c5454e545e129de08fbc0dc2439200644edd6805edd02f0faa7ff
---

# THUDM/slime: fixed source directory map

Commit `0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e` · ref `main`. Full paths are discoverable; listing a file does not imply its contents were read.

Use `wiki-code THUDM/slime 0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e PATH` to inspect exact files, then follow callers/tests. A gitlink entry pins a child SHA, not its latest branch.

## .agents

- [.agents/skills](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.agents/skills) · blob `454b8427cd757f30dc7fdb9a325d19c399770417`

## .claude

- [.claude/skills/add-dynamic-filter/SKILL.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.claude/skills/add-dynamic-filter/SKILL.md) · blob `be8461a0edb44597e95d83f5ad02e3319f70d202`
- [.claude/skills/add-eval-dataset-config/SKILL.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.claude/skills/add-eval-dataset-config/SKILL.md) · blob `f59360687ffa342c7f2214de8fee4b3692a07236`
- [.claude/skills/add-reward-function/SKILL.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.claude/skills/add-reward-function/SKILL.md) · blob `f6ba3f9a79bf8755351de2e33a608de4a28a19de`
- [.claude/skills/add-rollout-function/SKILL.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.claude/skills/add-rollout-function/SKILL.md) · blob `c8623a135b77e787d3725211ee61034e2bcf59bb`
- [.claude/skills/add-tests-and-ci/SKILL.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.claude/skills/add-tests-and-ci/SKILL.md) · blob `000ea983b91922bfccec231a25a5ce7045737b71`
- [.claude/skills/release/SKILL.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.claude/skills/release/SKILL.md) · blob `b4fcdaa2d239e9f5e7d1caa18ef402a050f409f8`
- [.claude/skills/release/scripts/check_release.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.claude/skills/release/scripts/check_release.py) · blob `72482f25bbd329400fb0705d629b58d0bc4ffd1d`
- [.claude/skills/slime-code-review-preferences/SKILL.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.claude/skills/slime-code-review-preferences/SKILL.md) · blob `0065afbed90b7de290458b742a7d79859f82eec9`

## .dockerignore

- [.dockerignore](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.dockerignore) · blob `937a820df0f139586d42b85c2bf1955f662e8595`

## .github

- [.github/ISSUE_TEMPLATE/bug_report.yml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/ISSUE_TEMPLATE/bug_report.yml) · blob `36ff4770cf1acbbd7c6f440056d847509bc61d2b`
- [.github/ISSUE_TEMPLATE/config.yml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/ISSUE_TEMPLATE/config.yml) · blob `04d024a2c2ea0f119eddf905b3e5282c1fb0c1bd`
- [.github/ISSUE_TEMPLATE/question.yml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/ISSUE_TEMPLATE/question.yml) · blob `7c9c4dac2ee9f9912f5601c73ddb58a2900eaf1a`
- [.github/workflows/bot-slash-lint.yaml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/workflows/bot-slash-lint.yaml) · blob `85ae508c268d4a3f65c24bff46a7bc1a3bec0f0b`
- [.github/workflows/conda-ci.yml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/workflows/conda-ci.yml) · blob `f698067365e98144590811b86568c65843ac4623`
- [.github/workflows/generate_github_workflows.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/workflows/generate_github_workflows.py) · blob `ee98bfcb5d6794c2c5372f835aa7e05a2542e0bf`
- [.github/workflows/pr-test.yml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/workflows/pr-test.yml) · blob `a170e5976b21264fac0ae14dd083a6d96db4cab0`
- [.github/workflows/pr-test.yml.j2](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/workflows/pr-test.yml.j2) · blob `3b4aa6a059aa2dec08fe0e7cfa9f32c3bac0d245`
- [.github/workflows/pre-commit.yml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/workflows/pre-commit.yml) · blob `9c6de3c5b71bf40c95dc0d703512a4467df99650`
- [.github/workflows/release-docs.yaml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.github/workflows/release-docs.yaml) · blob `fde68b4a361246afd25d219852cb9f2d158a6bc8`

## .gitignore

- [.gitignore](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.gitignore) · blob `40dfe47ffb48b1856479be25e8b320488adce233`

## .pre-commit-config.yaml

- [.pre-commit-config.yaml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/.pre-commit-config.yaml) · blob `7d0d57ac49bace39a4a47216edb070e159844efb`

## CONTRIBUTING.md

- [CONTRIBUTING.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/CONTRIBUTING.md) · blob `839956f743b03b171fe02bfbcd749c375ee71554`

## LICENSE

- [LICENSE](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/LICENSE) · blob `456e53742c2559a96f834c77daafd58c895db5cb`

## README.md

- [README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/README.md) · blob `932ed612f92d19d6bec2b93faf2b4b54348e6eb9`

## README_zh.md

- [README_zh.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/README_zh.md) · blob `1412e238f836ab3bb099b6d6891611f455841e20`

## build_conda.sh

- [build_conda.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/build_conda.sh) · blob `af89317380d77375d45294d520108cf4a0ea7b32`

## docker

- [docker/Dockerfile](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/Dockerfile) · blob `5ebd67fc8e6ad95fa12c3311bace2d67c99a1178`
- [docker/Dockerfile.gb10](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/Dockerfile.gb10) · blob `2844b946b5de4e2262ff54fc7083c348e71d1ec1`
- [docker/Dockerfile.rocm](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/Dockerfile.rocm) · blob `a3d6001d3e620f7bb2c1fc0a65f03e14216da240`
- [docker/Dockerfile.rocm_MI350-5](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/Dockerfile.rocm_MI350-5) · blob `f6974d69b446623ac1c363a668166a2df0cb42b8`
- [docker/Dockerfile_20250810_9a48ba0.rocm](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/Dockerfile_20250810_9a48ba0.rocm) · blob `176c1ee61b2a34e9fecdaf206302ec5ad890ee1a`
- [docker/Dockerfile_20250810_c22f55b.rocm](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/Dockerfile_20250810_c22f55b.rocm) · blob `2bc78501266226d34c4a1a8fd399a8f505fa3f43`
- [docker/NOTES_GB10.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/NOTES_GB10.md) · blob `4901b5a7904a43aac013d09a35faf3862d80f7aa`
- [docker/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/README.md) · blob `a5967bd6ad0131e8e66181ab5b80b8fba7813d45`
- [docker/amd_patch/latest/amd_megatron_fused_kernels_init.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/amd_patch/latest/amd_megatron_fused_kernels_init.patch) · blob `f6efca346dcebcd52ac8a7a611e6c7c02a074a59`
- [docker/amd_patch/latest/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/amd_patch/latest/megatron.patch) · blob `c840133cefd62824cb5610d15a1847e7ff28aff1`
- [docker/amd_patch/latest/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/amd_patch/latest/sglang.patch) · blob `990c2e628994734ef61edb3ad47c4ae0b3943f2f`
- [docker/amd_patch/sglv0.5.0rc0/amd_megatron_fused_kernels_init.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/amd_patch/sglv0.5.0rc0/amd_megatron_fused_kernels_init.patch) · blob `f6efca346dcebcd52ac8a7a611e6c7c02a074a59`
- [docker/amd_patch/sglv0.5.0rc0/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/amd_patch/sglv0.5.0rc0/megatron.patch) · blob `c840133cefd62824cb5610d15a1847e7ff28aff1`
- [docker/amd_patch/sglv0.5.0rc0/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/amd_patch/sglv0.5.0rc0/sglang.patch) · blob `990c2e628994734ef61edb3ad47c4ae0b3943f2f`
- [docker/justfile](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/justfile) · blob `166a2e900380cb444130c8898866cdb0670e9145`
- [docker/npu_patch/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/npu_patch/README.md) · blob `db93b67633f897c2466f5cb116b6cc7abd45e3fc`
- [docker/npu_patch/megatron-bridge.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/npu_patch/megatron-bridge.patch) · blob `3817097f4041aff5f6ecd1c96386ae6fe8b25dc5`
- [docker/npu_patch/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/npu_patch/megatron.patch) · blob `7687827db6b860a4e514434e9de72b93b2488aba`
- [docker/npu_patch/mindspeed.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/npu_patch/mindspeed.patch) · blob `0cf1c848403f0834d90a3243458e4d90091c3e55`
- [docker/npu_patch/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/npu_patch/sglang.patch) · blob `b684d3c0eb017fd65bbd8dae977c2498d4d2fe0f`
- [docker/npu_patch/slime.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/npu_patch/slime.patch) · blob `7b6222170403ea18b72a389168db88460335f7e5`
- [docker/patch/gb10/cuda_profiler_api.h](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/gb10/cuda_profiler_api.h) · blob `276b80b656fdc29638b4ef5769ac77887e1d94b8`
- [docker/patch/gb10/patch_sgl_kernel.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/gb10/patch_sgl_kernel.py) · blob `a6dc3bbebf5d4860c088139c31989989a1ffdbe3`
- [docker/patch/gb10/sgl-kernel-arch.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/gb10/sgl-kernel-arch.patch) · blob `a507e04c09f083943f114e8371c71ffcbf0604fe`
- [docker/patch/latest/megatron-sglang-aligned.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/latest/megatron-sglang-aligned.patch) · blob `8a688aa6fe3c034069eeac29eeceebb09bbd1738`
- [docker/patch/latest/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/latest/megatron.patch) · blob `f732021de498ceb8ecf7f4b0123f37108626ebb7`
- [docker/patch/latest/sglang-deterministic.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/latest/sglang-deterministic.patch) · blob `ad31f7a454eded660430dfdb596f288c83746dda`
- [docker/patch/latest/sglang-pull_weights.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/latest/sglang-pull_weights.patch) · blob `f308c4819ccf9b0f1a2c784211dc4d486664cab8`
- [docker/patch/latest/sglang-release_hicache.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/latest/sglang-release_hicache.patch) · blob `c8f6f9473fd3bc5929f9ec885f63a8a0a37a7850`
- [docker/patch/latest/sglang-top_p.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/latest/sglang-top_p.patch) · blob `fdf9d0d5d69fd6efb02b330572c1c50ee70482be`
- [docker/patch/latest/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/latest/sglang.patch) · blob `967585629a284dd5c89b735207477e19f8dd02e3`
- [docker/patch/v0.5.0rc0-cu126/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.0rc0-cu126/megatron.patch) · blob `95d59d284a05a21f464ea5afff9260f87fb8ea11`
- [docker/patch/v0.5.0rc0-cu126/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.0rc0-cu126/sglang.patch) · blob `990c2e628994734ef61edb3ad47c4ae0b3943f2f`
- [docker/patch/v0.5.12.post1/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.12.post1/megatron.patch) · blob `4b4c74d28e0144b144989ba1dc8a726125bc80ce`
- [docker/patch/v0.5.12.post1/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.12.post1/sglang.patch) · blob `861f2524606c5558165b3cf2fa3672e8b83a3bfe`
- [docker/patch/v0.5.15.post1/megatron-sglang-aligned.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.15.post1/megatron-sglang-aligned.patch) · blob `8a688aa6fe3c034069eeac29eeceebb09bbd1738`
- [docker/patch/v0.5.15.post1/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.15.post1/megatron.patch) · blob `f732021de498ceb8ecf7f4b0123f37108626ebb7`
- [docker/patch/v0.5.15.post1/sglang-deterministic.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.15.post1/sglang-deterministic.patch) · blob `ad31f7a454eded660430dfdb596f288c83746dda`
- [docker/patch/v0.5.15.post1/sglang-pull_weights.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.15.post1/sglang-pull_weights.patch) · blob `f308c4819ccf9b0f1a2c784211dc4d486664cab8`
- [docker/patch/v0.5.15.post1/sglang-release_hicache.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.15.post1/sglang-release_hicache.patch) · blob `c8f6f9473fd3bc5929f9ec885f63a8a0a37a7850`
- [docker/patch/v0.5.15.post1/sglang-top_p.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.15.post1/sglang-top_p.patch) · blob `fdf9d0d5d69fd6efb02b330572c1c50ee70482be`
- [docker/patch/v0.5.15.post1/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.15.post1/sglang.patch) · blob `967585629a284dd5c89b735207477e19f8dd02e3`
- [docker/patch/v0.5.5.post1/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.5.post1/megatron.patch) · blob `cca054d1e6c5220dcd4a0dd460cba17f370d2cbe`
- [docker/patch/v0.5.5.post1/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.5.post1/sglang.patch) · blob `5e0e72150d99b4dce5067748aee260b161817a40`
- [docker/patch/v0.5.6/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.6/megatron.patch) · blob `9d0d6011ce3c6e9a211625adebc40d084b1b3f24`
- [docker/patch/v0.5.6/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.6/sglang.patch) · blob `78bf161bc4f34fe6585f9245e31a990db2461989`
- [docker/patch/v0.5.7/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.7/megatron.patch) · blob `6d2a233949dffb96d167b3e5c5c4c23443c9b62a`
- [docker/patch/v0.5.7/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.7/sglang.patch) · blob `8c2b46fb739b40256b2e9c70eeb01b50d47380d7`
- [docker/patch/v0.5.9/megatron.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.9/megatron.patch) · blob `2e6ae436b1f1375d5dd7f87ba989ec951ae0efe1`
- [docker/patch/v0.5.9/sglang.patch](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/patch/v0.5.9/sglang.patch) · blob `e9145702e1a6c506cd1b10abf4871d5d6c080fc6`
- [docker/version.txt](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docker/version.txt) · blob `a7225e5e9718355b76b3233dbbe3f218c80d024d`

## docs

- [docs/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/README.md) · blob `08b978a0d7155e7bd5380abbad6b89ef596e3e95`
- [docs/_static/css/custom_log.css](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/css/custom_log.css) · blob `3edb005dfb7f286242901e9a1f3f3c4bbcf09a51`
- [docs/_static/css/readthedocs.css](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/css/readthedocs.css) · blob `aca6649b436a35cf39b2c924ce2f74ed2cdc8b90`
- [docs/_static/image/arch.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/image/arch.png) · blob `b809bd3ffee17e4c361c73a9cca454a849c3a8e8`
- [docs/_static/image/blogs/release_v0.1.0/cuda_vmm.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/image/blogs/release_v0.1.0/cuda_vmm.png) · blob `5bc852b9ed901dbadd6c4156ebad3f6c10d3164e`
- [docs/_static/image/blogs/release_v0.1.0/overrall.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/image/blogs/release_v0.1.0/overrall.png) · blob `ff0293ceb696fa8252dbd3626753069b02121b94`
- [docs/_static/image/logo.ico](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/image/logo.ico) · blob `78153d1e2f773763690ca0d60efb4328059f576b`
- [docs/_static/image/logo.jpg](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/image/logo.jpg) · blob `c1257d72b355bbee4172b77c07713bd968deba4f`
- [docs/_static/image/sglang_config.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/image/sglang_config.png) · blob `c4cde43ab238a708c8debd3eb40c71297ee5d9d9`
- [docs/_static/image/trace.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/image/trace.png) · blob `847f4009cbcb735719ecb3181266bb039cf22a9d`
- [docs/_static/js/lang-toggle.js](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/_static/js/lang-toggle.js) · blob `8ff31779fc10db74875c518573690c47cf4f5f76`
- [docs/build.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/build.sh) · blob `dd95b43a4377dc73f6d0a1151aed78bec9445487`
- [docs/build_all.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/build_all.sh) · blob `91ca957acf6725003ed9b3c997e6b9603f534c12`
- [docs/conf.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/conf.py) · blob `e5815fb04e9fd108457ec8a3921794bb8ca174bc`
- [docs/en/advanced/arch-support-beyond-megatron.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/arch-support-beyond-megatron.md) · blob `e6a1dbd4e7c3496f4b03f3a7bfca1c1c40958ac6`
- [docs/en/advanced/delta-weight-sync.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/delta-weight-sync.md) · blob `59d4b7b08cc0a4253dad8e56639651c32169d170`
- [docs/en/advanced/external-rollout-engines.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/external-rollout-engines.md) · blob `8efd245fd92ab627ce1752825bc6553da39a4a6b`
- [docs/en/advanced/fault-tolerance.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/fault-tolerance.md) · blob `321ba99efff66fa708f4d1061fd20974a6d2b7c3`
- [docs/en/advanced/low-precision.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/low-precision.md) · blob `5f0c970ba5b07f5cc2eec677662bf0b7a47d90a3`
- [docs/en/advanced/megatron-config.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/megatron-config.md) · blob `831082d64ebcfa634e788a13a64d23a9126308a4`
- [docs/en/advanced/observability.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/observability.md) · blob `3a4941dbc2a05ae94716801a57253724292aaf44`
- [docs/en/advanced/on-policy-distillation.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/on-policy-distillation.md) · blob `cfbc18ed5569ed0baa4b7a70d64a4f7ce8f266f8`
- [docs/en/advanced/pd-disaggregation.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/pd-disaggregation.md) · blob `085e1657b9ad6071d851e11a51ea7da684e59763`
- [docs/en/advanced/reproducibility.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/reproducibility.md) · blob `710a0b2af2ecccaa4abff5a9e6cdcbd3ff37d59d`
- [docs/en/advanced/sglang-config.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/sglang-config.md) · blob `62e71c1c8c8d77db6ca6b4bd554b3d663c7e4e8b`
- [docs/en/advanced/speculative-decoding.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/speculative-decoding.md) · blob `bfca86936d508ab4586a2d2be20dfa282ae08309`
- [docs/en/advanced/straw.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/advanced/straw.md) · blob `0bc2e59fd4792f1ce7754cffefe78cec287ca593`
- [docs/en/blogs/introducing_slime.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/blogs/introducing_slime.md) · blob `6f9dae7c2902d754f1bc52793b4a5dd4fc018166`
- [docs/en/blogs/release_v0.1.0.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/blogs/release_v0.1.0.md) · blob `2a1b93e6e82eaad7577a8a68ed31ad9e4b1d6ae0`
- [docs/en/developer_guide/ci.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/developer_guide/ci.md) · blob `67b0745287cda8a4ac2b09f67d427a66203a9839`
- [docs/en/developer_guide/debug.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/developer_guide/debug.md) · blob `e09a3751cda4e9ff0bbcc2ad3bd1c266fb9f552a`
- [docs/en/developer_guide/install_flashqla.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/developer_guide/install_flashqla.md) · blob `53e8a111e1c4fbc44a6d83faa0cd2bcf75aefb97`
- [docs/en/developer_guide/profiling.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/developer_guide/profiling.md) · blob `93b8ea5b39b908b54c41718dee28aeebe6e816af`
- [docs/en/developer_guide/trace.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/developer_guide/trace.md) · blob `604efa6564c620a10374253fb0150f2b25cf6a01`
- [docs/en/examples/deepseek-r1.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/deepseek-r1.md) · blob `ab10502eec20d5c920abc723e8c862697c5dad7e`
- [docs/en/examples/glm4-9B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/glm4-9B.md) · blob `4a934ee144690a3bb83c34d71d4e3480559c368a`
- [docs/en/examples/glm4.7-30B-A3B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/glm4.7-30B-A3B.md) · blob `7e52f51bc00029d3b659ff24db5f48d53790e47f`
- [docs/en/examples/glm4.7-355B-A32B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/glm4.7-355B-A32B.md) · blob `b6337a1d59657d1a4d5b733f846444f45971693c`
- [docs/en/examples/glm5.2-744B-A40B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/glm5.2-744B-A40B.md) · blob `8e3c7f8d30d085a380634e79621374bcef25b49f`
- [docs/en/examples/qwen3-30B-A3B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/qwen3-30B-A3B.md) · blob `04d973adfd70acf0aec2833c67b1f06f43ae2dc1`
- [docs/en/examples/qwen3-4B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/qwen3-4B.md) · blob `d0945f61a919a7103d645908b6f7f7df91fd7227`
- [docs/en/examples/qwen3-4b-base-openhermes.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/qwen3-4b-base-openhermes.md) · blob `550c45788dc90a86df28387be3a0520675264a9f`
- [docs/en/examples/qwen3-next-80B-A3B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/examples/qwen3-next-80B-A3B.md) · blob `5f0e24f01b49c43ec300f6944ff9e51c3e5527db`
- [docs/en/get_started/agent.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/get_started/agent.md) · blob `5ea9f07da805a7f71c8b834fe5083ee89e2c0f5c`
- [docs/en/get_started/customization.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/get_started/customization.md) · blob `83dac3bbe2a55f760c93d38d4f922b56bb1cac27`
- [docs/en/get_started/qa.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/get_started/qa.md) · blob `2344e4b1c962fec2345af177135342f9709f5a00`
- [docs/en/get_started/quick_start.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/get_started/quick_start.md) · blob `fed01f519fc312eee31104c474173bbad66d2406`
- [docs/en/get_started/usage.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/get_started/usage.md) · blob `57a319c869a1d6e0557a7ef13a5266c874fe31b3`
- [docs/en/index.rst](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/index.rst) · blob `c496583ede1ccf0612dd73b864a2238b82c41327`
- [docs/en/platform_support/amd_tutorial.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/en/platform_support/amd_tutorial.md) · blob `8597ac17012233986dc7872bb18770b777c9355f`
- [docs/requirements.txt](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/requirements.txt) · blob `76ec912a2eee016a47e5f47999b33dde77868152`
- [docs/serve.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/serve.sh) · blob `ae739852824d483138459e73e8f706c995e327b5`
- [docs/zh/advanced/arch-support-beyond-megatron.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/arch-support-beyond-megatron.md) · blob `06c03c7a4bd439cc7803e369c7430499e091c05e`
- [docs/zh/advanced/delta-weight-sync.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/delta-weight-sync.md) · blob `f384f475e0d7d91b3efe9695d81899eb30c2a689`
- [docs/zh/advanced/external-rollout-engines.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/external-rollout-engines.md) · blob `53b4571b1011d36ba6f95ce64818f91180986b6f`
- [docs/zh/advanced/fault-tolerance.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/fault-tolerance.md) · blob `4914a0cf6c4f25b0f844372943ce07c405622622`
- [docs/zh/advanced/low-precision.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/low-precision.md) · blob `0459b87f3b9252ce21defbcd201f43d82188a18c`
- [docs/zh/advanced/megatron-config.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/megatron-config.md) · blob `d873ab1bc12aec52c2265c8f555e13812774a762`
- [docs/zh/advanced/observability.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/observability.md) · blob `01a10f35cdcab03229d6f8b6ef47f17537a1b879`
- [docs/zh/advanced/on-policy-distillation.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/on-policy-distillation.md) · blob `91a739b25dc1cdb9a51eb80d6208c3ecc34c433f`
- [docs/zh/advanced/pd-disaggregation.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/pd-disaggregation.md) · blob `d9d9e2ddb89f371b21323b530556a452698db0c8`
- [docs/zh/advanced/reproducibility.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/reproducibility.md) · blob `f3e1274c93fa3647a87f76687cf28c06242bee5f`
- [docs/zh/advanced/sglang-config.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/sglang-config.md) · blob `7be825a5e6a6d737064ced75d045d3bac531c3a1`
- [docs/zh/advanced/speculative-decoding.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/speculative-decoding.md) · blob `c2508be2272bfa21401d46583fba3439b3c9983d`
- [docs/zh/advanced/straw.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/advanced/straw.md) · blob `032fe1d29cd164d21ff696e4daf0ca5a79cb3b1a`
- [docs/zh/blogs/introducing_slime.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/blogs/introducing_slime.md) · blob `5c779e394aeeed65a69be0734d87fa889374925f`
- [docs/zh/blogs/release_v0.1.0.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/blogs/release_v0.1.0.md) · blob `ff95a7e3cbe73a9b172b6ff9972452ea4edc51ca`
- [docs/zh/developer_guide/ci.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/developer_guide/ci.md) · blob `6a17e088f68d7788c0deaf9a7fd2dcc5b8ab95cb`
- [docs/zh/developer_guide/debug.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/developer_guide/debug.md) · blob `2e8674cbbe6ea00db0af220fe832365789be3646`
- [docs/zh/developer_guide/install_flashqla.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/developer_guide/install_flashqla.md) · blob `ece493d79a9cf34f8009c5a2387d83cf45893b1b`
- [docs/zh/developer_guide/profiling.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/developer_guide/profiling.md) · blob `11609ec555ed9d5fb67367877095ebf8da61a16e`
- [docs/zh/developer_guide/trace.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/developer_guide/trace.md) · blob `ab2afe016dc4ec3866d7d153d04cfaf27b8087a0`
- [docs/zh/examples/deepseek-r1.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/deepseek-r1.md) · blob `368653844d55ed580a29674aaaafb55605a66caf`
- [docs/zh/examples/glm4-9B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/glm4-9B.md) · blob `a6389f13cdc10e2cf742e77c59e9dead8120ee33`
- [docs/zh/examples/glm4.7-30B-A3B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/glm4.7-30B-A3B.md) · blob `9ecc832912d3b9f23ea553a0d2a3d53856e8cc84`
- [docs/zh/examples/glm4.7-355B-A32B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/glm4.7-355B-A32B.md) · blob `f6bafcd70902d3099ebe28c2a466210fcce5d541`
- [docs/zh/examples/glm5.2-744B-A40B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/glm5.2-744B-A40B.md) · blob `3c7712022b29d458fa161e63fdd034d9e00846e0`
- [docs/zh/examples/qwen3-30B-A3B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/qwen3-30B-A3B.md) · blob `8413d1d1aaf9eabe956d94c0772f6b34c48ed0eb`
- [docs/zh/examples/qwen3-4B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/qwen3-4B.md) · blob `a11ad12abd0bba3b2fc36ee5b15575ca6bd94c17`
- [docs/zh/examples/qwen3-4b-base-openhermes.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/qwen3-4b-base-openhermes.md) · blob `043586370f74d0dc8cb270caceca1c7d799f6c95`
- [docs/zh/examples/qwen3-next-80B-A3B.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/examples/qwen3-next-80B-A3B.md) · blob `2ca2c7651a157434a58834ab794311c27e4bd13b`
- [docs/zh/get_started/agent.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/get_started/agent.md) · blob `14cf80c01e0c0e5541887cba9cfb9c1e1000893f`
- [docs/zh/get_started/customization.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/get_started/customization.md) · blob `f94bbf06579aed8fe45379836cb17d619932aaf5`
- [docs/zh/get_started/qa.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/get_started/qa.md) · blob `05c73890bc7faa19fbdf68cdd4032486edca0683`
- [docs/zh/get_started/quick_start.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/get_started/quick_start.md) · blob `99501bb37972b68192a8d542deb7693b967074b4`
- [docs/zh/get_started/usage.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/get_started/usage.md) · blob `8828ed260190a23fe849cbf5e666b840a411ad0a`
- [docs/zh/index.rst](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/index.rst) · blob `c4d391381907b851a84fbb578119c83b4d78d6b2`
- [docs/zh/platform_support/amd_tutorial.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/docs/zh/platform_support/amd_tutorial.md) · blob `c142fe6b4f60d5d25920d5c87707c22c468098de`

## examples

- [examples/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/README.md) · blob `abbd8888e769b088d539e6234792156fffd69d40`
- [examples/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [examples/coding_agent_rl/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/coding_agent_rl/README.md) · blob `cc1956383011cd1cc49ff802c155227a0301d093`
- [examples/coding_agent_rl/generate.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/coding_agent_rl/generate.py) · blob `34a10a931cab340e00842e324272378ebf6e9ef9`
- [examples/coding_agent_rl/run_qwen36_35b_a3b_swe_8nodes.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/coding_agent_rl/run_qwen36_35b_a3b_swe_8nodes.sh) · blob `99f9200391214ab7806c78c54ee45339ce6b222a`
- [examples/coding_agent_rl/swe.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/coding_agent_rl/swe.py) · blob `06a453c4a9f1f8fc58a2ad6be1b690c600f73559`
- [examples/delta_weight_sync/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/delta_weight_sync/README.md) · blob `60d826153ba3f7ccf2b3f8edb35935a8115ca4a9`
- [examples/delta_weight_sync/run-glm4.7-30B-A3B-delta.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/delta_weight_sync/run-glm4.7-30B-A3B-delta.sh) · blob `32996f79ad83aebc2ead1abfd903345f99c5980d`
- [examples/eval_multi_task/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/eval_multi_task/README.md) · blob `0bf61ec7294e7f5dfb44710f02eade5f4465fb8e`
- [examples/eval_multi_task/multi_task.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/eval_multi_task/multi_task.sh) · blob `8d4fe1994cde61902574806772dc5f637dbfd65b`
- [examples/eval_multi_task/multi_task.yaml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/eval_multi_task/multi_task.yaml) · blob `bad2d61412f61897bb47d5693a26c70d0efcde7a`
- [examples/eval_multi_task/requirements_ifbench.txt](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/eval_multi_task/requirements_ifbench.txt) · blob `78f13fac47749ca3ec7ad4f7c1af9197d7274ac9`
- [examples/fully_async/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/fully_async/README.md) · blob `1c1208ed50cf93878f192b60369621d78b9a8178`
- [examples/fully_async/run-qwen2.5-0.5B-fully_async.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/fully_async/run-qwen2.5-0.5B-fully_async.sh) · blob `1472224ec29033335cdad196806a04414b90e9f6`
- [examples/fully_async/run-qwen3.5-9B-fully_async.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/fully_async/run-qwen3.5-9B-fully_async.sh) · blob `1b0e30d07610ca9027edc52267eed32c0a11c1b6`
- [examples/geo3k_vlm/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm/README.md) · blob `a073e03f1078a404f80e71f11bdfd15160ca9a68`
- [examples/geo3k_vlm/fsdp_vs_megatron.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm/fsdp_vs_megatron.png) · blob `5c32e414b84f4ea43b94c55f0f2081abfd0b407c`
- [examples/geo3k_vlm/run_geo3k_qwen35.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm/run_geo3k_qwen35.sh) · blob `152878cd62ca4ed5b04b146dadf83cebad3155f4`
- [examples/geo3k_vlm_multi_turn/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/README.md) · blob `dad14e354f729c6d68ce2886bb2c42b346d58b31`
- [examples/geo3k_vlm_multi_turn/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/__init__.py) · blob `526e3ae7c68160bbb147ce00121c876b6e76ec70`
- [examples/geo3k_vlm_multi_turn/base_env.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/base_env.py) · blob `05d9632b37e001d83630c40c600f4c095f053d20`
- [examples/geo3k_vlm_multi_turn/env_geo3k.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/env_geo3k.py) · blob `3fdf0cfd56374e65ede779f9f2ac766ef8689919`
- [examples/geo3k_vlm_multi_turn/geo3k_vlm_multi_turn_config.yaml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/geo3k_vlm_multi_turn_config.yaml) · blob `ad2dd6feff40f805006ea76a5f2253bcff4ceaf9`
- [examples/geo3k_vlm_multi_turn/geo3k_vlm_multi_turn_reward.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/geo3k_vlm_multi_turn_reward.png) · blob `88851bb461bda64034846c98c3f37e29fd76ebe8`
- [examples/geo3k_vlm_multi_turn/rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/rollout.py) · blob `f0cc076c5db37e77b9f0965d6c8f34a2dd86f99d`
- [examples/geo3k_vlm_multi_turn/rollout_experiment_result_megatron.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/rollout_experiment_result_megatron.png) · blob `dd249de2952016e460aa946cd28b7bd3f757d848`
- [examples/geo3k_vlm_multi_turn/run_geo3k_vlm_multi_turn.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/geo3k_vlm_multi_turn/run_geo3k_vlm_multi_turn.py) · blob `49906c0d846e1412cbab9dbd62241780eb263906`
- [examples/multi_agent/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/multi_agent/README.md) · blob `c91aa8df1a8ecc38c80d97c5750ea045ce1cf4c4`
- [examples/multi_agent/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/multi_agent/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [examples/multi_agent/agent_system.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/multi_agent/agent_system.py) · blob `e83b12b369a6882f2d205ac52c4c473aa3da21df`
- [examples/multi_agent/prompts.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/multi_agent/prompts.py) · blob `a79047258fd8ac597a9799a3a8e0bfed241902ac`
- [examples/multi_agent/rollout_with_multi_agents.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/multi_agent/rollout_with_multi_agents.py) · blob `4b57d74881e29450ec06378eeb533625cc50ee35`
- [examples/multi_agent/run-qwen3-30B-A3B-multi-agent.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/multi_agent/run-qwen3-30B-A3B-multi-agent.sh) · blob `d065b9101f0f4ee01e6aa6bfd5eec1dbac52c2be`
- [examples/on_policy_distillation/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/on_policy_distillation/README.md) · blob `05fcf658c6bde1602d49d020052b87782af05326`
- [examples/on_policy_distillation/run-qwen3-8B-opd-megatron.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/on_policy_distillation/run-qwen3-8B-opd-megatron.sh) · blob `2f798a7550caf6c292c338a1682b69cd9b4cef2c`
- [examples/on_policy_distillation/run-qwen3-8B-opd.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/on_policy_distillation/run-qwen3-8B-opd.sh) · blob `3fdc479b1613ca2ed02fde9312c3ada9cf5e23b4`
- [examples/retool/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/retool/README.md) · blob `73a0e736219e5a832ac0c0e9a9f442e3351be23a`
- [examples/retool/generate_with_retool.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/retool/generate_with_retool.py) · blob `ebb5c4f1a64baa1e1569952df96f6e1634de3989`
- [examples/retool/requirements.txt](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/retool/requirements.txt) · blob `154747336b3c93587090f7eb16ca5b63cb99d3cb`
- [examples/retool/retool_qwen3_4b_rl.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/retool/retool_qwen3_4b_rl.sh) · blob `32a837f394b402ad1deed2f45dda7fe5a6e5e002`
- [examples/retool/retool_qwen3_4b_sft.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/retool/retool_qwen3_4b_sft.sh) · blob `01ecdf96f36de7d969393328470b6eeefc4a8879`
- [examples/retool/rl_data_preprocess.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/retool/rl_data_preprocess.py) · blob `548b74468576bc1ace53aed90a587f8845bd7990`
- [examples/retool/sft_data_processing.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/retool/sft_data_processing.py) · blob `96790af1e9c73f30cf657fae78da6251334c9ec3`
- [examples/retool/tool_sandbox.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/retool/tool_sandbox.py) · blob `cdf68aa020714d206791d4fb257e45999f0cfdc6`
- [examples/search-r1/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/README.md) · blob `973030e9eb783199c46f55d04dbb01d23b688077`
- [examples/search-r1/README_zh.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/README_zh.md) · blob `5a7b9ad282b35145c7ab2506ef8d9b9467ef993c`
- [examples/search-r1/generate_with_search.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/generate_with_search.py) · blob `ae0f18dd15be8fd78715cc1be43b1df637032b9d`
- [examples/search-r1/google_search_server.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/google_search_server.py) · blob `3ddfff8142e9d8464217baf40074be6c4f0b9ed7`
- [examples/search-r1/local_dense_retriever/download.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/local_dense_retriever/download.py) · blob `6fe554936fafc57ada63198fadd4f30af0de8b8a`
- [examples/search-r1/local_dense_retriever/retrieval_server.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/local_dense_retriever/retrieval_server.py) · blob `f8733582ea00d729014e063f452b223f7298e4d2`
- [examples/search-r1/local_search_server.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/local_search_server.py) · blob `0e5c814a7bca2c7376432d31bcbc9b61784c98b7`
- [examples/search-r1/qa_em_format.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/qa_em_format.py) · blob `330f9c9256909c71e4f87ed0e34656f829c08eab`
- [examples/search-r1/run_qwen2.5_3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/search-r1/run_qwen2.5_3B.sh) · blob `2f2fdc444de7847bd5560a00fc997512b2cb32c8`
- [examples/strands_sglang/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/strands_sglang/README.md) · blob `f6978fa8c6511c9b7e80d19af5ff5bc62c6bbf04`
- [examples/strands_sglang/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/strands_sglang/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [examples/strands_sglang/generate_with_strands.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/strands_sglang/generate_with_strands.py) · blob `d62ee79780112369ab0e5876892a7180c8916b1a`
- [examples/strands_sglang/strands_qwen3_8b.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/strands_sglang/strands_qwen3_8b.sh) · blob `5f7af4f7515b327b5c4217f4d72f3d671efc03ef`
- [examples/strands_sglang/subprocess_interpreter.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/strands_sglang/subprocess_interpreter.py) · blob `b6e04937672b09879e0cd23d1618581e669d674b`
- [examples/tau-bench/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/tau-bench/README.md) · blob `f9e3879800775b58700003ba22b45db0c669ee62`
- [examples/tau-bench/generate_with_tau.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/tau-bench/generate_with_tau.py) · blob `42e69cd9738326bcf73ed04f84de3dc45a3361f8`
- [examples/tau-bench/openai_tool_adapter.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/tau-bench/openai_tool_adapter.py) · blob `b580f28b20534d77e26fd7f41b98034ff9140d2b`
- [examples/tau-bench/run_qwen3_4B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/tau-bench/run_qwen3_4B.sh) · blob `12bdb270eda2bfcecef3302af0590c82bb33b293`
- [examples/tau-bench/sglang_tool_parser.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/tau-bench/sglang_tool_parser.py) · blob `ea4f380ba1aec8dc84f30c7a2ef5af030954dd87`
- [examples/tau-bench/tau1_mock.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/tau-bench/tau1_mock.py) · blob `74ed424a75c5a56c852d76a06f1a8a3f61e55c6b`
- [examples/tau-bench/token_delta.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/tau-bench/token_delta.py) · blob `b78023d8cec3a38959711baa5512b99f3161240b`
- [examples/tau-bench/trainable_agents.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/tau-bench/trainable_agents.py) · blob `effc5d7a661ce328c40bedb3e9a39a594dc07735`
- [examples/train_infer_mismatch_helper/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/train_infer_mismatch_helper/README.md) · blob `e9430711483c109f3617fbc2d55960e1cb637578`
- [examples/train_infer_mismatch_helper/mis.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/train_infer_mismatch_helper/mis.py) · blob `3bbf5cf26edb36eb6581627ea64ff3542e5726e0`
- [examples/train_infer_mismatch_helper/mis.yaml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/train_infer_mismatch_helper/mis.yaml) · blob `bd285979edb2ab47cfafe57d62bfa44903b0b745`
- [examples/train_infer_mismatch_helper/run-qwen3-4b-mis.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/examples/train_infer_mismatch_helper/run-qwen3-4b-mis.sh) · blob `14a7011e03daa36b3e46ded591df6b6aa3a204a1`

## imgs

- [imgs/arch.png](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/imgs/arch.png) · blob `b809bd3ffee17e4c361c73a9cca454a849c3a8e8`

## pyproject.toml

- [pyproject.toml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/pyproject.toml) · blob `28cf1de9dd3543fcc4b68df4b689992462929a63`

## requirements.txt

- [requirements.txt](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/requirements.txt) · blob `bc17c72f10196383a7d17bf3b6c667f9725d687d`

## scripts

- [scripts/low_precision/run-kimi-k2-Thinking-int4.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/low_precision/run-kimi-k2-Thinking-int4.sh) · blob `c11779e0375ba7c84803bfa7b2a22fb926d34060`
- [scripts/low_precision/run-moonlight-16B-A3B-int4.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/low_precision/run-moonlight-16B-A3B-int4.sh) · blob `2218df3cbe924633382a9302ff37a8224008cd65`
- [scripts/low_precision/run-qwen3-235B-A22B-int4.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/low_precision/run-qwen3-235B-A22B-int4.sh) · blob `6d41eabd85c2504fd4b7fc0c2bae9b96d32c5665`
- [scripts/low_precision/run-qwen3-30B-A3B-int4.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/low_precision/run-qwen3-30B-A3B-int4.sh) · blob `30cbcb5b840afb4797712168dbaf87953ee582b6`
- [scripts/low_precision/run-qwen3-30b-a3b-fp8.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/low_precision/run-qwen3-30b-a3b-fp8.sh) · blob `402076e64b6762e93570dd427d458a749cc3fae0`
- [scripts/low_precision/run-qwen3-4b-fp8.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/low_precision/run-qwen3-4b-fp8.sh) · blob `eccf2872d89badcadd3a20d853d22a175ad02476`
- [scripts/models/deepseek-v3-20layer.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/deepseek-v3-20layer.sh) · blob `6fdde1820c8c850236a10494e6cea8bfb0c36d34`
- [scripts/models/deepseek-v3-5layer.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/deepseek-v3-5layer.sh) · blob `a5e5d2522ce83e23ce693a584bc98ee69c0d50ea`
- [scripts/models/deepseek-v3.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/deepseek-v3.sh) · blob `8c50d2c9405ce2553b4174ad541cc10b02b4669b`
- [scripts/models/glm4-32B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/glm4-32B.sh) · blob `a9c3e00616248e0807dbaebb3e876d897aee8494`
- [scripts/models/glm4-9B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/glm4-9B.sh) · blob `d1e02936549a00ebb81b3a6d0c87d5901e69d61f`
- [scripts/models/glm4.5-106B-A12B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/glm4.5-106B-A12B.sh) · blob `6bab15b77f70d4863e32246590db555cb371ee6a`
- [scripts/models/glm4.5-355B-A32B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/glm4.5-355B-A32B.sh) · blob `8aca21fd47566cf408e289b1cdd3c3ff69b1f9a1`
- [scripts/models/glm4.7-30B-A3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/glm4.7-30B-A3B.sh) · blob `696eb9bcfe54724dde2b2a2fd9152c2ac64f4767`
- [scripts/models/glm5-744B-A40B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/glm5-744B-A40B.sh) · blob `0afd676a7e6fcbc47b4775a87ba0ecacafcd9d56`
- [scripts/models/glm5.2-744B-A40B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/glm5.2-744B-A40B.sh) · blob `bd39c9359475d37438dc36d5c376b49272929035`
- [scripts/models/kimi-k2-thinking.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/kimi-k2-thinking.sh) · blob `b7fceda5913f48aaea287733b1b4ed447d445ae7`
- [scripts/models/kimi-k2.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/kimi-k2.sh) · blob `eafb7acadd11b2d470265ca845000b943e87cee3`
- [scripts/models/llama3.1-8B-Instruct.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/llama3.1-8B-Instruct.sh) · blob `0815b3e0a343bf644e7b8629aec6743f53a12b39`
- [scripts/models/llama3.2-3B-Instruct-amd.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/llama3.2-3B-Instruct-amd.sh) · blob `654de5a38652675918c5669d2f9375d40f7b2779`
- [scripts/models/llama3.2-3B-Instruct.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/llama3.2-3B-Instruct.sh) · blob `ff50130c8a706af8c0560b848e43cd0dad63261d`
- [scripts/models/mimo-7B-rl.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/mimo-7B-rl.sh) · blob `22366935f9913e125f8976b66998d2e60006ee2c`
- [scripts/models/minimax-m2.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/minimax-m2.sh) · blob `390eb03fab51f77ff2491d47f28550dec719d957`
- [scripts/models/moonlight.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/moonlight.sh) · blob `bcce99892a790eee372880d40024939c7b141800`
- [scripts/models/qwen2.5-0.5B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen2.5-0.5B.sh) · blob `66d5b29a024d52dfc6ca9cfe0bb3aa18391089cf`
- [scripts/models/qwen2.5-1.5B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen2.5-1.5B.sh) · blob `b046a95c66b4015ff9212ef1aa5d964bd8f07a12`
- [scripts/models/qwen2.5-32B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen2.5-32B.sh) · blob `26b49845a417baa9ff74c1b1eb3db0dc61eaa49c`
- [scripts/models/qwen2.5-3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen2.5-3B.sh) · blob `9da5a9e0339ffba6d162acd8c4dffa88a263778f`
- [scripts/models/qwen2.5-7B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen2.5-7B.sh) · blob `eba912b1d7c93e242ba7d4909583916815be1a67`
- [scripts/models/qwen3-0.6B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-0.6B.sh) · blob `f484ec9519bc7615d2e4a3497ad1292c65e4dc6e`
- [scripts/models/qwen3-1.7B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-1.7B.sh) · blob `7435996337e97b341ec93160ac7caf510ed93a0d`
- [scripts/models/qwen3-14B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-14B.sh) · blob `11b9377da005fb482a651d4aa531d05cfdeebd7d`
- [scripts/models/qwen3-235B-A22B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-235B-A22B.sh) · blob `1f6635526539b310a2162be4b57f440b6a258009`
- [scripts/models/qwen3-30B-A3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-30B-A3B.sh) · blob `dfab8682abb2489e24c67748581399000247e030`
- [scripts/models/qwen3-32B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-32B.sh) · blob `e7407e327c9ca416f999db35d8e1dad25e6619b9`
- [scripts/models/qwen3-4B-Instruct-2507.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-4B-Instruct-2507.sh) · blob `67d13c0c82384d5eafc361a0a52202aef0cef7a1`
- [scripts/models/qwen3-4B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-4B.sh) · blob `51f9e47581e8d113711e8f5026f6d27d908ce8be`
- [scripts/models/qwen3-8B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-8B.sh) · blob `fc573adb37bb42f0837aabb6cdbb9525f44a581f`
- [scripts/models/qwen3-next-80B-A3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3-next-80B-A3B.sh) · blob `74e4e02ed84b485e18ef8eb2785c16f70cecbece`
- [scripts/models/qwen3.5-0.8B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3.5-0.8B.sh) · blob `c235c4c1f67b455d6519a636d3e62cebecbe034d`
- [scripts/models/qwen3.5-27B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3.5-27B.sh) · blob `ffa6ab178745c5fe197f123fd48c2ef6ec2f55dc`
- [scripts/models/qwen3.5-35B-A3B-vl.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3.5-35B-A3B-vl.sh) · blob `381d577723daa9b902e3422883134d647210ee0a`
- [scripts/models/qwen3.5-35B-A3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3.5-35B-A3B.sh) · blob `c3cb7219bba7f4df25ee800dfbefc781d3f6c204`
- [scripts/models/qwen3.5-4B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3.5-4B.sh) · blob `18bea47c9c41d2ec0b5afe1b64337d57e4fc820f`
- [scripts/models/qwen3.5-9B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/models/qwen3.5-9B.sh) · blob `cca6d6c29dca73b025c3e572687d0575398133fe`
- [scripts/run-deepseek-r1.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-deepseek-r1.sh) · blob `8c4c7de0ea5b4c8713b66658b36db4182ff7465f`
- [scripts/run-glm4-9B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-glm4-9B.sh) · blob `72e67d0866590f2bf0c4d2c361334045b2a31ac7`
- [scripts/run-glm4.7-30B-A3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-glm4.7-30B-A3B.sh) · blob `62c093c6e0c6463fc82d103c5ed603ce943ca814`
- [scripts/run-glm4.7-355B-A32B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-glm4.7-355B-A32B.sh) · blob `5c8a28929898875aca1224706042688abf51b458`
- [scripts/run-glm5-744B-A40B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-glm5-744B-A40B.sh) · blob `63c6601c3c41b0fdfe5e7e50f96fd2d3e80fdbad`
- [scripts/run-glm5.2-744B-A40B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-glm5.2-744B-A40B.sh) · blob `c2bd2bc7ac82dbde97564a5b1715050e90da7782`
- [scripts/run-kimi-k2-Instruct.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-kimi-k2-Instruct.sh) · blob `8b7d051a4b620fe3c821884a626808742c06bb29`
- [scripts/run-kimi-k2-Thinking.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-kimi-k2-Thinking.sh) · blob `beb8bf866b93b97a9f9831bbd11b6929eafbf98f`
- [scripts/run-mimo-7B-rl-eagle.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-mimo-7B-rl-eagle.sh) · blob `ed631c77b6f85c42d3e4adb44d7c1f500c4befe7`
- [scripts/run-minimax-m2.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-minimax-m2.sh) · blob `4653a60389c82949d6a93b3a52d16c604ac3b4e0`
- [scripts/run-moonlight-16B-A3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-moonlight-16B-A3B.sh) · blob `1f54f81d166c6f73cb7a0290c82ab45d92e5ad66`
- [scripts/run-qwen2.5-0.5B-gb10-smoke.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen2.5-0.5B-gb10-smoke.sh) · blob `7a379b9614d288d1bd0fc1e8e725da18ca526433`
- [scripts/run-qwen2.5-0.5B-reproducibility.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen2.5-0.5B-reproducibility.sh) · blob `446eca65e108f8e15aa8e4b6293818186210b56c`
- [scripts/run-qwen3-235B-A22B-sft.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3-235B-A22B-sft.sh) · blob `f458c9e6e7c2e69e12df8e943f97cf39d2c7ec5a`
- [scripts/run-qwen3-235B-A22B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3-235B-A22B.sh) · blob `cf2eef9fc4a7684303b4c54e6ac9a43dc3a95367`
- [scripts/run-qwen3-30B-A3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3-30B-A3B.sh) · blob `b2d01df6d3bce1bde6d567029d49ea6c6a245627`
- [scripts/run-qwen3-32B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3-32B.sh) · blob `4d870ca391fb55e219943ec754e5d155446bfe00`
- [scripts/run-qwen3-4B-amd.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3-4B-amd.sh) · blob `d31abacdf0fa194709d2363cd525a4e9c9ebfeae`
- [scripts/run-qwen3-4B-base-sft.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3-4B-base-sft.sh) · blob `76f263cd4f80b2c19badaf50d137699dd841f39e`
- [scripts/run-qwen3-4B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3-4B.sh) · blob `ec06a8f525cd7d1940bd337e595d6d50c224706d`
- [scripts/run-qwen3-next-80B-A3B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3-next-80B-A3B.sh) · blob `6600bf13bfeba583c20f1f5ddc7bf41a8cc6ca98`
- [scripts/run-qwen3.5-27B.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3.5-27B.sh) · blob `28d4ba21850a8716811c8097ee0b32dc76488ce5`
- [scripts/run-qwen3.5-35B-A3B-sft.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/scripts/run-qwen3.5-35B-A3B-sft.sh) · blob `1b8618dd57ae344826269be7f67175be8b5684f5`

## setup.py

- [setup.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/setup.py) · blob `56fb62d9802bd5330f70a936af86a5cc3527866c`

## slime

- [slime/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/agent/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/__init__.py) · blob `1048d52b8a7c1f70fdec3483219ffbe8c75e46f3`
- [slime/agent/adapters/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/adapters/__init__.py) · blob `d5bb725ea9df36c510f1d6308878399472cbe559`
- [slime/agent/adapters/anthropic.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/adapters/anthropic.py) · blob `0a48b09fd5e7d7b1f7b36ead5bf11c2550d4f955`
- [slime/agent/adapters/common.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/adapters/common.py) · blob `05f2cc6f9ab0d4b2493272d4ce4429df5e40eb7e`
- [slime/agent/adapters/openai.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/adapters/openai.py) · blob `ad3d2e4d8739275edc11753718c415d9da1b5e30`
- [slime/agent/aiohttp_threaded.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/aiohttp_threaded.py) · blob `ad5fa0ccb841e0b47c3be1ffafa3f7ba1d3d8bdb`
- [slime/agent/harness/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/harness/__init__.py) · blob `caac42b06679134c9b271c5ade6e05db29045f61`
- [slime/agent/harness/claude_code.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/harness/claude_code.py) · blob `f1ba2a0b86d4ad35a9da554043bf1882c99df713`
- [slime/agent/harness/codex.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/harness/codex.py) · blob `a0afddb8a93425d567601860f36e44f6f01af4dd`
- [slime/agent/harness/common.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/harness/common.py) · blob `b81486c949a344e120caf4ca18e780af9e24bca7`
- [slime/agent/parsing.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/parsing.py) · blob `56bc85a4bc78634c18f59eb9c5c630cd4343550a`
- [slime/agent/sandbox.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/sandbox.py) · blob `2b888127803ec47dfa109a5dfbdfae8b37c14e22`
- [slime/agent/trajectory.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/agent/trajectory.py) · blob `a2791f36ce579b4465a98967a97f0168bb4d075b`
- [slime/backends/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/__init__.py) · blob `8b137891791fe96927ad78e64b0aad7bded08bdc`
- [slime/backends/megatron_utils/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/__init__.py) · blob `55372a8641487dafd01b4a7e51fa1e226710f6cc`
- [slime/backends/megatron_utils/actor.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/actor.py) · blob `d1146a15dbeece783dfaf42c6636c0d5ca1a896c`
- [slime/backends/megatron_utils/alignment/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/alignment/__init__.py) · blob `682d8170be9696def3c57473c38ecef535da6ce9`
- [slime/backends/megatron_utils/alignment/deepgemm_forward.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/alignment/deepgemm_forward.py) · blob `0f493158e0ee9144aa2041731e3cdaf19441b3a0`
- [slime/backends/megatron_utils/alignment/deepgemm_moe_forward.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/alignment/deepgemm_moe_forward.py) · blob `30e9640e1775e762a7a6b18be62add563108003f`
- [slime/backends/megatron_utils/alignment/deterministic_route_kernels.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/alignment/deterministic_route_kernels.py) · blob `1bd2127a1b9804a56c378ab3982a4c78d9b48499`
- [slime/backends/megatron_utils/alignment/env.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/alignment/env.py) · blob `5a249d2828865a688afe67bca62aa37c9c3270a2`
- [slime/backends/megatron_utils/alignment/layerwise_alignment.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/alignment/layerwise_alignment.py) · blob `a9eaf477603da203d5fdef97f9b7bfa1e507e428`
- [slime/backends/megatron_utils/arguments.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/arguments.py) · blob `7b471144b6afa9541488a12f143c3a08191db465`
- [slime/backends/megatron_utils/checkpoint.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/checkpoint.py) · blob `4b0e372eb04761b7bae1e4ef13549d70fe05874b`
- [slime/backends/megatron_utils/ci_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/ci_utils.py) · blob `e6ce784ca2a37bed71091f6223217e7333b7d4c0`
- [slime/backends/megatron_utils/cp_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/cp_utils.py) · blob `cddc361d7b4798751cdd3f68f3bcbcbd719be4aa`
- [slime/backends/megatron_utils/data.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/data.py) · blob `6ae48a9613fef893461b20fb38db3de769141d22`
- [slime/backends/megatron_utils/hf_checkpoint_saver.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/hf_checkpoint_saver.py) · blob `2b8007c8529f339329bfc8ba892f4c761fbbeacb`
- [slime/backends/megatron_utils/hf_to_megatron/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/hf_to_megatron/__init__.py) · blob `234a410b9eb9c9594ebee3b19894c991210f8d45`
- [slime/backends/megatron_utils/hf_to_megatron/common.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/hf_to_megatron/common.py) · blob `66e0190e1e7268f6ee517de3281134c6f269ddc4`
- [slime/backends/megatron_utils/hf_to_megatron/deepseek.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/hf_to_megatron/deepseek.py) · blob `e7f8fbe379c4ac59096061abbf23d148b35c505a`
- [slime/backends/megatron_utils/hf_to_megatron/glm.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/hf_to_megatron/glm.py) · blob `a7e973394fb1103dfcada0d2aed1badab519ed1f`
- [slime/backends/megatron_utils/hf_to_megatron/qwen.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/hf_to_megatron/qwen.py) · blob `29cebc7602a1daacc4264c1086b1139c532f428e`
- [slime/backends/megatron_utils/hf_to_megatron/qwen3_5.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/hf_to_megatron/qwen3_5.py) · blob `254290a22d2a3bff74be4226632b424aa38781b8`
- [slime/backends/megatron_utils/hf_to_megatron/qwen3_next.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/hf_to_megatron/qwen3_next.py) · blob `f14d4222756f6167656da5ec7222b56f1329f4e1`
- [slime/backends/megatron_utils/initialize.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/initialize.py) · blob `7bb4077f150d7683294b63153fbfe76e7a779bc4`
- [slime/backends/megatron_utils/kernels/fp8_kernel.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/kernels/fp8_kernel.py) · blob `0cfa6042695fc73d00019e3391aed650f80103d2`
- [slime/backends/megatron_utils/kernels/int4_qat/fake_int4_quant_cuda.cu](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/kernels/int4_qat/fake_int4_quant_cuda.cu) · blob `f7df09987e63cd4fba5115d3c95de8e92395b858`
- [slime/backends/megatron_utils/kernels/int4_qat/setup.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/kernels/int4_qat/setup.py) · blob `2db4683f9854d492ce800cfb49abaa71cef62310`
- [slime/backends/megatron_utils/loss.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/loss.py) · blob `2e09cfb517b130e1e7aa9a122e55bea07eb40478`
- [slime/backends/megatron_utils/megatron_to_hf/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/__init__.py) · blob `cd5d4420f20917e6b4f64ccd5f07fd8f33ab25d3`
- [slime/backends/megatron_utils/megatron_to_hf/deepseekv3.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/deepseekv3.py) · blob `205b025556e9a7e8a936ee57d0eed00cb2431cb6`
- [slime/backends/megatron_utils/megatron_to_hf/glm4.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/glm4.py) · blob `cb82edac99a044a2f908498d1e2e4aaf76a6de64`
- [slime/backends/megatron_utils/megatron_to_hf/glm4moe.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/glm4moe.py) · blob `33a64e6e8f0fe5d22045c996b83e1fe45c8c807c`
- [slime/backends/megatron_utils/megatron_to_hf/llama.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/llama.py) · blob `6d89cb868358aa38b9a29261e6803debf16bd8cf`
- [slime/backends/megatron_utils/megatron_to_hf/mimo.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/mimo.py) · blob `5efafb29befcdac1b0f2d361ff35e50e62c6c3b5`
- [slime/backends/megatron_utils/megatron_to_hf/minimax_m2.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/minimax_m2.py) · blob `3701e30f2f433ada5dbbc08b083bdf3b517802ad`
- [slime/backends/megatron_utils/megatron_to_hf/processors/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/processors/__init__.py) · blob `6efe6bdadfb4fc57ecb8eb940ff9b9e87a570d78`
- [slime/backends/megatron_utils/megatron_to_hf/processors/padding_remover.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/processors/padding_remover.py) · blob `ada08a6a8b62696f2cdc13398db2169d496ca339`
- [slime/backends/megatron_utils/megatron_to_hf/processors/quantizer_compressed_tensors.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/processors/quantizer_compressed_tensors.py) · blob `5f953f91791952c44ccf653b24bd1fbb6967b735`
- [slime/backends/megatron_utils/megatron_to_hf/processors/quantizer_fp8.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/processors/quantizer_fp8.py) · blob `9e50fa8974a8a4bd3e9a46041f19365e1f89886c`
- [slime/backends/megatron_utils/megatron_to_hf/qwen2.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/qwen2.py) · blob `f7b72935cf512ed9aab70faa03f7c0458acd2e4f`
- [slime/backends/megatron_utils/megatron_to_hf/qwen3_5.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/qwen3_5.py) · blob `eea892753c8e75c4473e75c6c8db068806716740`
- [slime/backends/megatron_utils/megatron_to_hf/qwen3_next.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/qwen3_next.py) · blob `f12f31195f0fa4cad8968c37383085d3cbe9bd28`
- [slime/backends/megatron_utils/megatron_to_hf/qwen3_vl.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/qwen3_vl.py) · blob `97c5bc7ced849d7afc438d3f6717014987a87ab9`
- [slime/backends/megatron_utils/megatron_to_hf/qwen3moe.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/megatron_to_hf/qwen3moe.py) · blob `9f5b5b81a63e1a4311a5fbebefc3b7d1552c6886`
- [slime/backends/megatron_utils/memory.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/memory.py) · blob `e39b3256baaaf554d1acdac71625b571ba606cc7`
- [slime/backends/megatron_utils/misc_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/misc_utils.py) · blob `f101111d683f739b16be972a88da097b00cb2501`
- [slime/backends/megatron_utils/model.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/model.py) · blob `89f17f3d80fa7fd3fcd514297ce5dfe650226fa4`
- [slime/backends/megatron_utils/model_provider.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/model_provider.py) · blob `c6ce0eaedbe19e3722f7908695956d2e1e06310c`
- [slime/backends/megatron_utils/server/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/server/__init__.py) · blob `53b132ab0fafeff62e0d512bc8b90aaf8f1cdc38`
- [slime/backends/megatron_utils/server/arguments.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/server/arguments.py) · blob `32c9ba6b6619519a720ad27eb741e6db1034631c`
- [slime/backends/megatron_utils/server/logprob_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/server/logprob_utils.py) · blob `3772056dbddc1d34b4cbd18b8ce817b3eb874c43`
- [slime/backends/megatron_utils/server/megatron_server.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/server/megatron_server.py) · blob `d086a5f39307a694735ee133c9e99fbd8cc910c0`
- [slime/backends/megatron_utils/sglang.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/sglang.py) · blob `b72d9802f154c7302b0f76e780cbc30eb15ab459`
- [slime/backends/megatron_utils/stateless_adam.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/stateless_adam.py) · blob `4c49ab92b682591c5d8ca97791badcae37374845`
- [slime/backends/megatron_utils/transformer_engine.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/transformer_engine.py) · blob `9f22401cfe971c5270c3943738cbca8e8e349a40`
- [slime/backends/megatron_utils/update_weight/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/update_weight/__init__.py) · blob `dc40d630e53a00ccfb899cdf696de2e730a96c84`
- [slime/backends/megatron_utils/update_weight/common.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/update_weight/common.py) · blob `c06d6ae5cc57a7589163a64807c7d2fac4a8f9cb`
- [slime/backends/megatron_utils/update_weight/expert_routing.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/update_weight/expert_routing.py) · blob `ee3eea8da6880dad255bfa49655b34e7a730e01e`
- [slime/backends/megatron_utils/update_weight/hf_weight_iterator_direct.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/update_weight/hf_weight_iterator_direct.py) · blob `7c63f3512f42a58b009f2d3aeffe7e087adc3c69`
- [slime/backends/megatron_utils/update_weight/update_weight_from_disk.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/update_weight/update_weight_from_disk.py) · blob `d9bd74b23119fcc4883916bfe6ab1075b5032e26`
- [slime/backends/megatron_utils/update_weight/update_weight_from_disk_delta.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/update_weight/update_weight_from_disk_delta.py) · blob `6c3d33ab7dbeaf781e62e75b26d4085f26740eef`
- [slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py) · blob `f1e2fa153e2a27fdd1210bfc1005444d40d2a20f`
- [slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py) · blob `dd06316b37992ee31d78875b04552e35bce2a479`
- [slime/backends/sglang_utils/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/__init__.py) · blob `1a15621488c7086ab0cec0a7187a2cfb7ae66949`
- [slime/backends/sglang_utils/arguments.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/arguments.py) · blob `87ea0188257234d927f78ba565009d43ec607f8c`
- [slime/backends/sglang_utils/deployment.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/deployment.py) · blob `3ed2eca0338245d90bcfee5d7feb0d9a20bf9a4e`
- [slime/backends/sglang_utils/disaggregation.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/disaggregation.py) · blob `87492f591c62e4c1320958225bf4b8cef9aa2009`
- [slime/backends/sglang_utils/engine_group.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/engine_group.py) · blob `8ad5c860380d56ab2d06b2e8eb1816ab64dc8127`
- [slime/backends/sglang_utils/external.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/external.py) · blob `41efc86fb49c4930749c8c96b7ea44282e4acd79`
- [slime/backends/sglang_utils/jit_kernels/csrc/gemm/glm5_router_gemm.cuh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/jit_kernels/csrc/gemm/glm5_router_gemm.cuh) · blob `17a54b299edb2900adc70fa17268dbb039498681`
- [slime/backends/sglang_utils/server_control.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/server_control.py) · blob `60a598f9b02f82effbd61b79237e09d549c53f63`
- [slime/backends/sglang_utils/sglang_config.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/sglang_config.py) · blob `3504e5593c5db175028ec060ac4cb4b866eaf469`
- [slime/backends/sglang_utils/sglang_engine.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/sglang_utils/sglang_engine.py) · blob `482b06ece444f4018aa7505400ce94597729b533`
- [slime/data/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/__init__.py) · blob `7bc880e115bd3b346d711d23c60b50f25e0f3fb2`
- [slime/data/archive.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/archive.py) · blob `d51efe026e83ce3800dec9740441c6637f22eacb`
- [slime/data/batch_builder.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/batch_builder.py) · blob `fc750c37480de61065f18c223bb2e1ddc178a72f`
- [slime/data/checkpoint.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/checkpoint.py) · blob `65d35f4757a0ac7bfc6aa8e19c01e6aa28b4997a`
- [slime/data/codec.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/codec.py) · blob `6a320d033358c37cc5ded296aa86541eb1ba7819`
- [slime/data/data_source.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/data_source.py) · blob `61983821c23c11ac56fa8a2ef34b19c5757f67f2`
- [slime/data/queue_data_source.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/queue_data_source.py) · blob `5b9acc0240de3714525f3b35a757038b4116e804`
- [slime/data/sample_metadata.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/sample_metadata.py) · blob `fba8f479e71738279501c488e34d6bf53d2f70b6`
- [slime/data/tensor.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/tensor.py) · blob `9baa19ad0de50bf326d442617121bae09fe32c32`
- [slime/data/transport.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/data/transport.py) · blob `41385a1dba7c30e15df524876d7b8fa8ee74050c`
- [slime/observability/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/__init__.py) · blob `3dab479228218908bf5cc0f84b6da523df7cca1d`
- [slime/observability/logging_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/logging_utils.py) · blob `2ae2a222ce607cb6a42caa27f72b8996f42fab74`
- [slime/observability/metric_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/metric_utils.py) · blob `46e42d73b0df51060307410fb00e602d3cde3901`
- [slime/observability/profile_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/profile_utils.py) · blob `68569bac8997f900f1d1dfe79f3cc4f6f8c38929`
- [slime/observability/rollout_data_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/rollout_data_utils.py) · blob `4103ad6329f681d859c2d8c64422bcb2bb1846c3`
- [slime/observability/rollout_metrics.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/rollout_metrics.py) · blob `0636a78a3c88343eb50e00e4e0ec35f3218a8055`
- [slime/observability/tensorboard_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/tensorboard_utils.py) · blob `250864636c4873d8c21b48811b33a5317476ec20`
- [slime/observability/timer.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/timer.py) · blob `b0a89a53892dc9ee0a4eb65de66f8b33bb090d42`
- [slime/observability/trace_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/trace_utils.py) · blob `486e50b15b69cde41fde357bd8b564e40ccfaaa8`
- [slime/observability/train_data_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/train_data_utils.py) · blob `bf1372570821f5b47cefaacdc2d9ff53efb6b87f`
- [slime/observability/train_metric_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/train_metric_utils.py) · blob `07ddd931c5e3fb3147ed8bb86e25bf9c676a478b`
- [slime/observability/wandb_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/observability/wandb_utils.py) · blob `093be4d3518f398cf725f87660b6a1945a3c82b4`
- [slime/ray/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/ray/actor_group.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/actor_group.py) · blob `ce6e6d03955416f65fbe928e85534268ec258b7e`
- [slime/ray/placement_group.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/placement_group.py) · blob `bbee464c9034b641502031e881b20d405abb1385`
- [slime/ray/ray_actor.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/ray_actor.py) · blob `e44322a7117710a486500ad6c3531c79716ebc09`
- [slime/ray/rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/rollout.py) · blob `d81879154ff2f6783e4de92a4b8c66817ef25ae3`
- [slime/ray/serving.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/serving.py) · blob `b7e979b49e924c80b54d15dda1bd083fa21fcc36`
- [slime/ray/train_actor.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/train_actor.py) · blob `e91bc5a2cd95df829ca77b2594e88edd38625c3f`
- [slime/ray/training_recovery.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/training_recovery.py) · blob `3d891568c06bb57f2a9930d3f67bb1a6a1bec33e`
- [slime/ray/utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/utils.py) · blob `6275058f5b26865bcf6a04b77aadfeaf13c38605`
- [slime/rollout/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/rollout/base_types.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/base_types.py) · blob `cfcf11be85af5d6efc9bed0bb26941032177494e`
- [slime/rollout/filter_hub/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/filter_hub/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/rollout/filter_hub/base_types.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/filter_hub/base_types.py) · blob `5f2154c2c7fce483f2eb1c63832afb7b375790bc`
- [slime/rollout/filter_hub/dynamic_sampling_filters.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/filter_hub/dynamic_sampling_filters.py) · blob `167ad6de1581d4f2d50c101d3ba2a75f9e52468b`
- [slime/rollout/forge_load.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/forge_load.py) · blob `4f4aef7ec678a05760596b2c786e144149ccd684`
- [slime/rollout/fully_async_distributed.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/fully_async_distributed.py) · blob `ce8d38fae3bf77cbad2413389e891bf27402da62`
- [slime/rollout/fully_async_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/fully_async_rollout.py) · blob `2b819f8d3936bee2c36dab7fa1a98e41bd1c3fd4`
- [slime/rollout/on_policy_distillation.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/on_policy_distillation.py) · blob `eb52a0821de0fa4b47548ec5763698997507cc75`
- [slime/rollout/rm_hub/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/rm_hub/__init__.py) · blob `a2739fbec763ad28cead5b205c27f50bf14a5d07`
- [slime/rollout/rm_hub/deepscaler.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/rm_hub/deepscaler.py) · blob `39d4de383a1bdce9fc2558455469d41ab5bf99eb`
- [slime/rollout/rm_hub/f1.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/rm_hub/f1.py) · blob `ed98553f7b372e17947f1f3850f7d4b83a5178d7`
- [slime/rollout/rm_hub/gpqa.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/rm_hub/gpqa.py) · blob `affb7a22ad888ae9734a9cbc9c584dc1b31dd6d6`
- [slime/rollout/rm_hub/ifbench.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/rm_hub/ifbench.py) · blob `fc31d43eb83fafecb75ca8582b3e5405b705a7cd`
- [slime/rollout/rm_hub/math_dapo_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/rm_hub/math_dapo_utils.py) · blob `915c3aa480b1f9812c18fd3255b5c03e774a81f2`
- [slime/rollout/rm_hub/math_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/rm_hub/math_utils.py) · blob `fe4a8009551d74ea9c7a71476c46c562a4b50930`
- [slime/rollout/sample_hooks.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/sample_hooks.py) · blob `e72638ec9bc20846a97e8195cb0f1d9502a02ceb`
- [slime/rollout/sft_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/sft_rollout.py) · blob `4df55ff08da822c43afb2e48d84cbff650022f21`
- [slime/rollout/sglang_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/sglang_rollout.py) · blob `fd5f487f5aec3000e1bfd8d64fe6b1c70a210b24`
- [slime/rollout/sglang_streaming_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/sglang_streaming_rollout.py) · blob `911ff3ba269b08bfdaa7cdd667c4687a1be570d6`
- [slime/rollout/sleep_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/sleep_rollout.py) · blob `563b4138d0fd953713620151310a20031c95d914`
- [slime/rollout/streaming_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/rollout/streaming_utils.py) · blob `42793f471f14f6674212a8a51faefc2ea84cd4e9`
- [slime/utils/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/__init__.py) · blob `0745576620155d995c66f31f3d223d48b8e8b99f`
- [slime/utils/accelerator/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/accelerator/__init__.py) · blob `98127eacd6e4413cea949e2560d1f85085a64481`
- [slime/utils/accelerator/base.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/accelerator/base.py) · blob `9d760c619e2d57843112ecaaedda491117a106a3`
- [slime/utils/accelerator/cuda.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/accelerator/cuda.py) · blob `c9fca2afe0b39aeb7a9897559aa2a92185381e16`
- [slime/utils/accelerator/musa.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/accelerator/musa.py) · blob `62b398dfaa2d3f2e967978d1546a92df5594ed96`
- [slime/utils/accelerator/npu.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/accelerator/npu.py) · blob `5fc613e22b3925f2c41ab88bab7b898f848a07f3`
- [slime/utils/accelerator/supa.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/accelerator/supa.py) · blob `534604d427f5c83878f57aea0f9f346b2c4fad13`
- [slime/utils/accelerator/torch_accelerator.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/accelerator/torch_accelerator.py) · blob `d961ebe3d8d215ebf29f19bff40c7c600b732c06`
- [slime/utils/arguments.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/arguments.py) · blob `e4961ee242cb440816f44a6060cb347d2e97a1ba`
- [slime/utils/async_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/async_utils.py) · blob `26a752431c4485ed9fedd24836ff71414ffbd7d4`
- [slime/utils/cleanup.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/cleanup.py) · blob `df057f530d16c128978e290faacddb3b22e782f0`
- [slime/utils/data.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/data.py) · blob `bc7c855b3e5129aa0fb42c1a415e5ca86a2016b8`
- [slime/utils/disk_delta.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/disk_delta.py) · blob `7907a82171dfd6e0decd0aa644c6db1d80152241`
- [slime/utils/distributed_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/distributed_utils.py) · blob `af97bc14daa84f10bcbeeb3624e18708cb02a1fe`
- [slime/utils/dp_schedule.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/dp_schedule.py) · blob `1735fad3b48cd52ada98912ff2440481beaebf64`
- [slime/utils/eval_config.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/eval_config.py) · blob `f45f2be08662748d1f0ec44f5eabbc623212a3fa`
- [slime/utils/external_utils/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/external_utils/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime/utils/external_utils/command_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/external_utils/command_utils.py) · blob `656bc4a8500334f560c4118148932f32c8fc3ba0`
- [slime/utils/external_utils/typer_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/external_utils/typer_utils.py) · blob `ece4f5fd9f96dd56532890f3a3bbde5e0d4bca6b`
- [slime/utils/flops_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/flops_utils.py) · blob `7ac90fe8309f560ee375fec29c81962aee420206`
- [slime/utils/health_monitor.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/health_monitor.py) · blob `3e4af2d77dbf1e0b060c1caf70d4596963ccba1d`
- [slime/utils/http_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/http_utils.py) · blob `20d327a54622743b20fcbf8fdc66ba562b489359`
- [slime/utils/mask_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/mask_utils.py) · blob `51cb43c0b9988283028a1a73d651ac23dd3e7d95`
- [slime/utils/memory_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/memory_utils.py) · blob `4bcb6759bfa0d5894a1485a66f7efd24abf13b25`
- [slime/utils/misc.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/misc.py) · blob `090845569cfba6bf8c845017dec4653038f32728`
- [slime/utils/ppo_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/ppo_utils.py) · blob `c2ce5eaee500011735349bf6f61cf0258be19af9`
- [slime/utils/processing_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/processing_utils.py) · blob `fb652e73d0fbf3d73ce9355e5e960c6f32d5aad2`
- [slime/utils/reloadable_process_group.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/reloadable_process_group.py) · blob `bef0dc5e7b0dc57fe1d9e52e64c483fe5a49e778`
- [slime/utils/rocm_checkpoint_writer.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/rocm_checkpoint_writer.py) · blob `7a8a1be2cee9840380bd3fcf05af32b703a33fe8`
- [slime/utils/routed_experts.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/routed_experts.py) · blob `798bea78ec85190f6936f3c24d9f11c1d64bb164`
- [slime/utils/routing_replay.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/routing_replay.py) · blob `7d0b7627ec952d82248ea96ae86fdb2957d159b9`
- [slime/utils/score_centering.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/score_centering.py) · blob `06dd4a7d1ae7f9119258cd09fd17a519fcb7abd4`
- [slime/utils/seqlen_balancing.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/seqlen_balancing.py) · blob `57cf47f3cd20e67c8f0ab34d5841cd708ee451fa`
- [slime/utils/staleness.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/staleness.py) · blob `8e51536c7f0ddb3c15bce1a726ff1368ba81afb9`
- [slime/utils/tensor_backper.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/tensor_backper.py) · blob `3b0c3a64bf8fd0d125ff20d48fe7711c804c69d4`
- [slime/utils/types.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/types.py) · blob `0094c0ea55d44e4cf44a02a2f0aa987db02116f8`
- [slime/utils/weight_sync.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/utils/weight_sync.py) · blob `6d83bc19e50298bade0dc42b07e998fec5f600eb`

## slime_plugins

- [slime_plugins/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime_plugins/models/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [slime_plugins/models/flash_dot_product_attention.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/flash_dot_product_attention.py) · blob `fd89bdc4645f040d44ab1fc943d4798d81a66135`
- [slime_plugins/models/glm4.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/glm4.py) · blob `cc8efbad22dc8c492ad4b4df5ef3d355d8314eb4`
- [slime_plugins/models/glm5/glm5.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/glm5/glm5.py) · blob `e1c451383686269cb48d9e545246c61cf6e8f1cc`
- [slime_plugins/models/glm5/ops/indexer.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/glm5/ops/indexer.py) · blob `8dcac9053cc5933e7a97aa11ce03158a702f1ea7`
- [slime_plugins/models/glm5/ops/sparse_mla.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/glm5/ops/sparse_mla.py) · blob `2e3ce2628b4486d812558a2f7f0f6d79db1a2ca0`
- [slime_plugins/models/glm5/ops/tilelang_indexer_bwd.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/glm5/ops/tilelang_indexer_bwd.py) · blob `737800f0348451e39f52fb3d630c3e2e8760b45e`
- [slime_plugins/models/glm5/ops/tilelang_indexer_fwd.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/glm5/ops/tilelang_indexer_fwd.py) · blob `cc1b7a3ce4055bd95819e4f5edcf970f8e05782d`
- [slime_plugins/models/glm5/ops/tilelang_sparse_mla_bwd.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/glm5/ops/tilelang_sparse_mla_bwd.py) · blob `7c7b2097e09b416490177732b17889dda4aa1a44`
- [slime_plugins/models/glm5/ops/tilelang_sparse_mla_fwd.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/glm5/ops/tilelang_sparse_mla_fwd.py) · blob `864b14939330ac90b2d898c3251db6bec9db0a90`
- [slime_plugins/models/hf_attention.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/hf_attention.py) · blob `2daba2a3ff9f799030b5a3e49cf46adea49fda3b`
- [slime_plugins/models/learnable_softmax_attention.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/learnable_softmax_attention.py) · blob `6dd515782fae59243b828bac9ddc87e8813458ee`
- [slime_plugins/models/minimax_m2.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/minimax_m2.py) · blob `ec43af26d907fdc1acdf57a70edcd7b571c84577`
- [slime_plugins/models/qwen3_5.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/qwen3_5.py) · blob `d7551f9a94c985f62499877954fa76ec24e45b5e`
- [slime_plugins/models/qwen3_5_vl.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/qwen3_5_vl.py) · blob `cdc1ad7622a9857123fb68130d34c0c61f382855`
- [slime_plugins/models/qwen3_5_vl_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/qwen3_5_vl_utils.py) · blob `26f59d1f7e96841132e5be6c91f889e239fded6f`
- [slime_plugins/models/qwen3_next.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/qwen3_next.py) · blob `cc2937228eb4c8f38fb6bfa3c0b8d1706722fb71`
- [slime_plugins/models/qwen_gdn_backend.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/models/qwen_gdn_backend.py) · blob `a95bc8a0d05a08ca78bbef9a1b6284333991fbf2`
- [slime_plugins/rollout_buffer/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/rollout_buffer/README.md) · blob `e85e68d89c6d1192999bd9df5fbfb87ee85b8940`
- [slime_plugins/rollout_buffer/README_zh.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/rollout_buffer/README_zh.md) · blob `cfa689fe716b7d4f6bce02073057fc378c52d05a`
- [slime_plugins/rollout_buffer/buffer.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/rollout_buffer/buffer.py) · blob `db4e561124b54598c7788636291ab34c9cef33e0`
- [slime_plugins/rollout_buffer/generator/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/rollout_buffer/generator/__init__.py) · blob `87090b103846e53a0d1ffa318408f3a1d96d4657`
- [slime_plugins/rollout_buffer/generator/base_generator.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/rollout_buffer/generator/base_generator.py) · blob `5c6cb1d269883da5cb96228cf4c3bec7ef75d52f`
- [slime_plugins/rollout_buffer/rollout_buffer_example.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/rollout_buffer/rollout_buffer_example.py) · blob `ac1fb6998f9eb0bd50e2d4aaa410abc715cc62f9`
- [slime_plugins/rollout_buffer/rollout_buffer_example.sh](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime_plugins/rollout_buffer/rollout_buffer_example.sh) · blob `345660b5ef6fb86bfdc1d5a50a25a3fc4b736f64`

## tests

- [tests/_cp_dist_helpers.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/_cp_dist_helpers.py) · blob `351dadfc28d80ad20b810eeeafac5cf0bd123417`
- [tests/ci/README.md](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/ci/README.md) · blob `2b58be3d4c78a57ec8c5794c5852dbcb9069d8a1`
- [tests/ci/github_runner/.env.example](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/ci/github_runner/.env.example) · blob `1692a83a38f74fbeb314af605b365334df7e80cd`
- [tests/ci/github_runner/.gitignore](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/ci/github_runner/.gitignore) · blob `2eea525d885d5148108f6f3a9a8613863f783d36`
- [tests/ci/github_runner/docker-compose.yml](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/ci/github_runner/docker-compose.yml) · blob `c6d0fb63c8de5ec1a18bd3a7622c2dac6eadff75`
- [tests/ci/gpu_lock_exec.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/ci/gpu_lock_exec.py) · blob `e61593170c1f934c5d70bfea1de649d64b081b96`
- [tests/fanout_test_helpers.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/fanout_test_helpers.py) · blob `1e646e2be3c9681953e6badd654b5f06d0184c6e`
- [tests/glm52_layerwise_comparator.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/glm52_layerwise_comparator.py) · blob `d19fda98b62258b7e8a1a8ff2c11eebd6fbb1d8a`
- [tests/observability/test_trace_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/observability/test_trace_utils.py) · blob `dc19f1f36dc5ee955824af0c5ad38f9dbbb02718`
- [tests/pipeline_rl_test_helpers.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/pipeline_rl_test_helpers.py) · blob `0dda5cf5fb2b49cc4297eb030282b08ff8d7e382`
- [tests/plugin_contracts/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/plugin_contracts/__init__.py) · blob `87f1598bf0b17a9cd2a07c095656f41e7c0cba6e`
- [tests/plugin_contracts/_shared.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/plugin_contracts/_shared.py) · blob `9efa1b9072f59af768924bd983cbbad3034f6d9a`
- [tests/plugin_contracts/test_plugin_generate_contracts.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/plugin_contracts/test_plugin_generate_contracts.py) · blob `857aaa8381663b47f0b2e6064c1c136b4fff1fec`
- [tests/plugin_contracts/test_plugin_path_loading_contracts.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/plugin_contracts/test_plugin_path_loading_contracts.py) · blob `87aba819768dcbddb4bfa4c0c96fc9818ec4180c`
- [tests/plugin_contracts/test_plugin_rollout_contracts.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/plugin_contracts/test_plugin_rollout_contracts.py) · blob `a4f31310d5b1d48b74e3eada14ffe834ffaf75de`
- [tests/plugin_contracts/test_plugin_runtime_hook_contracts.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/plugin_contracts/test_plugin_runtime_hook_contracts.py) · blob `18343409cafa0b01295c8d944c7c7a23c8f73641`
- [tests/rollout_health_test_helpers.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/rollout_health_test_helpers.py) · blob `88f05d0d6a01d27dcc9c5749713d79f8f21ea42a`
- [tests/test_accelerator.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_accelerator.py) · blob `4273b632540c0090fe0535feb7d1ddcd7153e4cc`
- [tests/test_advantage_whiten_cp.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_advantage_whiten_cp.py) · blob `e33c0ed7fe6e43411a696b6c364a77e1bfa34cd5`
- [tests/test_agent/__init__.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_agent/__init__.py) · blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`
- [tests/test_agent/_dump_helpers.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_agent/_dump_helpers.py) · blob `3a4519d835834186f5515ad3abe9061b9900587d`
- [tests/test_agent/_fakes.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_agent/_fakes.py) · blob `6800652de76675ed927d051192eebada41ae1c53`
- [tests/test_agent/test_adapters.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_agent/test_adapters.py) · blob `852a9cf9735efb3463007a6b39309c1310104cac`
- [tests/test_agent/test_agent_rollout_cpu.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_agent/test_agent_rollout_cpu.py) · blob `32e8780df536ed227d4e7c1c668545a144cf1463`
- [tests/test_agent/test_harness.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_agent/test_harness.py) · blob `2fb1e38bd3d681198ebf0577d599de2e2b70db10`
- [tests/test_agent/test_sandbox_exec_and_wait.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_agent/test_sandbox_exec_and_wait.py) · blob `662d73233d422eb340e4c1213019c98e90a1f9e5`
- [tests/test_agent/test_trajectory_manager_branching.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_agent/test_trajectory_manager_branching.py) · blob `4400425d83081c09bf4fa40f0d5a5606b813e227`
- [tests/test_block_fp8_zero_block.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_block_fp8_zero_block.py) · blob `16885d25c61d51109bf68525f2f450cde48ad99f`
- [tests/test_cispo_loss.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_cispo_loss.py) · blob `9f2e86c89cb6f4ed707aa6b8915793b5b9d6f1f1`
- [tests/test_cp_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_cp_utils.py) · blob `c7d3abe9a2c21fbc3bd3952f01c1ac9dc5a3056c`
- [tests/test_cuda_stack_offload.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_cuda_stack_offload.py) · blob `fa52ff64a114ec8c15ff613f21f62fd939622a4c`
- [tests/test_deep_ep_tms_patch.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_deep_ep_tms_patch.py) · blob `b1aee804782cf253b007212dfb732ef63f14d56b`
- [tests/test_discounted_returns.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_discounted_returns.py) · blob `8e1caae82e93c1bb37b347b016413519d52fe113`
- [tests/test_disk_delta_checkpoint_index.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_disk_delta_checkpoint_index.py) · blob `52087704952a72be3a582e111fa03de24608eac7`
- [tests/test_disk_delta_recovery.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_disk_delta_recovery.py) · blob `429c404d3f30ec4d135420f2aefdddd30ef21082`
- [tests/test_distributed_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_distributed_rollout.py) · blob `66049992869fe603cc0f4c0a6659dc8c05e2bcac`
- [tests/test_docs_consistency.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_docs_consistency.py) · blob `217a29884fe26ef0fbef7b085ea804d4294d0802`
- [tests/test_dp_schedule.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_dp_schedule.py) · blob `33a8be53b5ea8aef7a4ea53af7049aacaea352c4`
- [tests/test_empty_colocated_weight_bucket.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_empty_colocated_weight_bucket.py) · blob `c7683e10bc034592901eb8647fcafb3b7011cd04`
- [tests/test_eval_config.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_eval_config.py) · blob `a51270e01205be500130d8d07aed73a8995a03b7`
- [tests/test_expert_routing.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_expert_routing.py) · blob `5d17f24ae0fb9c7648d10d813442270ca1c9e6c1`
- [tests/test_external_sglang_engines.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_external_sglang_engines.py) · blob `61b32c460d350277d4faccff1ad09edae9179026`
- [tests/test_filter_long_prompt.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_filter_long_prompt.py) · blob `9ec9462337217cf4daf844f3b7177e08742ef904`
- [tests/test_full_disk_weight_update.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_full_disk_weight_update.py) · blob `978175d5642d7334db32243cb2ea9c6641f4af20`
- [tests/test_fully_async_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_fully_async_rollout.py) · blob `396e59a677bb036f24fa100f3637baaa12c0f397`
- [tests/test_glm4.7_30B_A3B_pd_mooncake.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_glm4.7_30B_A3B_pd_mooncake.py) · blob `75614e48cef460d113dc28658b2c58e5e3b5fb43`
- [tests/test_glm52_6layer_deterministic_e2e.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_glm52_6layer_deterministic_e2e.py) · blob `7311e0886ba0e11682d45bf56538e9dd4c1bae0a`
- [tests/test_glm52_layerwise_comparison.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_glm52_layerwise_comparison.py) · blob `9228646461e3cbe8445630dccd7ad0bec0bd1573`
- [tests/test_glm52_layerwise_zero_e2e.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_glm52_layerwise_zero_e2e.py) · blob `93a7ffc5717a6aed4327911c63ef9e4cb76f0954`
- [tests/test_glm5_indexer_q_norm.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_glm5_indexer_q_norm.py) · blob `30201f36a30713264824bfe383ace3f7153d1afb`
- [tests/test_glm5_indexer_short_context.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_glm5_indexer_short_context.py) · blob `fb189d122624ef0289a92eab9f2eed5de12b35eb`
- [tests/test_hf_to_megatron.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_hf_to_megatron.py) · blob `dc41681494d3205ef3015c0a5a975497b46ab527`
- [tests/test_layerwise_alignment.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_layerwise_alignment.py) · blob `d84e78fe3ffd72816de0c2596e1c0024e449685e`
- [tests/test_logprob_response_spans.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_logprob_response_spans.py) · blob `51f22016f0b67ffa89591d7106e17c8952521786`
- [tests/test_loss_cp_invariance.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_loss_cp_invariance.py) · blob `4f2ca9559b251fd5fa419786504db57bed60b104`
- [tests/test_megatron_argument_validation.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_megatron_argument_validation.py) · blob `7d1bef6791bbe8abd83524dc2a0da377008fa3fa`
- [tests/test_megatron_checkpoint.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_megatron_checkpoint.py) · blob `4af344ebcd5abb46c854fe9ce9b2bab90793b094`
- [tests/test_megatron_tokenizer_init.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_megatron_tokenizer_init.py) · blob `47eb0a7c7dbaf02bed0e1ab9a63bda09dfb9949a`
- [tests/test_metric_report.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_metric_report.py) · blob `a83f7fda1b8d7129fb7fcb9f14b997ab86352270`
- [tests/test_metric_report_dist.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_metric_report_dist.py) · blob `466ad3b72974394f8a8c46266cdc8b7e5f3e6478`
- [tests/test_mimo_7B_mtp_only_grad.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_mimo_7B_mtp_only_grad.py) · blob `e1bee49d1cfe02efe4ec7ece7ebbecbc49bd81fa`
- [tests/test_model_provider_freeze.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_model_provider_freeze.py) · blob `cd238c8ff7883ea5923fef994eab5c66146f005a`
- [tests/test_moonlight_16B_A3B.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_moonlight_16B_A3B.py) · blob `bc63dbdbbdb0cedb3ff5c05a226f1590f1c1a43b`
- [tests/test_moonlight_16B_A3B_r3.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_moonlight_16B_A3B_r3.py) · blob `157795812128047d011e369f69126bc8b9f019b4`
- [tests/test_optional_straw.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_optional_straw.py) · blob `7c99c49c01665fde3f6395175d60654814f832d7`
- [tests/test_pipeline_rl.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_pipeline_rl.py) · blob `3e84d75e8e3fe5a4887d3fd469049be81193dfb3`
- [tests/test_placement_group.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_placement_group.py) · blob `537b883d7a95b02b18c53e57d2ad3ffd9cbcc6c0`
- [tests/test_policy_loss.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_policy_loss.py) · blob `410b46e63645502654404602f25cc5bac16fb49a`
- [tests/test_ppo_kl_metric.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_ppo_kl_metric.py) · blob `eb3e1855982fb66236be7b7a2e23d9c5d6f215e4`
- [tests/test_ppo_logprob_entropy.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_ppo_logprob_entropy.py) · blob `b23d56b0503e94de9ced7e363f351db48e227aa1`
- [tests/test_ppo_logprob_entropy_gpu.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_ppo_logprob_entropy_gpu.py) · blob `c1d833bcb8ee89a8153c59e98e0cbc79ee0fd2b1`
- [tests/test_process_rollout_data.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_process_rollout_data.py) · blob `b8090c95fa7645baecebd061097d66da6b9b8d47`
- [tests/test_published_payload_retry.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_published_payload_retry.py) · blob `9be1e4c910b3eec853789ab6b157f01441a5ba16`
- [tests/test_queue_sample_codec.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_queue_sample_codec.py) · blob `b868cd6f99532f8992a331c220e191e468c8f52e`
- [tests/test_quick_start_glm4_9B.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_quick_start_glm4_9B.py) · blob `e1b71bd5175b646498279e59c5e4862f736901f3`
- [tests/test_qwen2.5_0.5B_debug_rollout_then_train.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_debug_rollout_then_train.py) · blob `1e900b675ece61f368cf62cbbf2c60c29e297b85`
- [tests/test_qwen2.5_0.5B_debug_train_dump_e2e.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_debug_train_dump_e2e.py) · blob `76c1411964cbc648dea40e153743d9b4c055adaf`
- [tests/test_qwen2.5_0.5B_fanout_short.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_fanout_short.py) · blob `d4045218f381a23b53d6503a95e4cc37556177ce`
- [tests/test_qwen2.5_0.5B_fully_async_short.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_fully_async_short.py) · blob `1d83b00a12cadd6bce93ab0bc396fe7c3f651255`
- [tests/test_qwen2.5_0.5B_opd_sglang.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_opd_sglang.py) · blob `4ac42172563f48c877bae27f6609d086d6d34bd7`
- [tests/test_qwen2.5_0.5B_pipeline_rl.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_pipeline_rl.py) · blob `0b4d73c4ad8db35c034c9d0299aa0775e343b314`
- [tests/test_qwen2.5_0.5B_rollout_health.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_rollout_health.py) · blob `85434712c3a80155f8b6f04a59b227ca77fa91fe`
- [tests/test_qwen2.5_0.5B_score_centering.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_score_centering.py) · blob `d5a75288c84e828bd37254dfb369757703117c78`
- [tests/test_qwen2.5_0.5B_sglang_config.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_sglang_config.py) · blob `6229a91604050f9573de7c0a2589d6c9b5f76cac`
- [tests/test_qwen2.5_0.5B_sglang_config_distributed.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_sglang_config_distributed.py) · blob `aee1ae19678f4f5a2e238eef475477c7fd337ba1`
- [tests/test_qwen2.5_0.5B_training_recovery.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen2.5_0.5B_training_recovery.py) · blob `9bb0a25b8391caf012398f5ab43a2b2459587c88`
- [tests/test_qwen3.5_0.8B_gsm8k_short.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3.5_0.8B_gsm8k_short.py) · blob `93306eadd32fbdbac93d3d715d1d7309ec4babc0`
- [tests/test_qwen3.6_35B_A3B_pd_mooncake.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3.6_35B_A3B_pd_mooncake.py) · blob `2a4cee57b0485517da3da15d2d7fa2d7b4b0a75d`
- [tests/test_qwen3_0.6B_parallel_check.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_0.6B_parallel_check.py) · blob `0a1438a1258a9fb3b6b16155672ede2f178399a3`
- [tests/test_qwen3_30B_A3B.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_30B_A3B.py) · blob `cdb9ebbe5199c281d80e0c3663686644fef89981`
- [tests/test_qwen3_30B_A3B_r3.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_30B_A3B_r3.py) · blob `c36613fcc45d28eae0784336c0c94292ca0b9875`
- [tests/test_qwen3_30B_A3B_training_recovery.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_30B_A3B_training_recovery.py) · blob `69c9cb22ccf57894f0ffcc77572cb18c3b46dd39`
- [tests/test_qwen3_4B_ckpt.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_4B_ckpt.py) · blob `c9803bfb16f98f0f277b51ca8a0f047861040e83`
- [tests/test_qwen3_4B_external_pd.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_4B_external_pd.py) · blob `5c87592b8b87609b12a0704de301f610b9441609`
- [tests/test_qwen3_4B_ppo.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_4B_ppo.py) · blob `f261e9781a8396e3f5c81f16db8dd1afa2b26f58`
- [tests/test_qwen3_4B_ppo_disaggregate.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_4B_ppo_disaggregate.py) · blob `bafb6260ff1ad9db4fe1b4b40e37b7225c9a6269`
- [tests/test_qwen3_4B_ppo_train_critic_only.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_4B_ppo_train_critic_only.py) · blob `50b5072e4fbd0fe939fbda1092749be2651558f5`
- [tests/test_qwen3_4B_streaming_partial_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_4B_streaming_partial_rollout.py) · blob `85b4b7d2ab518bc710a4a71191502cc5ad6f7bd7`
- [tests/test_qwen3_5_vl_native.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_5_vl_native.py) · blob `d1c63e009e9385984c58cb9ac594c2140886fe68`
- [tests/test_qwen3_linear_attention_cu_seqlens.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_qwen3_linear_attention_cu_seqlens.py) · blob `7300f009f61f201108ded8b382971f22dba7e430`
- [tests/test_read_file_slicing.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_read_file_slicing.py) · blob `363af1b2b047d6d9fac7dc3f03e9ea01bba2f79e`
- [tests/test_reference_top_p_replay.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_reference_top_p_replay.py) · blob `25fa0aac02cd05317ffa02f7bbe086ec4adf2276`
- [tests/test_release_train.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_release_train.py) · blob `9e6a3b7527542e95f28c06a567a7ea97f8544c20`
- [tests/test_reloadable_process_group_memory_check.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_reloadable_process_group_memory_check.py) · blob `69abee7b9ab8a53932690880745ddcd6bd59368f`
- [tests/test_reloadable_process_group_world.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_reloadable_process_group_world.py) · blob `289b0bebf0eee5cf419af677cce09a581480799d`
- [tests/test_rm_deepscaler.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rm_deepscaler.py) · blob `0883a606228a74b7fae74081b0dda5a5c5aaf467`
- [tests/test_rm_f1.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rm_f1.py) · blob `f6ba8140f07fc2675dd9b2b648dc0fa321554530`
- [tests/test_rm_gpqa.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rm_gpqa.py) · blob `6e7ac1009f24bab8cd91616fb8182a391424cf32`
- [tests/test_rm_math.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rm_math.py) · blob `6ec589485574967ee17edbfbeb49c43aea4428f7`
- [tests/test_rm_math_dapo.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rm_math_dapo.py) · blob `3a5e9a28b96680505848783ed114ece15936271e`
- [tests/test_rollout_buffer_order.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rollout_buffer_order.py) · blob `f4f8b17a12bcd237d95fcf142d4d8fab87548a0d`
- [tests/test_rollout_data_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rollout_data_utils.py) · blob `c6d9cb8abd92d6ffff2eb13471ac1c517cf8b0f5`
- [tests/test_rollout_manager_recovery.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rollout_manager_recovery.py) · blob `d0d6ccbe91a4a551561ee151863a8883557188eb`
- [tests/test_rollout_metadata_index.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rollout_metadata_index.py) · blob `4123129ba3f46a65a7855c8ac361c3ea768b1e2d`
- [tests/test_rollout_metrics.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rollout_metrics.py) · blob `79997412e520991eba2b4e724479d22dc0ea3017`
- [tests/test_rollout_sample_hooks.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rollout_sample_hooks.py) · blob `ec5f2926705f26870010e6ac117740c1980dad67`
- [tests/test_rollout_straw_transport.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_rollout_straw_transport.py) · blob `35940dea4b2e2f8dd3dc88036c6f1b166141e3b3`
- [tests/test_routed_experts_disk_layout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_routed_experts_disk_layout.py) · blob `aba7aa896a69dd50e66b70f50953ff8b014dba7e`
- [tests/test_sample.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_sample.py) · blob `e61326377493adcc221270b4876b5edeac6c29b4`
- [tests/test_score_centering.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_score_centering.py) · blob `0d0e4361cb82548ef302859a6b496ae48cfd2aa9`
- [tests/test_score_centering_binary.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_score_centering_binary.py) · blob `b936f3064161aea57921c81ad06713111d86d673`
- [tests/test_score_centering_transport.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_score_centering_transport.py) · blob `be005d16a7f7e24243544173518bddd977cfa919`
- [tests/test_server_control.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_server_control.py) · blob `baec3965b4357ceb165f289715b24e989f8c3bd2`
- [tests/test_sglang_config_mixed_offload.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_sglang_config_mixed_offload.py) · blob `edcd460791b096d228aa53b1ade80097358d8604`
- [tests/test_sglang_config_mixed_offload_ft.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_sglang_config_mixed_offload_ft.py) · blob `525ea6bfb972f2228c9c15a888de6b4375aa361a`
- [tests/test_stateless_adam.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_stateless_adam.py) · blob `52aacb5c65bbc6e03fd449f65126bd4136a2656f`
- [tests/test_straw_checkpoint_fork.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_straw_checkpoint_fork.py) · blob `724d73e6ed2a322183d12a22bb51d8dfb16852a9`
- [tests/test_straw_fully_async_recovery.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_straw_fully_async_recovery.py) · blob `1fd4b02b0f06b3d082b18f7a80861592df5f0121`
- [tests/test_straw_r3.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_straw_r3.py) · blob `57b081d93f24990c062a025ba0a971339ae0b0e3`
- [tests/test_streaming_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_streaming_rollout.py) · blob `22a93588d9fdbfcd65df94de78ced5d994ff81d1`
- [tests/test_tau_bench_token_delta.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_tau_bench_token_delta.py) · blob `4e677ef27d50f8731d0f105dcd6ce90e5c07c21e`
- [tests/test_train_data_utils.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_train_data_utils.py) · blob `6b94ff29ac7f334ce6beb6f326336f4b794cd566`
- [tests/test_training_recovery.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_training_recovery.py) · blob `871cf42a0261cfd9875c06ddf73b1c9f30fd696e`
- [tests/test_update_weight_factory.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_update_weight_factory.py) · blob `ef4968daa1d9399084319c4c81469ce8ff73a152`
- [tests/test_value_temperature.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/test_value_temperature.py) · blob `195d89e88f985d635a85ca8b095c0710abb3bc47`
- [tests/training_recovery_test_helpers.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/training_recovery_test_helpers.py) · blob `a5ea377e4d4b8d56ea6ab8bb708f8bc72cc770bd`
- [tests/utils/test_hf_checkpoint_saver.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/utils/test_hf_checkpoint_saver.py) · blob `ab73061349f893f87ac0037645fe130d78aac787`
- [tests/utils/test_loss_mask_type_qwen35.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/utils/test_loss_mask_type_qwen35.py) · blob `18457ccc26b8cd01430f331b7d03c25183056b3b`
- [tests/utils/test_megatron_role_config.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/utils/test_megatron_role_config.py) · blob `093b33519487f4fe5482cf9db2f5d2ce295cef78`
- [tests/utils/test_megatron_server_arguments.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/utils/test_megatron_server_arguments.py) · blob `ebf837c6e7af206bf0ad8d3ff066e63bd76b3b0b`
- [tests/utils/test_sglang_arguments.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/utils/test_sglang_arguments.py) · blob `48c98ec6f628faae450ed7ab67fcb33c502159df`
- [tests/utils/test_sglang_config.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tests/utils/test_sglang_config.py) · blob `404ada7d765cfe286756ff0965426c59ad364878`

## tools

- [tools/analyze_profile.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/analyze_profile.py) · blob `de511744f279402b4fddbdef2bb1e923434d45a1`
- [tools/convert_hf_to_fp8.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/convert_hf_to_fp8.py) · blob `bcc4306b9d829bc8bc282d488e6a46270d9ee345`
- [tools/convert_hf_to_int4.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/convert_hf_to_int4.py) · blob `3dbf075ebf6d8a08cfa875cc08ab88f7be6af66c`
- [tools/convert_hf_to_int4_direct.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/convert_hf_to_int4_direct.py) · blob `7eaffc7272f381d0def7cb755765724ce0f7438a`
- [tools/convert_hf_to_torch_dist.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/convert_hf_to_torch_dist.py) · blob `62207788951cdd23d130500dce35fdccae00e0dc`
- [tools/convert_k2_thinking_int4_to_bf16.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/convert_k2_thinking_int4_to_bf16.py) · blob `78c0effc043dd0f39bdd4a871aee399595855d74`
- [tools/convert_to_hf.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/convert_to_hf.py) · blob `201e35bf9c4c9faa2f7bb734b2fef6cf92f8b435`
- [tools/convert_torch_dist_to_hf.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/convert_torch_dist_to_hf.py) · blob `8049d77437024d9b381a911e96b846a48f8098a2`
- [tools/convert_torch_dist_to_hf_parallel.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/convert_torch_dist_to_hf_parallel.py) · blob `763254d42cfc2cc7bbe3fe46d4e614ecbb035729`
- [tools/fp8_cast_bf16.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/fp8_cast_bf16.py) · blob `edc8485d90f278dacea3adece1668dc18b4d5d50`
- [tools/profile_rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/profile_rollout.py) · blob `8869a199360a89fb985289657d45161f97edb555`
- [tools/trace_timeline_viewer.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/tools/trace_timeline_viewer.py) · blob `924ab3205a8e9d1df8f26480b98600eea33db726`

## train.py

- [train.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/train.py) · blob `c13a9832516e9ae8327a5cb21074d75543adfa26`

