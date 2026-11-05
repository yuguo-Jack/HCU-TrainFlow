---
id: pr-ascend--mindspeed-2
title: Fix missing bias in TE sequence-parallel column linear
engine: mindspeed
stages:
- adapt
- optimize
- fault-tolerance
kind: source-pr
coverage: upstream-body-and-discussions
review_level: source-reported
runtime_validated: false
repository: Ascend/MindSpeed
pr_number: 2
updated_at: '2026-11-03T07:36:18Z'
artifact_sha256: 704462509515c3e8bfe5b5a95602dd895d5a1ecaa937221755dc2edc2da840df
artifact_path: knowledge/evidence/prs/Ascend--MindSpeed/2-704462509515c3e8bfe5b5a95602dd895d5a1ecaa937221755dc2edc2da840df.json
sources: []
generated_body_sha256: 7747231333649f3e8d6c1257f7c8d07c0b3aa2ac0d4c513459c1e844cf0c44dc
---

# Fix missing bias in TE sequence-parallel column linear

[Upstream PR](https://github.com/Ascend/MindSpeed/pull/2) · state: open · merged: False

## Original PR description

## Problem

`ColumnParallelSeq.forward` passes `None` for the bias argument to `allgather_matmul`, but did not add the supplied bias to its result. Consequently, TE sequence-parallel column-linear layers silently dropped a nonzero bias. This affects both FP8-enabled and FP8-disabled execution; it is not evidence of a defective FP8 GEMM. The non-sequence-parallel path already adds bias explicitly.

## Change

Add the supplied bias once to `output_parallel` when it is not `None`, matching the existing non-SP behavior. `skip_bias_add=True` remains correct because the outer module passes `None` to the autograd function and returns the separate bias for its caller to add.

The production change remains two lines. Backward, collectives, quantization, scaling/amax, and MC2 implementations are unchanged. This is an unconditional source correctness fix; no environment variable is needed to activate the upstream patch.

## Regression coverage

`test_column_parallel_seq_bias.py` now contains 24 parameter combinations on real TP2/SP NPU execution:

- The original 12 zero-weight forward cases isolate bias handling.
- An additional 12 nonzero-weight forward/backward cases check full tensors for output, input gradient, weight gradient, and bias gradient, rather than only norms.
- Both methods cover FP8 off/on, absent/zero/nonzero bias, and `skip_bias_add` off/on.
- Tests use BF16 parameters, `TEDelayedScaling` with `Format.HYBRID` for the enabled arm, and `gradient_accumulation_fusion=False`, `use_ascend_mc2=False`.

For the nonzero-weight fixture, each global input row is `[.125, .25, .5, 1]` repeated 16 times, weights are `.125`, and the supplied output gradient is `.25`. Under the initial E4M3 input scale, these inputs map to `[56, 112, 224, 448]`, all representable. Hand-derived expectations are unbiased output `3.75`, input gradient `2`, weight-gradient row `[1, 2, 4, 8]` repeated 16 times, and bias gradient `8`. Assertions use zero tolerance. This avoids the incorrect assumption that any BF16-exact input remains exact after FP8 scaling.

## Local verification

### Targeted bias regression

| Invocation | Unfixed source | Fixed source |
|---|---|---|
| Historical pytest run of original 12 forward cases | 2 failed, 10 passed | 12 passed, 0 skipped |
| New explicit two-worker invocation of all 24 actual test-method cases, each rank | 4 expected failures, 20 passed | 24 passed, 0 failures |

For the new invocation, the unfixed production file was restored exactly (SHA256 `8f40a81a47c369c379edcbbbd7061c76d9ecd6ae7d61c43bd847cb4b646ae0da`), while the fixed file has SHA256 `d3cb844df26934e422a0f70d179a6e702e95e8c37d112fdc675b78542956aae8`. Both arms used the same new test file. The four failures in the unfixed arm were exactly the nonzero-bias/non-skip cases for both methods and both FP8 states. All 12 new complete-gradient cases passed on both ranks of the fixed arm.

The new test-file SHA256 is `26dfd04bf5bf96e9bca1ddfee21740b6c47abd9c02fdb32f385045816e156572`, matching the file now committed in this PR. The new explicit-worker invocation took about 67.26 seconds including both arms and supervision. It is **not** a new standard-pytest collection or a whole-suite green result.

### Broader-suite MC2 failure: accepted same-node A/B isolation

The historical broader run stopped at `features/test_tflops.py::TestDotProductAttn::test_mc2_tflops` with 1 failed, 281 passed and 221 skipped (`--maxfail=1`; not all collected tests ran).

A subsequent accepted isolation invoked the unchanged upstream `run_mc2_tflops(2)` using two explicit workers per arm, sequentially on the same idle Ascend 950DT node, with the exact unfixed/fixed production files above. **Both arms failed**, and all four workers emitted the same specific signature: `OpParamMaker.cpp:453 std::bad_alloc`, followed by `aclnnAllGatherMatmulV2` / `ERR00100` through `npu_all_gather_base_mm`. One baseline peer was terminated by the controller after its counterpart failed, after it had already emitted that signature.

The baseline therefore reproduces this native error without the bias fix. This is useful isolation evidence, **not a passing MC2 test, a diagnosis of its native cause, or proof that every possible suite-order effect has been excluded**. The diagnostic supervisor returned 0 because both arms completed their bounded diagnostic protocol; the test workers did not pass. The two-arm diagnostic took about 44.36 seconds.

An earlier diagnostic had been rejected by an audit guard during dependency imports and never started its patched arm. The accepted runs above used explicitly authorized, narrow exceptions for a pinned, shell-free, argument-free `lscpu` query and dependency-created `scipy-*` temporary regular-file cleanup in each new private scratch directory. All four per-worker denial logs were empty in each accepted A/B run; no general delete/exec permission was granted. Fresh resource gates were checked, all eight NPUs were healthy/idle at completion, and no shared source/environment or device recovery was changed. The audit guard is not a native syscall sandbox.

Software identity: torch `2.7.1+cpu`, torch_npu `2.7.1.post8`, Python `3.12.13`, CANN `9.1.0`, Ascend 950DT.

## Follow-up validation status (2026-11-03)

Independent replication of this PR's tests on a pristine official container image
(MindSpeed-LLM v26.1.0 / CANN 9.1.0 / torch_npu 2.7.1.post8 / Python 3.12, Ascend 950DT),
using only `python -m pytest` with the repository's stock configuration — no custom worker
or supervisor harness:

1. **mc2_tflops pre-existing failure reconfirmed without any harness.** Running the repo's
   standard pytest against `features/test_tflops.py::TestDotProductAttn::test_mc2_tflops`
   fails identically on the unfixed base tree and on the fixed tree
   (`aclnnAllGatherMatmulV2` / `ERR00100 PTA call acl api failed` through
   `torch_npu.npu_all_gather_base_mm`). This failure is pre-existing on the base revision
   and unrelated to this change.
2. **Target-file standard pytest, unfixed base (RED).** `python -m pytest -ra
   tests_extend/unit_tests/mindspeed/te/test_column_parallel_seq_bias.py` on the base tree:
   **4 failed, 20 passed** — the 4 failures are exactly the expected nonzero-bias,
   non-skip cases (bf16 pair + FP8 pair).
3. **Target-file standard pytest, fixed tree (GREEN).** Same command on the patched tree:
   **24 passed, 8 warnings** (exit 0).

Both arms ran in the same container on the same node, back to back, with the test file
checksum-verified (SHA-256 `26dfd04bf5bf96e9bca1ddfee21740b6c47abd9c02fdb32f385045816e156572`)
before each arm. This closes the previously documented gate
`standard_pytest_current_revision_rerun` (earlier GREEN/RED evidence used an explicit
worker/executor harness; the results above reproduce it under the repository's default
pytest invocation).

## Limits and readiness

- Remains draft. The latest added cases have real NPU method-level RED/GREEN evidence, but a new standard-pytest/full-suite run and upstream CI/maintainer review are still outstanding. No CI-green or merge-ready claim is made.
- Tests are deliberately narrow: BF16 parameters, 2-D input, TP2/SP, one backward with gradient-accumulation fusion disabled. They do not establish arbitrary dimensions/dtypes, fused `main_grad` accumulation, all FP8 recipes, long-training convergence, or downstream quality.
- Inputs are identical across sequence rows and weights across TP shards, so permutation sensitivity is not established.
- The MC2 native failure remains unresolved, although it is now reproduced with and without this patch under an accepted same-node isolation.

Submitted by vincentlau2046.


## Review and discussion

### reviews

### issue_comments

- vincentlau2046 · comment · 2026-10-31T18:51:39Z · [source](https://github.com/Ascend/MindSpeed/pull/2#issuecomment-6547694805)

compile

### inline_comments

## Changed files and fixed code

- `mindspeed/te/pytorch/module/linear.py` · modified · additions 2 / deletions 0
  - [head](https://github.com/vincentlau2046/MindSpeed/blob/17f1bb727be109b152e5c2e4d74664592233b2df/mindspeed/te/pytorch/module/linear.py)
  - [base](https://github.com/Ascend/MindSpeed/blob/c2357e9ae4689cf1791a5f258217cd256ce41ce1/mindspeed/te/pytorch/module/linear.py)
- `tests_extend/unit_tests/mindspeed/te/test_column_parallel_seq_bias.py` · added · additions 145 / deletions 0
  - [head](https://github.com/vincentlau2046/MindSpeed/blob/17f1bb727be109b152e5c2e4d74664592233b2df/tests_extend/unit_tests/mindspeed/te/test_column_parallel_seq_bias.py)
  - [base](https://github.com/Ascend/MindSpeed/blob/c2357e9ae4689cf1791a5f258217cd256ce41ce1/tests_extend/unit_tests/mindspeed/te/test_column_parallel_seq_bias.py)

## Evidence and interpretation boundary

[Original JSON, discussions and patches](../../../../../../evidence/prs/Ascend--MindSpeed/2-704462509515c3e8bfe5b5a95602dd895d5a1ecaa937221755dc2edc2da840df.json) · SHA-256 `704462509515c3e8bfe5b5a95602dd895d5a1ecaa937221755dc2edc2da840df`.

Diff complete: True. Missing/binary/truncated patches require pinned source inspection. This is a source page, not an independently verified optimization case. Open, merged and released are different states; recheck the deployed dependency.
