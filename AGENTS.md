# Project instructions

- Keep this repository public-safe. Put site configuration, source checkouts, task data, logs, credentials and original materials in an ignored private workspace.
- Preserve one coordinator entry plus three stage Skills and two Wiki Skills. Analysis-only, environment-only and diagnosis-only are valid independent requests.
- For model adaptation, inspect applicable scripts/configs in the selected HCU repository and the user's actual deployment first. Reuse compatible HCU launch recipes; use NVIDIA upstream to check model/training semantics. Verify branch, dependencies and effective environment instead of copying NVIDIA launch commands or platform-specific variables.
- Do not refresh HCU-Knowledge as a side effect of this project's search or maintenance.
- Attach full tasks to the persistent flow review protocol. A review never substitutes for executed training evidence. Read human guidance before new experiments and transitions.
- Treat source acquisition, content review, local tests and real hardware validation as different states. Never turn missing evidence, skipped tests, fallback dispatch or empty output into a pass.
- Use the initial numerical baseline and stage-level loss checks. Preserve wall-clock denominators, overlap accounting, actual rank groups and shape-specific models.
- A remote execution timeout or controller failure can leave the process running. Reconcile the original operation before retrying. Existing site recovery remains the single recovery owner.
- When upstream files change, review related overviews, topics, cases, Skills and command/parser contracts together.
- Keep generic guidance in docs; keep development tracking in task_plan.md, findings.md and progress.md.
- Validate changes with the relevant tests and `python scripts/validate_knowledge.py`. Real HCU/site limitations must remain explicit.
