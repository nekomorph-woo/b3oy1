# Map: 蒸馏检查 HTML 报告

`wayfinder:map`

## Destination

给 `scripts/distill.py` 增加一个 **dry-run 检查模式**（`--check` 标志）：只 clone 上游 + 跑内容检查，**不拷贝、不做路径替换、不写 meta**，产出一个自包含 HTML 单页报告。报告用 hash 总览卡片展示每个 skill 的状态（变更/新增/删除/未变），并对「内容变更」的 skill 展开左侧本地 vs 右侧上游的 side-by-side `.md` diff，让上游 matt 与本地蒸馏内容的区别一目了然。覆盖 fiber 的 engineering + productivity 两个 bucket，以及 extra/spin skill。

## Notes

- **领域脚本**：`scripts/distill.py`。检查逻辑已存在——`check_buckets()` / `check_extra()` 算每个 skill 的内容 hash（基于上游 `matt_src` 目录），对比 `DISTILL.meta.json` 里上次存的 hash，检测增/删/内容变更；`print_check_report()` 打印到终端。dry-run 模式复用这套 helper，不重写。
- **关键约束**：本地 `plugins/fiber/skills/` 的文件经过了 `GLOBAL_REPLACEMENTS`（路径前缀 `docs/agents/` `.scratch/` 等改成 `.fiber/` 前缀），**本地文件内容 ≠ 上游原始内容**。side-by-side diff 若直接拿本地文件 vs 上游原始文件，会满屏前缀噪音——这是本 effort 的核心技术张力，见 [Ticket 01：前缀噪音与 diff 数据来源](issues/01-prefix-noise-strategy.md)。
- **hash 基准干净**：`DISTILL.meta.json` 的 `skills_hash_by_bucket` 存的是**上游原始** hash（`skill_hash(matt_src/<skill>)`），不是本地蒸馏后文件的 hash。所以「哪个 skill 变了」的判定是干净的上游-对-上游对比，不受路径替换影响。受影响的只是「展开看 diff」那一步。
- **范围对齐**：HTML 总览区直接镜像 `print_check_report` 的结构——buckets 区 + extra skills 区 + changes 明细 + summary 行。
- **Tracker**：local markdown。Map 与 ticket 均在本目录下，按编号引用。
- **技能**：解 ticket 时如需 `/grilling`、`/prototype`、`/domain-modeling`，按 ticket 类型选用。

## Decisions so far

<!-- 空——charting 阶段不解决 ticket -->

## Not yet specified

- **diff 渲染粒度的边界**：展开 diff 时，是逐 `.md` 文件给全量 side-by-side，还是只列「变更文件清单 + 点击展开」？等 [Ticket 02：HTML 报告原型与 diff 渲染方案](issues/02-html-report-prototype.md) 原型出来再定，先不切片。
- **「未变更」skill 在报告里的呈现**：总览区全量列出（带「未变」标记）还是只列变更项 + 一个计数？倾向全量（与终端 UI 一致），但留给原型决策。
- **HTML 自包含 vs 外部依赖**：报告是否必须单文件自包含（CSS/JS 内联，可离线打开）？倾向是（便于分享、不入库），但原型阶段确认。
- **浏览器自动打开**：`--check` 生成后是否自动 `open` 浏览器？倾向只打印路径、不自动开（脚本可能远程跑）。小决策，实现时定。

## Out of scope

- **实际蒸馏行为**：`--check` 明确不触发拷贝、路径替换、meta 写入、agents 清理。这些归正常 `python3 scripts/distill.py`，不在本 effort。
- **非 `.md` 文件的 diff**：skill 目录里的非 markdown 文件（如未来的 yaml/json 资源）不纳入 side-by-side diff；hash 总览会覆盖整个 skill 目录（含所有文件类型），但展开 diff 只看 `.md`。
