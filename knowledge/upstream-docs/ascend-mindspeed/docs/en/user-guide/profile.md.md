---
id: doc-ascend-mindspeed-5f735f31bc233a1e9d10
title: Ascend/MindSpeed / docs/en/user-guide/profile.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/user-guide/profile.md
raw_sha256: 95af40c81442af12ce2073f3f3034482b027df49d7f26b81974357f967f22bbc
sources: []
generated_body_sha256: 90fa6502a52c02e7494b7e4c2a91307f87b3bee387ca729fd622cc1138480f72
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/user-guide/profile.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/user-guide/profile.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Data Profiling in MindSpeed

📝 MindSpeed supports enabling of data profiling through commands. The command configurations are as follows:

| Command Configuration    | Command Description                                                                                                                                                                                                 |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--profile`               | Enables the profiling switch                                                                                                                                                                                          |
| `--profile-step-start`    | Configures the start step for profiling. When not configured, it defaults to `10`. Configuration example: `--profile-step-start 30`                                                                                   |
| `--profile-step-end`      | Configures the end step for profiling. When not configured, it defaults to `12`. Configuration example: `--profile-step-end 35`                                                                                       |
| `--profile-level`         | Configures the profiling level. When not configured, it defaults to level0. Optional configurations: `level0`, `level1`, `level2`. Configuration example: `--profile-level level1`                                        |
| `--profile-with-cpu`      | Enables the CPU information profiling switch                                                                                                                                                                       |
| `--profile-with-stack`    | Enables the stack information profiling switch                                                                                                                                                                     |
| `--profile-with-memory`   | Enables the memory information profiling switch. When configuring this switch, `--profile-with-cpu` must be enabled                                                                                                  |
| `--profile-record-shapes` | Enables the shapes information profiling switch                                                                                                                                                                    |
| `--profile-save-path`     | Configures the save path for collected information. When not configured, it defaults to `./profile_dir`. Configuration example: `--profile-save-path ./result_dir`                                                      |
| `--profile-ranks`         | Configures the ranks to be collected. When not configured, it defaults to `-1`, indicating that profiling data for all ranks will be collected. Configuration example: `--profile-ranks 0 1 2 3`. Note: This configuration value is the global value for each rank in a single server/cluster |

---
