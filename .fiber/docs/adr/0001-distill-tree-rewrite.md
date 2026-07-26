# distill ASCII 目录树路径重写

distill 对 SKILL.md 里 ASCII 目录树采用「展平节点完整路径 → 应用窄前缀重写规则 → 按新路径重建树」机制（`scripts/distill.py` 的 `_parse_tree` / `_flatten_tree` / `_rewrite_a` / `_rebuild_tree` / `_serialize_forest`），替代原先对树也做裸 `str.replace`。`.fiber/` 约定一致应用到树结构：system-wide 文档进 `.fiber/`、per-context 文档跟代码走。

## Context

`GLOBAL_REPLACEMENTS` 的裸字符串替换对正文连续路径工作良好，但 ASCII 树把路径拆成跨行片段（`docs/` 与 `adr/` 被树干分到两行），字面量命中不了跨行路径。结果同一棵树被不一致改写：单行（`CONTEXT.md`）能改、跨行（`docs/adr/`）改不了；multi-context 时 `GLOBAL` 还误伤 `src/<ctx>/` 下的 per-context 文档，`SRC_FIX` 想还原同样跨行失灵。双向错误集中在 `plugins/fiber/skills/domain-modeling/SKILL.md` 两棵树——system-wide 的 `docs/adr/` 漏改（该进 `.fiber/` 没进）、per-context 的 `CONTEXT.md` / `docs/adr/` 误改（不该带 `.fiber/` 却被错加）。唯一改对的 `setup/domain.md` 靠手工整段字面量替换，不可泛化、上游一改就 miss。

## Why

路径重写把「改树」转化为「改路径」：per-context 与根级同名文档（`CONTEXT.md`）在完整路径上可区分（`src/ordering/CONTEXT.md` 第一段是 `src`，不在系统名集合，自动不动），跨行也不再失配（节点完整路径是单字符串）。拓扑重排（`src/` 提升为新顶层）是路径重写的副产品——规则保持声明式、可审计，延续 `README.md` 的机械替换哲学（规则作用域从裸字符串升级到节点路径，哲学不变）。

## Considered Options

- **裸 `str.replace`（现状）**：跨行树路径失配，双向错误不可避免。
- **树解析 + 路径重写（选定）**：展平成节点路径 → 前缀重写 → 重建。`/prototype` 用 9 个 fixture（matt 5 目录树、codebase-design 框图、5 层深嵌套、ASCII fallback、一 fence 双根）验证全过。
- **LLM 后处理**：不可预测、不可复现，违背 distill 的机械替换哲学，弃。

## Consequences

- **扁平 `docs/adr/` 规范为层级**：rebuild 按路径分隔符建层，单行的 `docs/adr/`（如 setup `domain.md` 上游）在产物里规范成 `docs/` + `adr/` 两层。视觉形态变化但语义一致，且 `setup/domain.md` 与 `domain-modeling/SKILL.md` 两处树产物结构统一（双轨维护负担消除）。注释 `← …` 保留但不再多空格对齐（视觉 polish，后续可补）。
- **`.fiber/` 作用域 A/B**：引擎参数化支持两模式——A（默认，根级系统文档进 `.fiber/`、per-context 跟代码，与 `SRC_FIX` 注释、setup 样板、matt 上游一致）与 B（per-context 也带 `.fiber/`）。默认 A；选 A 还是 B 是另一个 domain model 决策，不阻塞本机制。
- **容错**：parse 失败（框图 `┌┐┘┤`、一 fence 多根、无节点行）保留上游原文，`--check` dry-run diff 暴露「需关注」信号而非静默产出错误结构。多根 fail-loud 不走 `GLOBAL`，让 diff 明确显示「这个树没被处理」。
- **幂等**：树 fence 不经 `GLOBAL`（避免单行路径被半改），只走路径重写；规则 A 对已带 `.fiber/` 前缀的路径幂等。distill 流程靠 `copy_skills_flat` 每次重拷上游保证 orig 是上游原始。
