# Worktree 路由表

destination 与 throwaway worktree 的单一真源。每行一条：ticket/issue — worktree 绝对路径 — 分支名 — 状态。新 session 先读本表定位自己的任务目录；创建时登记、resolve / PR 合并时清理条目并 `git worktree remove`（见 `.claude/rules/throwaway-worktree-convention.md`）。

| Ticket/issue | Worktree 路径 | 分支 | 状态 |
|---|---|---|---|
| #55（原型查看） | /Volumes/Under_M2/morphiiouo/b3oy1/.fiber/worktrees/distill-report-analysis-proto | throwaway/distill-report-analysis-proto | 原型查看（PR #57 已合并，commit 0c1a900 恢复） |

