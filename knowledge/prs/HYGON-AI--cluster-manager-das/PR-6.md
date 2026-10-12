---
id: pr-hygon-ai--cluster-manager-das-6
title: 'fix(ci): allow automatic fork PR unit tests'
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
pr_number: 6
updated_at: '2026-10-10T02:44:39Z'
artifact_sha256: bdf56daabb53855ad627940643cd48e0a6d2812fccd1a6d0612816e448f44d33
artifact_path: knowledge/evidence/prs/HYGON-AI--cluster-manager-das/6-bdf56daabb53855ad627940643cd48e0a6d2812fccd1a6d0612816e448f44d33.json
sources: []
generated_body_sha256: e4810a00bf4d798d97a2afb705ba8b104fd08bcc1a0ac73d9022bea4c5818939
---

# fix(ci): allow automatic fork PR unit tests

[Upstream PR](https://github.com/HYGON-AI/cluster-manager-das/pull/6) · state: closed · merged: True

## Original PR description

## Problem and change

Fork PRs currently fail at `Authorize PR source` before checkout or pytest. Remove the blanket rejection so both fork and same-repository PRs run automatically through the existing five module path filters. The workflow remains controlled by the target branch and checks out the event's immutable head SHA with persisted credentials disabled.

Run tests against an ephemeral writable copy of the read-only runner checkout. Enable executable temporary fixtures and only the SETUID/SETGID capabilities needed by cross-UID process-control tests. Keep the container offline, its root filesystem read-only, and its CPU, memory, and process count bounded. This also accommodates the new envcheck tests that create files beside the source and execute temporary mock tools.

## Validation

- actionlint and `git diff --check` passed; YAML assertions verified automatic fork checkout, immutable head SHA, and disabled persisted credentials.
- On the configured CI host, all five main-branch suites passed with the final container command: **664 passed, 121 subtests passed**.
- On the same host and image, the envcheck suite from PR #5 at `a1e688a538a2dc3e746873bbf56a0fd72e53f23e` passed: **490 passed, 264 subtests passed**.
- These are direct container validations, not an Actions run using the new workflow. Existing `pull_request_target` runs continue to use the old target-branch definition until this change is merged and a fresh qualifying PR event is emitted.

## Impact

Fork code will execute automatically in the constrained container on the configured shared runner. No approval environment or job is introduced. No production code, test cases, or nightly workflow changes.

After merging, close and reopen PR #5 or push a new commit to trigger the updated workflow. Rerunning its old failed run does not validate the new definition.


## Review and discussion

### reviews

- lvj-repox · APPROVED · 2026-10-10T02:44:07Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/6#pullrequestreview-5477200125)

(No body; status only.)

### issue_comments

### inline_comments

## Changed files and fixed code

- `.github/workflows/README.md` · modified · additions 16 / deletions 3
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/ace4113e3c2bb2fc3fa0f86d26ef5f0107e190c2/.github/workflows/README.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/.github/workflows/README.md)
- `.github/workflows/_run-unit-tests.yml` · modified · additions 15 / deletions 22
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/ace4113e3c2bb2fc3fa0f86d26ef5f0107e190c2/.github/workflows/_run-unit-tests.yml)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/.github/workflows/_run-unit-tests.yml)

## Evidence and interpretation boundary

[Original JSON, discussions and patches](../../evidence/prs/HYGON-AI--cluster-manager-das/6-bdf56daabb53855ad627940643cd48e0a6d2812fccd1a6d0612816e448f44d33.json) · SHA-256 `bdf56daabb53855ad627940643cd48e0a6d2812fccd1a6d0612816e448f44d33`.

Diff complete: True. Missing/binary/truncated patches require pinned source inspection. This is a source page, not an independently verified optimization case. Open, merged and released are different states; recheck the deployed dependency.
