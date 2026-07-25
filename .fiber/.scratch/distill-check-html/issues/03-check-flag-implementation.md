# 03 — `--check` flag dry-run 接入与实现

`Type: task`
`Status: open`

## Question

把前两个 ticket 的决策落地到 `scripts/distill.py`：加 `--check` 标志，跑 dry-run 检查并产出 HTML 报告，不执行任何蒸馏写入。

实现要点：

1. **flag 解析**：`python3 scripts/distill.py --check`。可加 `--check-out <path>` 覆盖默认输出路径（默认倾向 `distill-check.html`，不入库——加入 `.gitignore`）。
2. **dry-run 边界**：`--check` 下只执行 `clone()` → `read_skill_list()` → `check_buckets()` → `check_extra()`，**跳过** `copy_skills_flat` / `apply_global` / `distill_setup` / `copy_license` / `copy_extra` / `clean_agents` / `write_meta`。
3. **复用 helper**：不重写检查逻辑，直接用 `check_buckets` / `check_extra` / `skill_hash` 的返回。HTML 生成是新增的渲染层（基于 Ticket 02 的原型 + Ticket 01 的前缀策略）。
4. **退出码**：与现有约定一致——发现 bucket/extra 缺失 → exit 1；检测到变更 → exit 2（提示用户重跑正式蒸馏）；无变更 → exit 0。`--check` 同样遵循。
5. **终端输出**：保留现有 `print_check_report`（终端 UI 不丢），额外打印一行 `HTML 报告：<path>`。不自动开浏览器（见 map 的 Not yet specified）。
6. **幂等**：`--check` 多次跑不产生副作用（除临时 clone 和 HTML 文件）。

依赖 Ticket 01（前缀策略）和 Ticket 02（HTML 原型与 diff 引擎）的结论才能实现渲染层。

## Blocked by

01, 02
