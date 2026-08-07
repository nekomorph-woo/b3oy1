#!/usr/bin/env python3
"""distill 树重写机制测试。

只测 transform_fiber_md / transform_setup_text 的 text→text 外部行为,
不测 parse/flatten/rebuild/serialize 内部实现(issue #21 Testing Decisions)。
覆盖:9 个 fixture golden + 上游回归 + 幂等/一致性 + 双轨统一。
"""
import json
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
        "│   └── .fiber/\n"
        "│       ├── CONTEXT.md\n"
        "│       └── docs/adr/ ← context-specific decisions\n"
        "└── billing/\n"
        "    └── .fiber/\n"
        "        ├── CONTEXT.md\n"
        "        └── docs/adr/"
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


def test_out_of_scope_tree_idempotent():
    """.out-of-scope/ 命名根树重写后是单根 .fiber/，再跑不再 double-prefix。

    回归 triage/OUT-OF-SCOPE.md：首次 .out-of-scope/ → .fiber/.out-of-scope/ 正确，
    但对产物（.fiber/ root）再跑 _regroup_b 会把 .out-of-scope/ 又套一层 .fiber/。
    _regroup_b 对「root 已是 .fiber/ 命名空间」短路 children regroup 修复。
    """
    inp = fence(
        ".out-of-scope/\n"
        "├── dark-mode.md\n"
        "└── plugin-system.md"
    )
    once = transform_fiber_md(inp)
    assert transform_fiber_md(once) == once
    assert ".fiber/.fiber/" not in once


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


