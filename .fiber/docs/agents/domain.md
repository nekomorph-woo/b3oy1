# Domain 文档

工程类 skill 探索代码库时，如何消费本仓库的 domain 文档。

## 探索前先读

- **`CONTEXT.md`** 在 `.fiber/`，或
- **`CONTEXT-MAP.md`** 在 `.fiber/`（若存在）——它指向每个 context 一份 `CONTEXT.md`。读与主题相关的每一份。
- **`.fiber/docs/adr/`**——读触及你将要工作区域的 ADR。multi-context repo 里，也查 `src/<context>/docs/adr/` 的 context 范围决策。

这些文件若有不存在的，**静默继续**。不要标记其缺失，也不要预先建议创建。`/domain-modeling`（经 `/grill-with-docs` 与 `/improve-codebase-architecture` 触达）会在术语或决策真正落定时惰性创建它们。

## 文件结构

Single-context repo（大多数 repo）：

```
.fiber/
├── CONTEXT.md
└── docs/adr/
    ├── 0001-event-sourced-orders.md
    └── 0002-postgres-for-write-model.md
src/
```

Multi-context repo（存在 `.fiber/CONTEXT-MAP.md`）：

```
.fiber/
├── CONTEXT-MAP.md
└── docs/adr/                          ← 系统级决策
src/
├── ordering/
│   ├── CONTEXT.md
│   └── docs/adr/                  ← context 特定决策
└── billing/
    ├── CONTEXT.md
    └── docs/adr/
```

## 使用 glossary 的词汇

当你的输出命名一个 domain 概念（issue 标题、重构提案、假设、测试名），用 `CONTEXT.md` 里定义的术语。不要漂移到 glossary 明确避免的同义词。

若你需要的概念还不在 glossary 里，那是个信号——要么你在发明项目不用的语言（重新考虑），要么存在真实缺口（记下给 `/domain-modeling`）。

## 标记 ADR 冲突

若你的输出与现有 ADR 矛盾，明确表面化，而非静默覆盖：

> _与 ADR-0007（event-sourced orders）矛盾——但值得重开，因为…_
