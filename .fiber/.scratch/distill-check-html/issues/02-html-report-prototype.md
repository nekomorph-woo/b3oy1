# 02 — HTML 报告原型与 diff 渲染方案

`Type: prototype`
`Status: open`

## Question

HTML 报告长什么样、用什么技术渲染 side-by-side diff？用一个粗稿原型来反应，把「布局」和「diff 引擎」两个问题一起具象化。

要探索的：

1. **整体布局**：顶部 summary 行（N changed · N added · N removed）→ buckets 区（engineering / productivity，每个 skill 一张状态卡片，带 hash）→ extra skills 区 → 变更详情区（折叠/展开的 side-by-side diff）。参照 `print_check_report()` 的信息层级。
2. **diff 引擎选型**：
   - Python 标准库 `difflib.HtmlDiff` 能直接产出 side-by-side HTML 表格，零依赖、与 distill.py 同语言。评估它的可读性、是否支持前缀噪音降级（关联 [Ticket 01](01-prefix-noise-strategy.md) 方案 B）。
   - 备选：生成纯数据（变更文件清单 + 左右文本），用内联 JS（如 jsdiff / diff2html 的 CDN 或内联副本）在前端渲染。更现代，但破坏「单文件自包含、可离线」的倾向。
3. **状态卡片信息**：skill 名 / 当前 hash / 上次 hash / 状态徽章（changed/added/removed/unchanged）/ bucket 归属。点击变更项跳转到对应 diff 区块。
4. **样式基线**：单文件、CSS 内联、浅色为主、变更行红绿着色（GitHub diff 风格）。不引入构建链。

产出：一个 `prototype/report.html` 粗稿（可用 distill.py 蒸馏后的本地文件 + 一次新 clone 的上游文件作真实数据），能打开看到总览 + 至少一个变更 skill 的 side-by-side diff。原型不入库最终形态，只为决策服务。

原型可带着 Ticket 01 的「假设答案」先跑（如先试方案 A 反向还原），用来反推方案可行性。

## Blocked by

（无——可带着假设并行推进；与 Ticket 01 互相校验）