def test_per_context_prose_gets_fiber_prefix():
    """正文连续路径（规则 B）：根级与 per-context 的 CONTEXT.md 都带 .fiber/（命名空间对称）。"""
    inp = "root CONTEXT.md and src/ordering/CONTEXT.md coexist"
    expected = "root .fiber/CONTEXT.md and src/ordering/.fiber/CONTEXT.md coexist"
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
    """setup domain.md 单 context 树(扁平 docs/adr/)走新机制 → 保留扁平,与手工样板一致。

    删 SETUP_REPLACEMENTS 手工树字面量后,domain.md 树改走树重写;机制保留上游扁平形态
    (扁平 docs/adr/ 不被拆成层级),产物与原 SETUP_REPLACEMENTS 样板一致(user story 2/3)。
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
        "└── docs/adr/\n"
        "    ├── 0001-event-sourced-orders.md\n"
        "    └── 0002-postgres-for-write-model.md\n"
        "src/"
    )
    assert transform_setup_text("domain.md", inp) == expected


def test_setup_domain_multi_context_tree():
    """setup domain.md multi-context 树走新机制,system-wide 与 per-context 都保留扁平。"""
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
        "└── docs/adr/ ← system-wide decisions\n"
        "src/\n"
        "├── ordering/\n"
        "│   └── .fiber/\n"
        "│       ├── CONTEXT.md\n"
        "│       └── docs/adr/ ← context-specific decisions\n"
        "└── billing/\n"
        "    └── .fiber/\n"
        "        ├── CONTEXT.md\n"
        "        └── docs/adr/"
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
    expected = "one `.fiber/CONTEXT.md` + `.fiber/docs/adr/`"
    assert transform_setup_text("SKILL.md", inp) == expected


# ============================ 上游回归 golden(需 clone) ============================

@needs_matt
def test_upstream_domain_modeling_regression():
    """上游 domain-modeling/SKILL.md 经 transform 后：树按规则 B 正确重写。"""
    t = (MATT / "skills/engineering/domain-modeling/SKILL.md").read_text()
    out = transform_fiber_md(t)
    # system-wide 进根 .fiber/（漏改修复）
    assert ".fiber/\n├── CONTEXT.md" in out or ".fiber/\n├── CONTEXT-MAP.md" in out
    # per-context 进各 context 的 .fiber/（规则 B：命名空间对称）
    assert "ordering/\n│   └── .fiber/" in out
    assert "billing/\n    └── .fiber/" in out


@needs_matt
def test_upstream_setup_domain_regression():
    """上游 setup domain.md 经 transform 后：树按规则 B 正确重写（与新机制产物一致）。"""
    t = (MATT / "skills/engineering/setup-matt-pocock-skills/domain.md").read_text()
    out = transform_setup_text("domain.md", t)
    assert ".fiber/\n├── CONTEXT.md" in out
    assert "ordering/\n│   └── .fiber/" in out  # per-context 进各 context .fiber/（B）


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


# ============================ 逐条精细分析（#55：切分/导出/合并） ============================

def _u(*lines):
    """unified diff 文本行助手（---/+++/@@/+/-/空格 前缀保留原样）。"""
    return list(lines)


def _fake_block(title, lines):
    """fixture diff block：与 _build_diff_blocks 的产出结构对齐（键 lines）。"""
    return {"title": title, "skill": title.split(" · ")[0], "rel": title.split(" · ")[1],
            "lines": list(lines), "note": "E 方案", "id": f"diff-{title.replace(' · ', '-')}"}


# ---------- 独立变更段切分 ----------

def test_split_changes_hunk_inner_segments():
    """同一 hunk 内被上下文行分隔的多个独立变更 → 拆多条（hunk 是窗口不是粒度）。"""
    lines = _u("--- local/a.md", "+++ upstream-transformed/a.md",
               "@@ -10,8 +10,8 @@", " ctx-keep-1",
               "-old line A", "+new line A",
               " ctx-between",
               "-old line B", "+new line B",
               " ctx-keep-2")
    segs = distill.split_changes(lines)
    assert len(segs) == 2, f"期望 2 段，实际 {len(segs)}"
    assert all(s["hunk"] == "@@ -10,8 +10,8 @@" for s in segs)
    assert "-old line A" in segs[0]["lines"] and "+new line A" in segs[0]["lines"]
    assert "-old line B" in segs[1]["lines"] and "+new line B" in segs[1]["lines"]
    # 各归各条：段 2 不重复段 1 的增删行（切分不重叠）
    assert "-old line A" not in segs[1]["lines"]
    assert "+new line A" not in segs[1]["lines"]


def test_split_changes_contiguous_is_one():
    """连续增删行（无上下文行隔开）是同一段，不拆。"""
    lines = _u("--- local/a.md", "+++ upstream-transformed/a.md",
               "@@ -1,3 +1,3 @@", " ctx",
               "-line one", "-line two", "+line ONE",
               " ctx2")
    segs = distill.split_changes(lines)
    assert len(segs) == 1
    assert len([l for l in segs[0]["lines"] if l.startswith(("-", "+"))]) == 3


def test_split_changes_context_extended():
    """段行 = 连续增删行 ± 前后各 1 上下文行（@@ 行紧邻段前时自然带入）。"""
    lines = _u("--- local/a.md", "+++ upstream-transformed/a.md",
               "@@ -5,5 +5,5 @@",
               "-changed", "+changed-new",
               " ctx-after")
    segs = distill.split_changes(lines)
    seg_lines = segs[0]["lines"]
    assert seg_lines[0] == "@@ -5,5 +5,5 @@"      # @@ 紧邻段前 → 带入
    assert " ctx-after" in seg_lines              # 后 1 上下文
    # 不重叠：hunk 头只作 label，段行从增删行前 1 上下文起
    spaced = _u("@@ -5,5 +5,5 @@", " ctx-before", "-changed", "+changed-new")
    s2 = distill.split_changes(spaced)[0]["lines"]
    assert s2[0] == " ctx-before" and "@@" not in s2[0]


def test_split_changes_multi_hunk_multi_seg():
    """多 hunk 各有多段：段序号全局连续、hunk 行号各自归属。"""
    lines = _u("--- local/a.md", "+++ upstream-transformed/a.md",
               "@@ -1,3 +1,3 @@", "-a", "+A",
               "@@ -20,3 +20,3 @@", "-b", " ctx", "-c")
    segs = distill.split_changes(lines)
    assert len(segs) == 3
    assert [s["label"] for s in segs] == ["变更 1", "变更 2", "变更 3"]
    assert segs[0]["hunk"] == "@@ -1,3 +1,3 @@" and segs[2]["hunk"] == "@@ -20,3 +20,3 @@"


def test_split_changes_no_changes_empty():
    """无增删行 → 空段列表。"""
    assert distill.split_changes([" ctx only"]) == []


# ---------- 分析输入导出 ----------

def test_analyze_input_md_contains_spec_and_segments(tmp_path):
    """导出 Markdown：头部（含由谁分析 + 匹配约束）、输出规格、逐段（标题 + diff + 输出要求）。"""
    blocks = [_fake_block("engineering/wayfinder · SKILL.md",
                          _u("--- local/SKILL.md", "+++ upstream-transformed/SKILL.md",
                             "@@ -14,7 +14,7 @@", "-old", "+new"))]
    md = distill.analyze_input_md(blocks, prev_commit="ed37663c")
    assert "输出规格" in md and "summary" in md and "why" in md and "learn" in md
    assert "由谁分析" in md and "精确一致" in md          # 头部说明 + file/label 匹配约束
    assert "engineering/wayfinder · SKILL.md" in md
    assert "@@ -14,7 +14,7 @@" in md and "-old" in md and "+new" in md
    assert "产出一条分析" in md                            # 段级输出要求
    assert "ed37663c" in md


def test_analyze_input_md_segments_split():
    """导出时同一文件多个独立变更段分别出现（禁止合并）。"""
    blocks = [_fake_block("engineering/a · SKILL.md",
                          _u("--- local/SKILL.md", "+++ upstream-transformed/SKILL.md",
                             "@@ -1,5 +1,5 @@", " c", "-x", "+X", " c2", "-y", "+Y"))]
    md = distill.analyze_input_md(blocks, prev_commit="")
    assert md.count("### 变更 1") == 1 and md.count("### 变更 2") == 1


# ---------- 分析合并渲染 ----------

ANALYSIS_JSON = json.dumps([{
    "file": "engineering/wayfinder · SKILL.md", "label": "变更 1",
    "point": "名称引用规则精化。", "impact": "本地路由表无冲突。",
    "why": "裸编号墙不可读。", "learn": "名称包裹链接。",
    "action": "采纳", "detail": "检查回归测试。",
}], ensure_ascii=False)

REPORT_FIXTURE = (
    "<!doctype html><html lang=zh><meta charset=utf8><body><div class=wrap>"
    "<h1>蒸馏检查报告</h1><div class=summary></div>"
    "<section><h2>变更详情（unified diff）</h2>"
    '<details class="diff" open id="diff-engineering-wayfinder-SKILL-md">'
    "<summary>engineering/wayfinder · SKILL.md</summary>"
    '<div class="note">E 方案</div>'
    '<pre class="unified"><span class="h">--- local/SKILL.md</span>'
    '<span class="h">+++ upstream-transformed/SKILL.md</span>'
    '<span class="h">@@ -14,7 +14,7 @@</span>\n'
    '<span class="d">-old</span>\n<span class="a">+new</span></pre>'
    "</details></section></div></body></html>"
)


def test_apply_analysis_renders_grouped_section():
    """apply 后报告：分组卡 section 替换详情区段、五字段齐、徽章、diff 平铺卡内、锚点保留。"""
    out = distill.apply_analysis_to_report(REPORT_FIXTURE, ANALYSIS_JSON)
    assert "变更详情 · 逐段分析" in out
    assert "engineering/wayfinder" in out
    assert "名称引用规则精化。" in out and "裸编号墙不可读。" in out
    assert "学习要点" in out
    assert "采纳" in out
    assert "-old" in out and "+new" in out                     # diff 平铺在分组卡内
    assert "--- local/SKILL.md" in out                         # 文件头行保留（#56）
    assert "变更详情（unified diff）" not in out                # 原 flat 区段已被替换
    assert 'id="diff-engineering-wayfinder-SKILL-md"' in out   # 文件卡保留原锚点（总览/FAB 跳转有效）


def test_apply_analysis_bad_json_raises():
    """坏 JSON → 明确报错，不静默。"""
    try:
        distill.apply_analysis_to_report(REPORT_FIXTURE, "{not json")
        assert False, "应当抛错"
    except (ValueError, json.JSONDecodeError):
        pass


def test_apply_analysis_missing_field_placeholder():
    """分析条目缺字段 → 「—」占位 + 标注不完整，报告仍生成。"""
    bad = json.dumps([{"file": "engineering/wayfinder · SKILL.md", "action": "采纳"}],
                     ensure_ascii=False)
    out = distill.apply_analysis_to_report(REPORT_FIXTURE, bad)
    assert "—" in out and "采纳" in out
    assert "不完整" in out


def test_apply_analysis_unmatched_file_no_jump():
    """file 与 diff 块 title 失配 → 分析条照常渲染但无跳转。"""
    orphan = json.dumps([{"file": "engineering/ghost · X.md", "action": "采纳",
                          "point": "p", "impact": "i", "why": "w", "learn": "l"}],
                        ensure_ascii=False)
    out = distill.apply_analysis_to_report(REPORT_FIXTURE, orphan)
    assert "engineering/ghost · X.md" in out and "变更详情" in out


def test_apply_analysis_label_matching_ignores_order():
    """条目按 label 精确配对：label 乱序/与段序不一致仍落到正确段（LLM 输出顺序不稳）。"""
    multi = json.dumps([
        {"file": "engineering/wayfinder · SKILL.md", "label": "变更 2",
         "point": "B 点", "impact": "i2", "why": "w2", "learn": "l2", "action": "采纳"},
        {"file": "engineering/wayfinder · SKILL.md", "label": "变更 1",
         "point": "A 点", "impact": "i1", "why": "w1", "learn": "l1", "action": "忽略"},
    ], ensure_ascii=False)
    two_seg_report = (
        "<!doctype html><html lang=zh><meta charset=utf8><body><div class=wrap>"
        "<h1>蒸馏检查报告</h1><div class=summary></div>"
        "<section><h2>变更详情（unified diff）</h2>"
        '<details class="diff" open id="diff-w">'
        "<summary>engineering/wayfinder · SKILL.md</summary>"
        '<div class="note">E 方案</div>'
        '<pre class="unified"><span class="h">@@ -1,5 +1,5 @@</span>\n'
        '<span class="d">-old A</span>\n<span class="a">+new A</span>\n'
        ' ctx\n'
        '<span class="d">-old B</span>\n<span class="a">+new B</span></pre>'
        "</details></section></div></body></html>")
    out = distill.apply_analysis_to_report(two_seg_report, multi)
    # 段 1 的 hunk 卡后紧跟 A 点（label 配对而非位置）
    seg1 = out.split("变更 1")[1].split("变更 2")[0]
    assert "A 点" in seg1 and "B 点" not in seg1


def test_apply_analysis_badge_aggregation():
    """文件级徽章取各段最重动作：检查规则 > 忽略（忽略与采纳同为已决策）。"""
    multi = json.dumps([
        {"file": "engineering/wayfinder · SKILL.md", "label": "变更 1",
         "point": "p1", "impact": "i1", "why": "w1", "learn": "l1", "action": "忽略"},
        {"file": "engineering/wayfinder · SKILL.md", "label": "变更 2",
         "point": "p2", "impact": "i2", "why": "w2", "learn": "l2", "action": "检查规则"},
    ], ensure_ascii=False)
    two_seg_report = (
        "<!doctype html><html lang=zh><meta charset=utf8><body><div class=wrap>"
        "<h1>蒸馏检查报告</h1><div class=summary></div>"
        "<section><h2>变更详情（unified diff）</h2>"
        '<details class="diff" open id="diff-w">'
        "<summary>engineering/wayfinder · SKILL.md</summary>"
        '<div class="note">E 方案</div>'
        '<pre class="unified"><span class="h">@@ -1,5 +1,5 @@</span>\n'
        '<span class="d">-old A</span>\n<span class="a">+new A</span>\n'
        ' ctx\n'
        '<span class="d">-old B</span>\n<span class="a">+new B</span></pre>'
        "</details></section></div></body></html>")
    out = distill.apply_analysis_to_report(two_seg_report, multi)
    head = out.split('<div class="g1-head">')[1].split("</div>")[0]
    assert "检查规则" in head and "忽略" not in head


# ---------- 报告头来源行 ----------

def test_src_row_contains_both_sources(tmp_path, monkeypatch):
    """报告头来源行：上游 matt 链接+hash、本地远程地址+HEAD hash、对比基准。"""
    def fake_git(*args, **kw):
        out = "https://github.com/nekomorph-woo/b3oy1.git\n" if "remote" in args[0] else "abcdef0\n"
        return type("R", (), {"stdout": out, "returncode": 0})()
    monkeypatch.setattr(distill.subprocess, "run", fake_git)
    html = distill.write_check_report(tmp_path / "r.html", MATT, "ed37663c",
                                      {"engineering": {"content_changed": []}}, {},
                                      matt_ver="1.2.3", matt_commit="6acc160e")
    txt = (tmp_path / "r.html").read_text()
    assert "mattpocock/skills" in txt and "6acc160e" in txt
    assert "https://github.com/nekomorph-woo/b3oy1" in txt and "abcdef0" in txt
    assert "ed37663c" in txt
