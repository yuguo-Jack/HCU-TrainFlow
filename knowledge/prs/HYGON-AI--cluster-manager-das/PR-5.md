---
id: pr-hygon-ai--cluster-manager-das-5
title: 'feat(envcheck): unified cluster runner, site config, and rccl multi-node fixes'
engine: tooling
stages:
- adapt
- optimize
- fault-tolerance
kind: source-pr
coverage: upstream-body-and-discussions
review_level: source-reported
runtime_validated: false
repository: HYGON-AI/cluster-manager-das
pr_number: 5
updated_at: '2026-10-10T02:55:44Z'
artifact_sha256: ddaba92177d04210b8347df7b2e4a5a3dd5616374acea328d63b0f2302d5dec1
artifact_path: knowledge/evidence/prs/HYGON-AI--cluster-manager-das/5-ddaba92177d04210b8347df7b2e4a5a3dd5616374acea328d63b0f2302d5dec1.json
sources: []
generated_body_sha256: be25c4f2720cee41df8e4c65d1f4b1e89ebb42bcd1623fecd98f17c8018743b8
---

# feat(envcheck): unified cluster runner, site config, and rccl multi-node fixes

[Upstream PR](https://github.com/HYGON-AI/cluster-manager-das/pull/5) · state: closed · merged: True

## Original PR description

Sync from fork zhaoyu111111/cluster-manager-das (commit a1e688a).

- unified bin/hcu-cluster-run entry (scenario x operation), group hostfiles, container lifecycle with managed peer SSH, token-guard cleanup
- site cluster_env.conf layer for rccl communication defaults; RCCL_EXTRA_LD_PATH for the shca plugin
- fix multi-node rccl: rank/guard scripts materialized to shared log dir (mpirun argv re-splitting broke inline bodies)
- container checks/tests require -i/--image
- run directories: <scenario>_<operation>_<timestamp> (container/conda/lconda labels)
- thousand-node log folding via --log-detail milestone|every|quiet
- dead-code removal (legacy cluster_group_run.sh, old CLI), MANIFEST.release fix
- review fixes: OMPI WORLD_SIZE env mapping, env_script=None guard, --cards validation, doc examples, personal paths removed
- HYGON copyright/SPDX headers added (33 files); 490 unit tests green on Windows and Linux nodes

## Review and discussion

### reviews

- NLPCheng · APPROVED · 2026-10-10T02:50:43Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/5#pullrequestreview-5477234050)

(No body; status only.)

### issue_comments

- hygon-ai-reviewer[bot] · comment · 2026-10-10T02:09:06Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/5#issuecomment-6092548619)

<!-- github-ai-reviewer-progress:5:a1e688a538a2dc3e746873bbf56a0fd72e53f23e -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 部分结果不可用：1/111 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 99 个文件，已审查 28 个，部分审查 1 个，待审查 43 个，跳过 27 个。

> 跳过原因：无 patch 27 个；文件类型过滤 0 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-10-10T02:46:08Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/5#issuecomment-6092946415)

<!-- github-ai-reviewer-progress:5:2aeb7da14fe6da65110a82beaeb4cde5524cc196 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 99 个文件，已审查 15 个，部分审查 1 个，待审查 56 个，跳过 27 个。

> 跳过原因：无 patch 27 个；文件类型过滤 0 个。

> 进度已保存。正在继续处理。

### inline_comments

## Changed files and fixed code

- `.gitignore` · modified · additions 4 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/.gitignore)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/.gitignore)
- `hcu-envcheck/.gitattributes` · modified · additions 1 / deletions 1
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/.gitattributes)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/.gitattributes)
- `hcu-envcheck/.gitignore` · modified · additions 5 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/.gitignore)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/.gitignore)
- `hcu-envcheck/AGENTS.md` · added · additions 52 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/AGENTS.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/AGENTS.md)
- `hcu-envcheck/MANIFEST.release` · modified · additions 6 / deletions 2
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/MANIFEST.release)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/MANIFEST.release)
- `hcu-envcheck/README.md` · modified · additions 171 / deletions 81
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/README.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/README.md)
- `hcu-envcheck/USER_GUIDE.md` · removed · additions 0 / deletions 12
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/USER_GUIDE.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/USER_GUIDE.md)
- `hcu-envcheck/bin/hcu-cluster-run` · added · additions 140 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/bin/hcu-cluster-run)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/bin/hcu-cluster-run)
- `hcu-envcheck/bin/hcu-envcheck` · removed · additions 0 / deletions 104
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/bin/hcu-envcheck)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/bin/hcu-envcheck)
- `hcu-envcheck/bin/hcu-envcheck-doctor` · removed · additions 0 / deletions 71
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/bin/hcu-envcheck-doctor)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/bin/hcu-envcheck-doctor)
- `hcu-envcheck/bin/hcu-envcheck-verify` · removed · additions 0 / deletions 44
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/bin/hcu-envcheck-verify)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/bin/hcu-envcheck-verify)
- `hcu-envcheck/cluster_run/GUIDE.md` · added · additions 53 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/GUIDE.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/GUIDE.md)
- `hcu-envcheck/cluster_run/README.md` · added · additions 24 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/README.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/README.md)
- `hcu-envcheck/cluster_run/__init__.py` · added · additions 9 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/__init__.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/__init__.py)
- `hcu-envcheck/cluster_run/__main__.py` · renamed · additions 9 / deletions 5
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/__main__.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/__main__.py)
- `hcu-envcheck/cluster_run/active.py` · added · additions 324 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/active.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/active.py)
- `hcu-envcheck/cluster_run/baselines/gemm_baseline.conf.example` · added · additions 15 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/baselines/gemm_baseline.conf.example)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/baselines/gemm_baseline.conf.example)
- `hcu-envcheck/cluster_run/baselines/rccl_baseline.conf.example` · added · additions 28 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/baselines/rccl_baseline.conf.example)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/baselines/rccl_baseline.conf.example)
- `hcu-envcheck/cluster_run/cli.py` · added · additions 945 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/cli.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/cli.py)
- `hcu-envcheck/cluster_run/cluster_env.conf.example` · added · additions 108 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/cluster_env.conf.example)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/cluster_env.conf.example)
- `hcu-envcheck/cluster_run/common.sh` · added · additions 49 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/common.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/common.sh)
- `hcu-envcheck/cluster_run/consistency.py` · added · additions 191 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/consistency.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/consistency.py)
- `hcu-envcheck/cluster_run/container_ssh.py` · added · additions 250 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/container_ssh.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/container_ssh.py)
- `hcu-envcheck/cluster_run/env.py` · added · additions 90 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/env.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/env.py)
- `hcu-envcheck/cluster_run/examples/nodes.txt.example` · added · additions 5 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/examples/nodes.txt.example)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/examples/nodes.txt.example)
- `hcu-envcheck/cluster_run/extra_checks.py` · added · additions 203 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/extra_checks.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/extra_checks.py)
- `hcu-envcheck/cluster_run/hostfile.py` · added · additions 99 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/hostfile.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/hostfile.py)
- `hcu-envcheck/cluster_run/launchers.py` · added · additions 146 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/launchers.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/launchers.py)
- `hcu-envcheck/cluster_run/lifecycle.py` · added · additions 291 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/lifecycle.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/lifecycle.py)
- `hcu-envcheck/cluster_run/node_script.py` · added · additions 136 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/node_script.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/node_script.py)
- `hcu-envcheck/cluster_run/payloads/__init__.py` · added · additions 8 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/__init__.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/__init__.py)
- `hcu-envcheck/cluster_run/payloads/_torch_common.py` · added · additions 83 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/_torch_common.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/_torch_common.py)
- `hcu-envcheck/cluster_run/payloads/check_deepep_env.sh` · added · additions 366 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/check_deepep_env.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/check_deepep_env.sh)
- `hcu-envcheck/cluster_run/payloads/dcu_idle_check.sh` · added · additions 97 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/dcu_idle_check.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/dcu_idle_check.sh)
- `hcu-envcheck/cluster_run/payloads/gemm_perf_test.sh` · added · additions 298 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/gemm_perf_test.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/gemm_perf_test.sh)
- `hcu-envcheck/cluster_run/payloads/gemm_worker.py` · added · additions 56 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/gemm_worker.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/gemm_worker.py)
- `hcu-envcheck/cluster_run/payloads/ib_write_bw_worker.py` · added · additions 50 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/ib_write_bw_worker.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/ib_write_bw_worker.py)
- `hcu-envcheck/cluster_run/payloads/rccl_perf_test.sh` · added · additions 590 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/rccl_perf_test.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/rccl_perf_test.sh)
- `hcu-envcheck/cluster_run/payloads/rccl_worker.py` · added · additions 77 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/rccl_worker.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/rccl_worker.py)
- `hcu-envcheck/cluster_run/payloads/task_guard.sh` · added · additions 323 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/payloads/task_guard.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/payloads/task_guard.sh)
- `hcu-envcheck/cluster_run/preflight.py` · added · additions 440 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/preflight.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/preflight.py)
- `hcu-envcheck/cluster_run/task_control.py` · added · additions 310 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/task_control.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/task_control.py)
- `hcu-envcheck/cluster_run/tests/help_smoke_check.sh` · added · additions 17 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/tests/help_smoke_check.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/tests/help_smoke_check.sh)
- `hcu-envcheck/cluster_run/testsuites.py` · added · additions 110 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/cluster_run/testsuites.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/cluster_run/testsuites.py)
- `hcu-envcheck/docs/INDEX.md` · added · additions 7 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/docs/INDEX.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/docs/INDEX.md)
- `hcu-envcheck/docs/USER_GUIDE.md` · modified · additions 202 / deletions 1217
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/docs/USER_GUIDE.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/docs/USER_GUIDE.md)
- `hcu-envcheck/examples/check-nodes.sh` · removed · additions 0 / deletions 203
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/examples/check-nodes.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/examples/check-nodes.sh)
- `hcu-envcheck/examples/k8s-nodes.txt` · removed · additions 0 / deletions 7
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/examples/k8s-nodes.txt)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/examples/k8s-nodes.txt)
- `hcu-envcheck/examples/slurm-nodelist.sh` · removed · additions 0 / deletions 38
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/examples/slurm-nodelist.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/examples/slurm-nodelist.sh)
- `hcu-envcheck/examples/ssh-nodes-file.sh` · removed · additions 0 / deletions 39
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/examples/ssh-nodes-file.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/examples/ssh-nodes-file.sh)
- `hcu-envcheck/hcu-envcheck.sh` · removed · additions 0 / deletions 21
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu-envcheck.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu-envcheck.sh)
- `hcu-envcheck/hcu_envcheck/active_rdma.py` · removed · additions 0 / deletions 2634
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/active_rdma.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/active_rdma.py)
- `hcu-envcheck/hcu_envcheck/baremetal.py` · modified · additions 208 / deletions 41
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/baremetal.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/baremetal.py)
- `hcu-envcheck/hcu_envcheck/baremetal_cluster.py` · renamed · additions 628 / deletions 461
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/baremetal_cluster.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/slurm_cluster.py)
- `hcu-envcheck/hcu_envcheck/cli.py` · removed · additions 0 / deletions 979
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/cli.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/cli.py)
- `hcu-envcheck/hcu_envcheck/cluster_checks.py` · modified · additions 120 / deletions 42
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/cluster_checks.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/cluster_checks.py)
- `hcu-envcheck/hcu_envcheck/environment.py` · modified · additions 102 / deletions 84
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/environment.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/environment.py)
- `hcu-envcheck/hcu_envcheck/ib_fabric.py` · removed · additions 0 / deletions 2377
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/ib_fabric.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/ib_fabric.py)
- `hcu-envcheck/hcu_envcheck/k8s.py` · removed · additions 0 / deletions 475
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/k8s.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/k8s.py)
- `hcu-envcheck/hcu_envcheck/k8s_cluster.py` · removed · additions 0 / deletions 1912
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/k8s_cluster.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/k8s_cluster.py)
- `hcu-envcheck/hcu_envcheck/output.py` · modified · additions 33 / deletions 4
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/output.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/output.py)
- `hcu-envcheck/hcu_envcheck/pod_probe.py` · modified · additions 170 / deletions 66
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/pod_probe.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/pod_probe.py)
- `hcu-envcheck/hcu_envcheck/preflight.py` · modified · additions 2 / deletions 440
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/preflight.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/preflight.py)
- `hcu-envcheck/hcu_envcheck/rccl_output.py` · modified · additions 1 / deletions 1
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/rccl_output.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/rccl_output.py)
- `hcu-envcheck/hcu_envcheck/rdma_policy.py` · modified · additions 1 / deletions 1
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/rdma_policy.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/rdma_policy.py)
- `hcu-envcheck/hcu_envcheck/roce_health.py` · modified · additions 1 / deletions 1
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/roce_health.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/roce_health.py)
- `hcu-envcheck/hcu_envcheck/verbs.py` · added · additions 45 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/hcu_envcheck/verbs.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/hcu_envcheck/verbs.py)
- `hcu-envcheck/install.sh` · modified · additions 22 / deletions 15
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/install.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/install.sh)
- `hcu-envcheck/pyproject.toml` · modified · additions 5 / deletions 2
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/pyproject.toml)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/pyproject.toml)
- `hcu-envcheck/scripts/build_release.ps1` · modified · additions 14 / deletions 2
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/scripts/build_release.ps1)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/scripts/build_release.ps1)
- `hcu-envcheck/scripts/build_release.sh` · modified · additions 11 / deletions 2
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/scripts/build_release.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/scripts/build_release.sh)
- `hcu-envcheck/scripts/test.sh` · added · additions 1257 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/scripts/test.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/scripts/test.sh)
- `hcu-envcheck/tests/test_acceptance_contract.py` · added · additions 578 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_acceptance_contract.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_acceptance_contract.py)
- `hcu-envcheck/tests/test_active_rdma.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_active_rdma.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_active_rdma.py)
- `hcu-envcheck/tests/test_baremetal.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_baremetal.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_baremetal.py)
- `hcu-envcheck/tests/test_baremetal_cluster.py` · renamed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_baremetal_cluster.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_slurm_cluster.py)
- `hcu-envcheck/tests/test_base_execution_exit.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_base_execution_exit.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_base_execution_exit.py)
- `hcu-envcheck/tests/test_benchmark_profiles.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_benchmark_profiles.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_benchmark_profiles.py)
- `hcu-envcheck/tests/test_cli_output.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_cli_output.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_cli_output.py)
- `hcu-envcheck/tests/test_cluster_report.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_cluster_report.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_cluster_report.py)
- `hcu-envcheck/tests/test_cluster_run.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_cluster_run.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_cluster_run.py)
- `hcu-envcheck/tests/test_consistency_contract.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_consistency_contract.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_consistency_contract.py)
- `hcu-envcheck/tests/test_container_preflight.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_container_preflight.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_container_preflight.py)
- `hcu-envcheck/tests/test_container_ssh.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_container_ssh.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_container_ssh.py)
- `hcu-envcheck/tests/test_container_status.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_container_status.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_container_status.py)
- `hcu-envcheck/tests/test_entrypoint.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_entrypoint.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_entrypoint.py)
- `hcu-envcheck/tests/test_environment_contract.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_environment_contract.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_environment_contract.py)
- `hcu-envcheck/tests/test_extra_interfaces.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_extra_interfaces.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_extra_interfaces.py)
- `hcu-envcheck/tests/test_ib_fabric.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_ib_fabric.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_ib_fabric.py)
- `hcu-envcheck/tests/test_k8s_cluster_scale.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_k8s_cluster_scale.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_k8s_cluster_scale.py)
- `hcu-envcheck/tests/test_k8s_nodes_file.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_k8s_nodes_file.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_k8s_nodes_file.py)
- `hcu-envcheck/tests/test_k8s_output_capture.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_k8s_output_capture.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_k8s_output_capture.py)
- `hcu-envcheck/tests/test_launch_contract.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_launch_contract.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_launch_contract.py)
- `hcu-envcheck/tests/test_new_interface.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_new_interface.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_new_interface.py)
- `hcu-envcheck/tests/test_node_script_control.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_node_script_control.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_node_script_control.py)
- `hcu-envcheck/tests/test_output.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_output.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_output.py)
- `hcu-envcheck/tests/test_parsers.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_parsers.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_parsers.py)
- `hcu-envcheck/tests/test_rdma_protocol.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_rdma_protocol.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_rdma_protocol.py)
- `hcu-envcheck/tests/test_task_control.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/2aeb7da14fe6da65110a82beaeb4cde5524cc196/hcu-envcheck/tests/test_task_control.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/ce6d9b992370c898a502056e05a21be10ae2dd04/hcu-envcheck/tests/test_task_control.py)

## Evidence and interpretation boundary

[Original JSON, discussions and patches](../../evidence/prs/HYGON-AI--cluster-manager-das/5-ddaba92177d04210b8347df7b2e4a5a3dd5616374acea328d63b0f2302d5dec1.json) · SHA-256 `ddaba92177d04210b8347df7b2e4a5a3dd5616374acea328d63b0f2302d5dec1`.

Diff complete: False. Missing/binary/truncated patches require pinned source inspection. This is a source page, not an independently verified optimization case. Open, merged and released are different states; recheck the deployed dependency.
