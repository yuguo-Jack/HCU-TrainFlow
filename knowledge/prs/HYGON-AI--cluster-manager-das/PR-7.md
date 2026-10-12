---
id: pr-hygon-ai--cluster-manager-das-7
title: 'update the trace_analyze code '
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
pr_number: 7
updated_at: '2026-10-10T07:27:11Z'
artifact_sha256: 8d7b17387877a2e50cdb8138f87b99cd171c26fb41384900cce6b732647c5b78
artifact_path: knowledge/evidence/prs/HYGON-AI--cluster-manager-das/7-8d7b17387877a2e50cdb8138f87b99cd171c26fb41384900cce6b732647c5b78.json
sources: []
generated_body_sha256: 739a64f0c61939730f00a79d531408d208f308c220b7e416825ddd4baa235a72
---

# update the trace_analyze code 

[Upstream PR](https://github.com/HYGON-AI/cluster-manager-das/pull/7) · state: closed · merged: False

## Original PR description

`trace_analyzer` 用于离线分析多 rank 的 PyTorch Flight Recorder 转储文件，帮助定位分布式训练中的集合通信卡住、rank 进度不一致和疑似故障 rank。
<img width="1469" height="241" alt="img_v3_0216b_1dc5de95-bdcc-4c0e-a0b2-264760ffe15g" src="https://github.com/user-attachments/assets/9797e504-1145-46f3-a330-3c7b8600ad1e" />
<img width="1227" height="658" alt="img_v3_0216b_98216dc4-989d-4915-8ac8-0e4a0f69967g" src="https://github.com/user-attachments/assets/036d5502-ff22-42bd-93eb-387cdfdee441" />


## Review and discussion

### reviews

- NLPCheng · APPROVED · 2026-10-10T07:11:44Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/7#pullrequestreview-5478087407)

(No body; status only.)

### issue_comments

- hygon-ai-reviewer[bot] · comment · 2026-10-10T06:50:06Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/7#issuecomment-6094821208)

<!-- github-ai-reviewer-progress:7:b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08 -->
## AI Review

发现 4 个问题。

### [P2] all\_pairs 中 recv 侧键值方向未转换，配对后 source/destination 颠倒

- 位置：trace\_analyzer/fr\_attribution.py（行号未确定）
- 触发条件：发送端的 send 操作未出现在 trace、仅有对端 recv 记录（即检测缺失发送者的目标场景）时。
- 证据与影响：send\_ops 以 \(src,dst\) 为键；recv\_ops 以 \(dst,src\) 为键。但 all\_pairs 里的推导式写为 set\(\(dst,src\) for dst,src in recv\_ops.keys\(\)\)，解包后再组 \(dst,src\) 等于原键原样返回，未换回 \(src,dst\)。下游统一按 for src,dst in all\_pairs 处理，recv 侧 pair 首元素被当作 src。 仅 recv 侧存在的 pair 中 send\_count 与 recv\_count 均按错误方向查表得 0，recv\_count&gt;send\_count 恒假，真正缺失的发送 rank 无法被标记，输出漏报；若存在反向流量还可能错配计数。
- 修改建议：将该推导式改为 set\(\(src,dst\) for dst,src in recv\_ops.keys\(\)\)，使 recv 键换算为 \(src,dst\) 与 send\_ops 及下游查找方向一致。

### [P3] README 快速上手示例硬编码了维护者本机路径且含个人目录名

- 位置：trace\_analyzer/README.md:93
- 触发条件：读者在 1.2 节快速上手步骤中按文档照抄进入目录的命令
- 证据与影响：“进入 \`trace\_analyzer\` 目录”下方给出的可执行示例是一段硬编码的绝对路径，指向维护者本地机器目录并包含个人用户名目录（原值不展示），在其他任何环境均不存在 照抄命令会因目录不存在而失败，阻塞上手流程；同时把维护者本机的个人目录信息提交进公开仓库，泄露不必要的个人信息
- 修改建议：替换为通用占位符，例如 cd /path/to/trace\_analyzer，或使用仓库相对路径说明，并对第 7 节涉及的目录描述保持一致

### [P3] 测试说明命令写死本机用户目录绝对路径

- 位置：trace\_analyzer/README.md（行号未确定）
- 触发条件：其他环境的用户按 README 第11节命令逐字复制执行测试时。
- 证据与影响：测试命令中 cd 的目标为写死的本机绝对用户目录（含个人用户名，原值不展示），而非仓库相对路径说明。 该命令在其他机器无法直接复现，易造成照抄执行失败；同时在公开仓库中暴露内部个人目录信息。
- 修改建议：改为通用说明（如克隆仓库后进入仓库根目录），从文档中移除具体用户目录路径。

### [P3] pickle 加载异常捕获不完整，截断文件绕过带文件名的错误包装

- 位置：trace\_analyzer/fr\_attribution.py（行号未确定）
- 触发条件：加载被截断或不完整写入的二进制转储文件时（该工具面向卡死训练场景的离线分析，强制收集的转储可能不完整）
- 证据与影响：load\_trace\_file 的 pickle 分支仅捕获 \(pickle.PickleError, FileNotFoundError, json.JSONDecodeError\)；pickle 数据流提前结束会抛出 EOFError，不属于上述类型，绕过预期的 ValueError 包装。 截断的转储文件会抛出裸 EOFError，错误信息缺少具体文件路径，与函数声明的加载失败语义（ValueError with 文件名）不一致，多 rank 场景下定位损坏文件需额外排查。
- 修改建议：在该分支的 except 中补充 EOFError（必要时一并考虑解码/序列化失败），使所有加载失败统一转为包含文件名的 ValueError。

> 部分结果不可用：1/24 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 15 个文件，已审查 7 个，部分审查 1 个，待审查 7 个。

> 进度已保存。正在继续处理。

### inline_comments

## Changed files and fixed code

- `README.md` · modified · additions 10 / deletions 1
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/README.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/README.md)
- `trace_analyzer/README.md` · added · additions 472 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/README.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/README.md)
- `trace_analyzer/README_TOPO_CONVERTER.md` · added · additions 116 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/README_TOPO_CONVERTER.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/README_TOPO_CONVERTER.md)
- `trace_analyzer/__init__.py` · added · additions 35 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/__init__.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/__init__.py)
- `trace_analyzer/capture.py` · added · additions 39 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/capture.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/capture.py)
- `trace_analyzer/fr_attribution.py` · added · additions 2119 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/fr_attribution.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/fr_attribution.py)
- `trace_analyzer/fr_support.py` · added · additions 376 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/fr_support.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/fr_support.py)
- `trace_analyzer/standalone_support.py` · added · additions 166 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/standalone_support.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/standalone_support.py)
- `trace_analyzer/tests/test_fr_attribution.py` · added · additions 667 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/tests/test_fr_attribution.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/tests/test_fr_attribution.py)
- `trace_analyzer/tests/test_topo_to_json.py` · added · additions 100 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/tests/test_topo_to_json.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/tests/test_topo_to_json.py)
- `trace_analyzer/topo.example.json` · added · additions 459 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/topo.example.json)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/topo.example.json)
- `trace_analyzer/topo.example.txt` · added · additions 14 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/topo.example.txt)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/topo.example.txt)
- `trace_analyzer/topo_to_json.py` · added · additions 443 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/topo_to_json.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/topo_to_json.py)
- `trace_analyzer/trace_analyzer.py` · added · additions 36 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/trace_analyzer.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/trace_analyzer.py)
- `trace_analyzer/trace_collector.py` · added · additions 102 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/b14b3f4bc91a8ca7d50806befd52e8ed6a68cf08/trace_analyzer/trace_collector.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/trace_analyzer/trace_collector.py)

## Evidence and interpretation boundary

[Original JSON, discussions and patches](../../evidence/prs/HYGON-AI--cluster-manager-das/7-8d7b17387877a2e50cdb8138f87b99cd171c26fb41384900cce6b732647c5b78.json) · SHA-256 `8d7b17387877a2e50cdb8138f87b99cd171c26fb41384900cce6b732647c5b78`.

Diff complete: True. Missing/binary/truncated patches require pinned source inspection. This is a source page, not an independently verified optimization case. Open, merged and released are different states; recheck the deployed dependency.
