---
id: doc-yuguo-jack-hyperloom-14257d627cb31e6a7d7a
title: yuguo-Jack/Hyperloom / docs/kernelforge/reference/deployment-modes.md
engine: hyperloom
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: yuguo-Jack/Hyperloom
commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
path: docs/kernelforge/reference/deployment-modes.md
raw_sha256: 857860c94d64a3c233bf3e32b0c35ef9f2683e78156c7f4029a946e3bc07116a
sources: []
generated_body_sha256: e47ada39cf2a6e3f7496f51a241e6b75a57ea21527c8ecfc0a08a3350ddfe776
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/kernelforge/reference/deployment-modes.md

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/kernelforge/reference/deployment-modes.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
myst:
  html_meta:
    "description": "KernelForge deployment modes: Claude Code in-session live-stream and the autonomous forge-loop."
    "keywords": "KernelForge, deployment modes, Claude Code, in-session, forge-loop, autonomous loop, billing"
---

# Deployment modes

KernelForge can run in two modes that differ in where the agent runs, how much
human oversight the run gets, and how the run is billed.

## Claude Code — native in-session live-stream (default)

Launch from inside a Claude Code session and watch every state transition, tool
call, and decision land in chat as it happens. Everything routes through the
`claude` CLI subprocess and bills to your Claude Code Max subscription.

That billing depends on the `claude` in the container being authenticated, and
the container has no `~/.claude/.credentials.json` of its own — its `claude` is a
fresh install and your host's home is not mounted in. Either mount that file or
pass `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`. An `ANTHROPIC_API_KEY`
left in the environment moves the run to API credits, since the CLI reads it
ahead of the subscription token.

## Autonomous loop — overnight optimization

```bash
kernelforge forge-loop --workspace <W> \
    --kernel <f> --driver <f> --snr-threshold 30 --max-hours 8
```

Runs unattended with the driver-owned complete correctness suite, three
independent benchmarks, and automatic git keep/revert. Stop it between
iterations with `touch <workspace>/.stop`. See
{doc}`Autonomous overnight loop </kernelforge/how-to/autonomous-loop>`.

## Comparison

| | Claude Code (default) | Autonomous loop |
|:--|:--:|:--:|
| Agent runs on | Your machine (docker) | Your machine |
| GPU tools run on | Container | Your machine |
| Human oversight | Live in chat | None (overnight) |
| Billing | Max subscription | API credits |
| Git integration | Manual | Auto commit/revert |
| Best for | Interactive debug | Overnight optimization |
