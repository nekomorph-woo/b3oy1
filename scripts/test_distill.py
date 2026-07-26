#!/usr/bin/env python3
"""distill 树重写机制测试。

只测 transform_fiber_md / transform_setup_text 的 text→text 外部行为,
不测 parse/flatten/rebuild/serialize 内部实现(issue #21 Testing Decisions)。
覆盖:9 个 fixture golden + 上游回归 + 幂等/一致性 + 双轨统一。
"""
import sys
import pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import distill  # noqa: E402
from distill import transform_fiber_md, transform_setup_text  # noqa: E402

# 单方真源：MATT 复用 distill.TMP，不重复硬编码（conversation-style「单方真源」）
MATT = distill.TMP
needs_matt = pytest.mark.skipif(not MATT.exists(), reason="matt 上游未 clone 到 /tmp/matt-src")


def fence(body, lang=""):
    """把 body 包进一个 code fence。body 末尾不带换行。"""
    return f"```{lang}\n{body}\n```\n"


# ============================ 树 golden(规则 A) ============================

def test_single_context_tree():
    """domain-modeling 单 context 树:system-wide 进 .fiber/,src/ 留根级(森林)。"""
    inp = fence(
        "/\n"
        "├── CONTEXT.md\n"
        "├── docs/\n"
        "│   └── adr/\n"
        "│       ├── 0001-event-sourced-orders.md\n"
        "│       └── 0002-postgres-for-write-model.md\n"
        "└── src/"
    )
    expected = fence(
        ".fiber/\n"
        "├── CONTEXT.md\n"
        "└── docs/\n"
        "    └── adr/\n"
        "        ├── 0001-event-sourced-orders.md\n"
        "        └── 0002-postgres-for-write-model.md\n"
        "src/"
    )
    assert transform_fiber_md(inp) == expected


def test_multi_context_tree():
    """multi-context:根级进 .fiber/,per-context(src/ 下)不动 → 修复双向错误。

    上游里 per-context 的 CONTEXT.md / docs/adr/ 是单行,GLOBAL 能匹配会误加 .fiber/;
    SRC_FIX 想还原却跨行失配。路径重写靠完整路径区分,per-context 不动。
    """
    inp = fence(
        "/\n"
        "├── CONTEXT-MAP.md\n"
        "├── docs/\n"
        "│   └── adr/                          ← system-wide decisions\n"
        "├── src/\n"
        "│   ├── ordering/\n"
        "│   │   ├── CONTEXT.md\n"
        "│   │   └── docs/adr/                 ← context-specific decisions\n"
        "│   └── billing/\n"
        "│       ├── CONTEXT.md\n"
        "│       └── docs/adr/"
    )
    expected = fence(
        ".fiber/\n"
        "├── CONTEXT-MAP.md\n"
        "└── docs/\n"
        "    └── adr/ ← system-wide decisions\n"
        "src/\n"
        "├── ordering/\n"
        "│   ├── CONTEXT.md\n"
        "│   └── docs/\n"
        "│       └── adr/ ← context-specific decisions\n"
        "└── billing/\n"
        "    ├── CONTEXT.md\n"
        "    └── docs/\n"
        "        └── adr/"
    )
    assert transform_fiber_md(inp) == expected


def test_out_of_scope_tree():
    """triage OUT-OF-SCOPE:.out-of-scope/ 是命名根 → 整棵进 .fiber/。"""
    inp = fence(
        ".out-of-scope/\n"
        "├── dark-mode.md\n"
        "├── plugin-system.md\n"
        "└── graphql-api.md"
    )
    expected = fence(
        ".fiber/\n"
        "└── .out-of-scope/\n"
        "    ├── dark-mode.md\n"
        "    ├── plugin-system.md\n"
        "    └── graphql-api.md"
    )
    assert transform_fiber_md(inp) == expected


def test_deep_nesting_preserved():
    """5 层深嵌套:非系统名分支保真,树重写只移系统名。"""
    inp = fence(
        "/\n"
        "└── src/\n"
        "    └── a/\n"
        "        └── b/\n"
        "            └── c/\n"
        "                └── d/\n"
        "                    └── file.md"
    )
    expected = fence(
        "src/\n"
        "└── a/\n"
        "    └── b/\n"
        "        └── c/\n"
        "            └── d/\n"
        "                └── file.md"
    )
    assert transform_fiber_md(inp) == expected


def test_ascii_fallback():
    """ASCII fallback 风格(+-- / |)也能解析;产物规范为 box-drawing(user story 6/13)。"""
    inp = fence(
        "/\n"
        "+-- CONTEXT.md\n"
        "+-- docs/\n"
        "|   +-- adr/\n"
        "+-- src/"
    )
    expected = fence(
        ".fiber/\n"
        "├── CONTEXT.md\n"
        "└── docs/\n"
        "    └── adr/\n"
        "src/"
    )
    assert transform_fiber_md(inp) == expected


