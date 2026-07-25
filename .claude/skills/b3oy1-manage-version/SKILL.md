---
name: b3oy1-manage-version
description: 升级 plugin 版本并同步 plugin.json 与 marketplace.json，或审计版本一致性。Use when 用户要求升级版本、发布、bump，或提到 "版本" / "version" / "bump"，以及其他技能需要同步版本时。
---

# Manage version

升级一个 plugin 的版本并在两个文件间同步，或审计所有 plugin 是否一致。版本遵循 SemVer。

## 版本架构

    .claude-plugin/marketplace.json
    ├── metadata.version        ← marketplace 整体，独立递增
    └── plugins[].version       ← 每个 plugin，必须与 plugin.json 一致

    plugins/<name>/.claude-plugin/plugin.json
    └── version                 ← 每个 plugin，必须与 marketplace.json 一致

plugin：fiber、spin。

## 模式

| 模式 | 触发 | 行为 |
|------|------|------|
| 交互 | 用户直接调 | 询问操作类型与升级幅度 |
| 静默 | `/commit` 传 plugin 名 + 幅度 | 不问，直接升级 + 同步 |

静默输入：`manage-version <plugin-name> <patch|minor|major>`

## 升级

1. 读 `plugins/<name>/.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json` plugins[] 的当前版本
2. 按 SemVer 算新版本
3. 写两处：plugin.json 的 `version` + marketplace.json plugins[] 条目的 `version`（必须一致）
4. marketplace 的 `metadata.version` minor bump
5. 输出变更

完成标准：plugin.json 与 marketplace.json plugins[] 显示同一新版本；`metadata.version` 已 bump。

## 审计

读两个文件，报告每个 plugin 的 plugin.json 与 marketplace.json 版本。不一致时提议以 plugin.json 为准修复。

完成标准：每个 plugin 都已核对；不一致都已标记。

## SemVer

| 幅度 | 规则 | 示例 |
|------|------|------|
| patch | Z+1，X.Y 不变 | 0.1.0 → 0.1.1 |
| minor | Y+1，Z 归零 | 0.1.0 → 0.2.0 |
| major | X+1，Y.Z 归零 | 1.2.3 → 2.0.0 |
