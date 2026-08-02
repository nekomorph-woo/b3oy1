# Worktree 路由表

destination 与 throwaway worktree 的单一真源。每行一条：ticket/issue — worktree 绝对路径 — 分支名 — 状态。新 session 先读本表定位自己的任务目录；创建时登记、resolve / PR 合并时清理条目并 `git worktree remove`（见 `.claude/rules/throwaway-worktree-convention.md`）。

| Ticket/issue | Worktree 路径 | 分支 | 状态 |
|---|---|---|---|
|  |  |  |  |