# ============================ 框图 / 多根 fail-loud ============================

def test_box_art_preserved():
    """codebase-design 框图含 ┌┐┘┤ → 判非树,原样保留(user story 4)。"""
    body = (
        "┌─────────────────────┐\n"
        "│   Small Interface   │  ← Few methods, simple params\n"
        "├─────────────────────┤\n"
        "│  Deep Implementation│  ← Complex logic hidden\n"
        "└─────────────────────┘"
    )
    inp = fence(body)
    assert transform_fiber_md(inp) == inp


def test_box_art_connectors_preserved():
    """框图连线字符 ┬┴┼（T 型/十字）也判非树——_BOX_ART 覆盖角落之外的连线字符。"""
    body = (
        "┌────────┬────────┐\n"
        "│  Left  │  Right │\n"
        "└────────┴────────┘"
    )
    inp = fence(body)
    assert transform_fiber_md(inp) == inp


def test_multi_root_skip():
    """一 fence 双根:fail-loud 原样保留,--check diff 暴露(user story 5)。"""
    body = (
        "root-a/\n"
        "├── a.md\n"
        "root-b/\n"
        "├── b.md"
    )
    inp = fence(body)
    assert transform_fiber_md(inp) == inp


def test_no_node_passthrough():
    """无节点行的 fence(普通代码)不当作树,走 GLOBAL(现状)。"""
    inp = fence("just some text without tree nodes\nCONTEXT.md mentioned")
    expected = fence("just some text without tree nodes\n.fiber/CONTEXT.md mentioned")
    assert transform_fiber_md(inp) == expected


# ============================ 回归保护(非树行为不变) ============================

def test_prose_global_unchanged():
    """非 fence 的正文 prose:GLOBAL 字面量替换行为不变。"""
    inp = "See docs/agents/ for config. CONTEXT.md at root. docs/adr/ holds ADRs."
    expected = ("See .fiber/docs/agents/ for config. .fiber/CONTEXT.md at root. "
                ".fiber/docs/adr/ holds ADRs.")
    assert transform_fiber_md(inp) == expected


def test_src_fix_still_restores_per_context_in_prose():
    """正文连续路径：根级 CONTEXT.md 进 .fiber/，src/<ctx>/ 下 per-context 由 SRC_FIX 还原。"""
    inp = "root CONTEXT.md and src/ordering/CONTEXT.md coexist"
    expected = "root .fiber/CONTEXT.md and src/ordering/CONTEXT.md coexist"
    assert transform_fiber_md(inp) == expected


def test_idempotent_single_tree():
    """树重写幂等：纯树文本再跑一次树重写不变化（树 fence 不经 GLOBAL，不累积前缀）。

    注意：整文 transform 对含 prose 的文本不幂等——GLOBAL 对已带 .fiber/ 前缀的连续路径
    会二次加前缀；distill 流程靠 copy_skills_flat 每次重拷上游保证 orig 是上游原始，
    所以现实中不会对已蒸馏产物再变换。这里只守树重写部分的幂等。
    """
    inp = fence("/\n├── CONTEXT.md\n├── docs/\n│   └── adr/\n└── src/")
    once = transform_fiber_md(inp)
    assert transform_fiber_md(once) == once


def test_prose_and_tree_coexist():
    """prose 与树 fence 混合：prose 走 GLOBAL、树走路径重写，互不干扰。"""
    inp = ("See docs/agents/ for config.\n\n"
           + fence("/\n├── CONTEXT.md\n└── src/"))
    out = transform_fiber_md(inp)
    assert out.startswith("See .fiber/docs/agents/ for config.")
    assert ".fiber/\n└── CONTEXT.md\n" in out
    assert "\nsrc/\n" in out


def test_apply_writes_same_as_transform(tmp_path, monkeypatch):
    """一致性:apply_global 写盘内容 == transform_fiber_md(上游原文)。

    spec Testing Decisions 要求 dry-run 与 apply 共用同一变换——端到端守住 apply
    不在 transform 之外额外改动写盘内容（--check 报告可信的前提）。
    """
    skill = tmp_path / "fake-skill"
    skill.mkdir()
    md = skill / "SKILL.md"
    orig = fence("/\n├── CONTEXT.md\n└── src/") + "See docs/agents/ here.\n"
    md.write_text(orig)
    monkeypatch.setattr(distill, "SKILLS_DIR", tmp_path)
    distill.apply_global()
    assert md.read_text() == transform_fiber_md(orig)


# ============================ setup skill(双轨统一) ============================

