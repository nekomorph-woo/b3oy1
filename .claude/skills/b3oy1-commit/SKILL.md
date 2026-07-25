---
name: b3oy1-commit
description: 为暂存的改动写一条规范 commit，改动触及 plugin 时自动升级版本。
disable-model-invocation: true
---

# Commit

为暂存区写一条规范 commit。改动触及 plugin 时升级版本。用户提到 issue 才关联。

## 步骤

### 1. 读暂存 diff

跑 `git diff --cached --stat` 与 `git diff --cached`，据此定 **type** 与 **scope**。

完成标准：每个暂存文件都已归入 type 与 scope。

### 2. 写 message

格式：

    <type>(<scope>): <description>

- description 用仓库工作语言（本仓库开发过程用简体中文）
- 单行，祈使语气

完成标准：一行 message 说清改了什么行为，而不是列文件。

### 3. 触及 plugin 时升级版本

暂存 diff 包含 `plugins/fiber/**` 或 `plugins/spin/**` 时，升级该 plugin 版本：`feat` → minor，含 breaking → major，其余 → patch。委托 `/b3oy1-manage-version` 静默模式，同步 `plugins/<name>/.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json` 的 plugins[] 条目，并 minor bump `metadata.version`。版本文件 `git add` 纳入本次提交。

未触及 plugin 则静默跳过，不询问。

完成标准：每个被改的 plugin 在两个文件里版本一致；`metadata.version` 已 bump。

### 4. 用户提到 issue 才关联

用户消息或上下文含 `#<n>` 或 issue URL 时，追加 footer：

    Closes #<n>

没有则静默跳过，不询问。

完成标准：用户提到的每个 issue 都已关联，或无 footer。

### 5. 提交并摘要

`git commit`。按 `.claude/rules/conversation-style.md` 的变更摘要样式输出。

完成标准：commit 已创建；摘要含 type、版本升级（若有）、关联 issue（若有）、待推送计数。

## type

| type | 何时用 |
|------|--------|
| feat | 新增文件 / 函数 / 能力 |
| fix | 修复 bug |
| docs | 仅文档 |
| refactor | 重构，行为不变 |
| perf | 性能 |
| test | 测试 |
| chore | 构建 / 工具 / 依赖 |
| ci | CI 配置 |

## scope

| 路径 | scope |
|------|-------|
| `plugins/fiber/**` | fiber |
| `plugins/spin/**` | spin |
| `.claude/**` | meta |
| `scripts/**` | scripts |
| `README.md` / 根配置 | config |
| 无法判定 | core |
