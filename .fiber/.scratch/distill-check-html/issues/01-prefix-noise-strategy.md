# 01 — 前缀噪音与 diff 数据来源

`Type: grilling`
`Status: open`

## Question

HTML 报告里「内容变更」的 skill 要展开 side-by-side diff。左右两栏各放什么、本地文件含 `.fiber/` 路径前缀替换的噪音怎么处理？

背景张力：本地 `plugins/fiber/skills/<skill>/*.md` 经过 `GLOBAL_REPLACEMENTS`（`docs/agents/` → `.fiber/docs/agents/`、`.scratch/` → `.fiber/.scratch/` 等）和 `SRC_FIX`，上游 `matt_src/<skill>/*.md` 是原始内容。直接 diff 两者，未变更的逻辑行也会因前缀差异显示为「改动」，淹没真实上游变化。

候选方向（非穷尽，grilling 后可重组）：

- **A. 双栏反向还原**：把本地文件的 `.fiber/` 前缀反向还原成原始路径后再 diff，左=还原后本地、右=上游新。diff 干净，但要复现 `GLOBAL_REPLACEMENTS` + `SRC_FIX` 的逆变换，逻辑与蒸馏脚本耦合。
- **B. 双栏原样 + 智能标注**：左=本地含前缀、右=上游原始，但在 diff 渲染层把「仅前缀差异」的行降级为弱标记（不当作实质改动）。需要 diff 引擎支持行级规则。
- **C. 仅展示上游新旧 diff，不混入本地**：左=上次蒸馏时的上游快照、右=新上游快照。最干净地回答「上游改了啥」，但本地没存上次的上游快照（只有 hash），需要额外从 git 历史 / 上游 commit 检出旧版本。
- **D. 混合信号**：总览用 hash 判定变更（已有，干净）；展开 diff 用方案 A 或 C 之一。

要决策的子问题：

1. side-by-side 的语义到底是「**上游改了啥**」（C，回答上游演化）还是「**本地与当前上游差啥**」（A/B，回答本地滞后多少）？两者都合理，目的不同。
2. 选定语义后，前缀噪音用反向还原（A）还是渲染层降级（B）吸收？
3. setup skill（`setup-matt-pocock-skills`）除全局替换外还有 `SETUP_REPLACEMENTS` 精细替换，diff 它时前缀噪音更复杂——是否对 setup 特殊处理，还是接受它的 diff 噪音？

## Blocked by

（无）