def test_setup_domain_single_context_tree():
    """setup domain.md 单 context 树(扁平 docs/adr/)走新机制 → 与 domain-modeling 产物一致。

    删 SETUP_REPLACEMENTS 手工树字面量后,domain.md 树改走树重写;扁平 docs/adr/
    被 rebuild 规范为层级 docs/+adr/(user story 3 双轨统一 / 13 视觉一致)。
    """
    inp = fence(
        "/\n"
        "├── CONTEXT.md\n"
        "├── docs/adr/\n"
        "│   ├── 0001-event-sourced-orders.md\n"
        "│   └── 0002-postgres-for-write-model.md\n"
        "└── src/"
    )
    expected = fence(
        ".fiber/\n"
        "├── CONTEXT.md\n"
        "└── docs/\n"
        "    └── adr/\n"
        "        ├── 0001-event-sourced-orders.md\n"
        "        └── 0002-postgres-for-write-model.md\n"
        "src/"
    )
    assert transform_setup_text("domain.md", inp) == expected


def test_setup_domain_multi_context_tree():
    """setup domain.md multi-context 树走新机制,产物与 domain-modeling 一致。"""
    inp = fence(
        "/\n"
        "├── CONTEXT-MAP.md\n"
        "├── docs/adr/                          ← system-wide decisions\n"
        "└── src/\n"
        "    ├── ordering/\n"
        "    │   ├── CONTEXT.md\n"
        "    │   └── docs/adr/                  ← context-specific decisions\n"
        "    └── billing/\n"
        "        ├── CONTEXT.md\n"
        "        └── docs/adr/"
    )
    expected = fence(
        ".fiber/\n"
        "├── CONTEXT-MAP.md\n"
        "└── docs/\n"
        "    └── adr/ ← system-wide decisions\n"
        "src/\n"
        "├── ordering/\n"
        "│   ├── CONTEXT.md\n"
        "│   └── docs/\n"
        "│       └── adr/ ← context-specific decisions\n"
        "└── billing/\n"
        "    ├── CONTEXT.md\n"
        "    └── docs/\n"
        "        └── adr/"
    )
    assert transform_setup_text("domain.md", inp) == expected


def test_setup_semantic_replacements_kept():
    """删树字面量后,SETUP_REPLACEMENTS 的语义措辞(tracker local-first)仍生效。"""
    inp = ("where issues live (GitHub by default; local markdown is also supported "
           "out of the box)")
    expected = ("where issues live (local markdown, GitHub, or GitLab — follow the "
                "user's intent, all first-class)")
    assert transform_setup_text("SKILL.md", inp) == expected


def test_setup_skill_md_no_tree_passthrough():
    """setup SKILL.md 的语义措辞替换保留;无树则树重写无副作用。"""
    inp = "one `CONTEXT.md` + `docs/adr/` at the repo root"
    expected = "one `CONTEXT.md` + `docs/adr/` at `.fiber/`"
    assert transform_setup_text("SKILL.md", inp) == expected


# ============================ 上游回归 golden(需 clone) ============================

@needs_matt
def test_upstream_domain_modeling_regression():
    """上游 domain-modeling/SKILL.md 经 transform 后：树正确（修复双向错误）。"""
    t = (MATT / "skills/engineering/domain-modeling/SKILL.md").read_text()
    out = transform_fiber_md(t)
    # system-wide 进 .fiber（漏改修复）
    assert ".fiber/\n├── CONTEXT.md" in out or ".fiber/\n├── CONTEXT-MAP.md" in out
    # per-context 不带 .fiber（误改修复）
    assert "ordering/.fiber/" not in out
    assert "billing/.fiber/" not in out
    # per-context CONTEXT.md 原样跟在 ordering/ 下
    assert "ordering/\n│   ├── CONTEXT.md" in out


@needs_matt
def test_upstream_setup_domain_regression():
    """上游 setup domain.md 经 transform 后：树正确（与新机制产物一致）。"""
    t = (MATT / "skills/engineering/setup-matt-pocock-skills/domain.md").read_text()
    out = transform_setup_text("domain.md", t)
    assert ".fiber/\n├── CONTEXT.md" in out
    assert "ordering/.fiber/" not in out


@needs_matt
def test_upstream_triage_regression():
    """上游 triage/OUT-OF-SCOPE.md 的 .out-of-scope/ 树进 .fiber/。"""
    t = (MATT / "skills/engineering/triage/OUT-OF-SCOPE.md").read_text()
    out = transform_fiber_md(t)
    assert ".fiber/\n└── .out-of-scope/" in out


@needs_matt
def test_upstream_codebase_design_box_art_regression():
    """上游 codebase-design/SKILL.md 的框图原样保留。"""
    t = (MATT / "skills/engineering/codebase-design/SKILL.md").read_text()
    out = transform_fiber_md(t)
    # 框图字符完好
    assert "┌─────────────────────┐" in out
    assert "└─────────────────────┘" in out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
