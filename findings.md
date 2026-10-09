# Findings

## 2026-10-09 — implementation baseline
- Approved design has 36 requirements, 106 work packages, 12 modules and exactly five Skill entrypoints.
- First release follows the first vertical development batch; no training cluster was assigned.
- Existing directory contained five planning documents and no Git repository or implementation.
- Preserve original detailed planning privately; publish reusable implementation, public-source explanations and explicit capability status only.
- Core implementation uses system Python; no CUDA/DTK/training-engine dependency is required for control-plane installation.

## Implementation evidence
- TraceLens currently exposes TraceLens_generate_perf_report_pytorch with --profile_json_path and --output_xlsx_path / --output_csvs_dir. Keep it optional and verify installed --help.
- Primus has source-guarded per-layer recomputation and two-tier DDP hooks for compile/parameter-gather interactions; useful mechanisms require version-specific review before HCU adoption.
- LoongForge carries its Megatron implementation as a pinned gitlink: parent and child commits must both be recorded.
- Python sqlite3 context managers commit/rollback but do not close connections; explicit close is required before renaming index files on Windows.

- Initial Git whitespace review detected CRLF text as trailing whitespace under this host configuration. Added a repository LF policy and normalized only the intended tracked text files; cached source bytes remain unchanged.

## HCU model adaptation clarification

- The prepare Skill and several Megatron pages said to start from official recipes, which could mislead agents into copying NVIDIA platform setup and launch commands.
- Applicable HCU scripts, their sourced environment/configuration and the user's deployment form the launch reference. Official recipes remain the model/training semantic reference; both old HCU scripts and new task changes require compatibility and correctness checks.

## Training library / integration expansion

- TE currently has one short Megatron chapter and only four monitored files; cuDNN Frontend is absent. Both need their own detailed public-source sections and tutorial monitoring.
- TraceLens is currently mentioned as an external command only. Add an executable integration and pin its source alongside the kernel Skill repository.
- Use a tracked thirdparty manifest with ignored checkouts and selective bootstrap. This retains repository identity/version without publishing private HCU-Knowledge contents or making an authenticated clone mandatory for public users.
- Verified Git access to the optional private knowledge repository; it needs its own workspace-bound Skill installer and Git LFS setup, not an unbound copy of its Skills.
- TE now marks pytorch/fp8.py deprecated in favor of quantization.py. Attention selection distinguishes fused/flash/unfused backends; userbuffer overlap tutorial has NVIDIA-specific topology/connection constraints that cannot be copied as HCU defaults.
- cuDNN Frontend includes both backend graph APIs and open-source kernel families. Current source covers Python graph backends, plan/workspace reuse, MoE activation/quantization fusions and sparse attention; open-source frontends do not imply all cuDNN backend kernels are public.
- Official website latest/stable and main source are separate revisions. Track both; do not silently infer that newly added main APIs exist in the installed release.
- TraceLens report APIs work on Windows without the unrelated CLI helper that overflows C long via csv.field_size_limit(sys.maxsize). Keep upstream unmodified and invoke report APIs in an isolated process.
- Report generation is not training validation: preserve native statistical denominators, complete rank requirements and explicit HCU architecture input. Truncated tables must still produce a failed report receipt.
- Native report, gzip and complete two-rank synthetic collective paths are locally verified. Fresh bootstrap also verified the sparse clone path, avoiding unnecessary example trace downloads.
