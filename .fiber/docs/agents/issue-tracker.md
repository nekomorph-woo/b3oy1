# Issue tracker: GitHub

本仓库的 issue 和 PRD 以 GitHub issue 形式存在。所有操作用 `gh` CLI。

## 约定

- **创建 issue**：`gh issue create --title "..." --body "..."`。多行 body 用 heredoc。
- **读 issue**：`gh issue view <number> --comments`，用 `jq` 过滤 comment、同时取 label。
- **列出 issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，按需加 `--label` / `--state` 过滤。
- **评论**：`gh issue comment <number> --body "..."`
- **加 / 移除 label**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭**：`gh issue close <number> --comment "..."`

仓库从 `git remote -v` 推断——`gh` 在 clone 内运行时自动识别。

## Pull request 作为 triage 入口

**PR 作为请求入口：否。** _（若本仓库把外部 PR 当 feature 请求处理，设为 `yes`；`/triage` 读这个开关。）_

设为 `yes` 时，PR 走与 issue 相同的 label / 状态流，用 `gh pr` 等价命令：

- **读 PR**：`gh pr view <number> --comments`，`gh pr diff <number>` 看 diff。
- **列出待 triage 的外部 PR**：`gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`，只保留 `authorAssociation` 为 `CONTRIBUTOR` / `FIRST_TIME_CONTRIBUTOR` / `NONE` 的（去掉 `OWNER` / `MEMBER` / `COLLABORATOR`）。
- **评论 / 打 label / 关闭**：`gh pr comment`、`gh pr edit --add-label` / `--remove-label`、`gh pr close`。

GitHub 的 issue 与 PR 共享编号空间，裸 `#42` 可能是任一——用 `gh pr view 42` 解析，回退到 `gh issue view 42`。

## 当 skill 说「publish to the issue tracker」

创建一个 GitHub issue。

## 当 skill 说「fetch the relevant ticket」

运行 `gh issue view <number> --comments`。

## Wayfinding 操作

供 `/wayfinder` 使用。**map** 是单个 issue，**child** issue 即 ticket。

- **Map**：单个带 `wayfinder:map` label 的 issue，承载 Notes / Decisions-so-far / Fog body。`gh issue create --label wayfinder:map`。
- **Child ticket**：作为 GitHub sub-issue 链接到 map（对 sub-issues endpoint 调 `gh api`）。sub-issues 未启用时，把 child 加进 map body 的 task list，并在 child body 顶部写 `Part of #<map>`。Label：`wayfinder:<type>`（`research` / `prototype` / `grilling` / `task`）。被 claim 后，ticket assign 给推进的 dev。
- **Blocking**：GitHub **原生 issue 依赖**——规范的、UI 可见的表示。加边：`gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`，其中 `<blocker-db-id>` 是 blocker 的数字 **database id**（`gh api repos/<owner>/<repo>/issues/<n> --jq .id`，_不是_ `#number` 或 `node_id`）。GitHub 报告 `issue_dependencies_summary.blocked_by`（仅 open blocker——活动闸门）。依赖不可用时，回退到 child body 顶部的 `Blocked by: #<n>, #<n>` 行。ticket 在每个 blocker 关闭后才 unblock。
- **Frontier 查询**：列出 map 的 open child（`gh issue list --state open`，限定到 map 的 sub-issues / task list），去掉任何有 open blocker 的（`issue_dependencies_summary.blocked_by > 0`，或 `Blocked by` 行里有 open issue）或有 assignee 的；map 顺序里第一个胜出。
- **Claim**：`gh issue edit <n> --add-assignee @me`——session 的第一次写。
- **Resolve**：`gh issue comment <n> --body "<answer>"`，然后 `gh issue close <n>`，再把 context pointer（gist + 链接）追加到 map 的 Decisions-so-far。
