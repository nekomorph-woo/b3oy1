#!/usr/bin/env python3
"""蒸馏 mattpocock/skills 的 22 个核心 skill 到 plugins/fiber/skills/。

策略：config 驱动 + 全局路径前缀替换。
- GLOBAL：对所有非-setup skill 的 .md，把 matt 路径前缀统一加 .fiber/
  （docs/agents/ .scratch/ .out-of-scope/ docs/adr/ CONTEXT.md CONTEXT-MAP.md）
- SETUP：setup-matt-pocock-skills 单独精确处理（tracker 默认→local、domain file-structure
  块重排、multi-context src/ 保护），因为它生成 config，路径是它的产物。
- 文件名全保留；skill 灵魂不动；幂等可复跑。

跑法：python3 scripts/distill.py
"""
import argparse
import difflib
import html as _html
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = "https://github.com/mattpocock/skills"
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent                # b3oy1/
FIBER = ROOT / "plugins" / "fiber"
SKILLS_DIR = FIBER / "skills"
TMP = Path("/tmp/matt-src")

SETUP_NAME = "setup-matt-pocock-skills"

# 白名单 bucket：只蒸馏这些目录下的 skill（白名单语义，matt 新增目录默认不取）。
INCLUDED_BUCKETS = ["engineering", "productivity"]

# 额外单独蒸馏的 skill（非白名单 bucket，各自落到 target plugin，剥离 strip 列出的文件）。
EXTRA_SKILLS = [
    # extra skill 的 per-skill 剥离用 strip 字段（剥非 openai.yaml 的文件）。
    # agents/openai.yaml 由 clean_agents 统一处理，不在这里重复。
    {"bucket": "personal", "name": "edit-article", "target": "spin"},
]

# 全局替换：对所有非 setup skill 的所有 .md 应用（路径前缀，机械安全）。
# 注意：CONTEXT-MAP.md 必须在 CONTEXT.md 之前（虽不互含，保险）。
GLOBAL_REPLACEMENTS = [
    ("CONTEXT-MAP.md", ".fiber/CONTEXT-MAP.md"),
    ("CONTEXT.md", ".fiber/CONTEXT.md"),
    ("docs/agents/", ".fiber/docs/agents/"),
    ("docs/adr/", ".fiber/docs/adr/"),
    (".scratch/", ".fiber/.scratch/"),
    (".out-of-scope/", ".fiber/.out-of-scope/"),
]

# 后处理修正：全局替换会误伤 src/<context>/ 下的 per-context 文档（multi-context 时
# per-context CONTEXT.md/docs/adr 跟代码走，不加 .fiber/）。还原它们。
SRC_FIX = re.compile(r"(src/[\w-]+)/\.fiber/(CONTEXT(?:-MAP)?\.md|docs/adr/)")

# setup skill 的精确替换（语义 + file-structure 块 + multi-context src/ 保护）。
SETUP_REPLACEMENTS = {
    "SKILL.md": [
        ("docs/agents/", ".fiber/docs/agents/"),
        # 默认 tracker: GitHub → local markdown（fiber 哲学：本地持久追溯）
        ("where issues live (GitHub by default; local markdown is also supported out of the box)",
         "where issues live (local markdown, GitHub, or GitLab — follow the user's intent, all first-class)"),
        ("Default posture: these skills were designed for GitHub. If a `git remote` points at GitHub, propose that.",
         "Default posture: follow the user's intent — local markdown, GitHub, and GitLab are all first-class, "
         "none privileged. Infer from signals (`git remote`, existing `.fiber/.scratch/`) and confirm; "
         "honor whatever the user prefers."),
        # 探查路径加 .fiber/
        ("`CONTEXT.md` and `CONTEXT-MAP.md` at the repo root",
         "`.fiber/CONTEXT.md` and `.fiber/CONTEXT-MAP.md`"),
        ("`docs/adr/` and any `src/*/docs/adr/` directories",
         "`.fiber/docs/adr/` and any `src/*/docs/adr/` directories"),
        ("`.scratch/` — sign that a local-markdown issue tracker",
         "`.fiber/.scratch/` — sign that a local-markdown issue tracker"),
        ("write a markdown file under `.scratch/`",
         "write a markdown file under `.fiber/.scratch/`"),
        ("issues live as files under `.scratch/<feature>/`",
         "issues live as files under `.fiber/.scratch/<feature>/`"),
        # domain root 措辞
        ("one `CONTEXT.md` + `docs/adr/` at the repo root",
         "one `CONTEXT.md` + `docs/adr/` at `.fiber/`"),
        ("a root `CONTEXT-MAP.md` pointing to per-context",
         "a `.fiber/CONTEXT-MAP.md` pointing to per-context"),
    ],
    "domain.md": [
        ("**`CONTEXT.md`** at the repo root, or",
         "**`CONTEXT.md`** at `.fiber/`, or"),
        ("**`CONTEXT-MAP.md`** at the repo root if it exists",
         "**`CONTEXT-MAP.md`** at `.fiber/` if it exists"),
        ("**`docs/adr/`** — read ADRs",
         "**`.fiber/docs/adr/`** — read ADRs"),
        ("presence of `CONTEXT-MAP.md` at the root",
         "presence of `.fiber/CONTEXT-MAP.md`"),
        # file structure 块的 ASCII 目录树不再手工整段字面量替换——交由
        # _apply_tree_rewrite 的路径重写统一处理（见 transform_setup_text）。
        # 上游树结构更新后自动正确，无需在此维护 old/new 字面量（issue #21 双轨统一）。
    ],
    "issue-tracker-local.md": [
        (".scratch/", ".fiber/.scratch/"),
    ],
}


def step(msg):
    print(f"• {msg}", flush=True)


def clone():
    if TMP.exists():
        shutil.rmtree(TMP)
    step(f"clone {REPO} → {TMP}")
    subprocess.run(["git", "clone", "--depth", "1", REPO, str(TMP)], check=True)
    commit = subprocess.run(
        ["git", "-C", str(TMP), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return commit


def read_skill_list():
    pj = json.loads((TMP / ".claude-plugin/plugin.json").read_text())
    return pj["skills"], pj["version"]


def check_buckets(matt_src):
    """蒸馏前检查：白名单 bucket 存在性 + skill 增删 + 内容变更（vs 上次 meta）。
    返回 (errors, changes, current)。current = {bucket: {skill: hash}}。"""
    errors = []
    current = {}
    for bucket in INCLUDED_BUCKETS:
        bdir = matt_src / "skills" / bucket
        if not bdir.is_dir():
            errors.append(f"白名单 bucket 不存在：matt skills/{bucket}/（matt 可能已删除/重命名，需更新 INCLUDED_BUCKETS）")
            continue
        current[bucket] = {}
        for d in bdir.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                current[bucket][d.name] = skill_hash(d)
    changes = {}
    prev_meta = FIBER / ".claude-plugin" / "DISTILL.meta.json"
    if prev_meta.exists():
        try:
            prev = json.loads(prev_meta.read_text())
            prev_by_bucket = prev.get("skills_hash_by_bucket", {})
            if prev_by_bucket:  # 有基准才检测
                for bucket in INCLUDED_BUCKETS:
                    prev_skills = prev_by_bucket.get(bucket, {})
                    if isinstance(prev_skills, list):  # 旧 schema（list，无 hash）
                        prev_skills = {s: None for s in prev_skills}
                    curr = current.get(bucket, {})
                    added = sorted(set(curr) - set(prev_skills))
                    removed = sorted(set(prev_skills) - set(curr))
                    content_changed = sorted(
                        s for s in (set(curr) & set(prev_skills))
                        if prev_skills[s] and curr[s] != prev_skills[s]
                    )
                    if added or removed or content_changed:
                        changes[bucket] = {
                            "added": added,
                            "removed": removed,
                            "content_changed": content_changed,
                        }
        except (json.JSONDecodeError, KeyError):
            pass  # meta 损坏，跳过
    return errors, changes, current


NOISE_NAMES = {".DS_Store", "openai.yaml"}
NOISE_PARTS = {"__pycache__"}


def skill_hash(skill_dir):
    """skill 目录的内容 hash：所有文件的相对路径 + 内容排序后 sha256，取 12 位。
    文件增删/内容改/路径变都会改变 hash。"""
    import hashlib
    h = hashlib.sha256()
    files = sorted(
        f for f in skill_dir.rglob("*")
        if f.is_file()
        and f.name not in NOISE_NAMES
        and not (NOISE_PARTS & set(f.relative_to(skill_dir).parts))
    )
    for fpath in files:
        rel = fpath.relative_to(skill_dir).as_posix()
        h.update(rel.encode() + b"\0")
        h.update(fpath.read_bytes() + b"\0")
    return h.hexdigest()[:12]


def print_check_report(errors, changes, current, prev_commit, extra_current=None, extra_changes=None):
    """蒸馏前检查 UI：buckets + extra skills + 变更明细 + summary。"""
    head = f" vs 上次 meta ({prev_commit[:8]})" if prev_commit else ""
    print(f"\n🔍 蒸馏前检查{head}")
    print("\nbuckets")
    for bucket in INCLUDED_BUCKETS:
        if bucket in current:
            print(f"  ✓ {bucket:<14} {len(current[bucket])} skills")
        else:
            print(f"  ✗ {bucket:<14} missing")
    if extra_current:
        print("\nextra skills")
        for c in extra_current:
            print(f"  ✓ {c['target']}/{c['name']:<16} {c['hash']}  (from {c['bucket']})")
    n_add = sum(len(c["added"]) for c in changes.values())
    n_rem = sum(len(c["removed"]) for c in changes.values())
    n_chg = sum(len(c["content_changed"]) for c in changes.values())
    total = sum(len(v) for v in current.values())
    if changes or extra_changes:
        print("\nchanges")
        for bucket, ch in changes.items():
            for s in ch["added"]:
                print(f"  + {bucket}/{s}    added")
            for s in ch["removed"]:
                print(f"  - {bucket}/{s}    removed")
            for s in ch["content_changed"]:
                print(f"  ~ {bucket}/{s}    content changed")
        for ch in (extra_changes or []):
            sym = {"added": "+", "removed": "-", "content_changed": "~"}[ch["kind"]]
            print(f"  {sym} extra/{ch['name']:<16} {ch['kind']}")
    n_unch = total - n_add - n_chg
    extra_n = len(extra_current) if extra_current else 0
    extra_chg = len([c for c in (extra_changes or []) if c["kind"] == "content_changed"])
    tail = f"  |  {extra_n} extra · {extra_chg} changed" if extra_current else ""
    print(f"\n{total} bucket skills · {n_chg} changed · {n_add} added · {n_rem} removed · {n_unch} unchanged{tail}")


def check_extra(matt_src):
    """检查 extra skills：存在性 + hash 变更（vs 上次 meta）。返回 (errors, changes, current)。"""
    errors = []
    current = []
    for ex in EXTRA_SKILLS:
        sdir = matt_src / "skills" / ex["bucket"] / ex["name"]
        if not (sdir.is_dir() and (sdir / "SKILL.md").exists()):
            errors.append(f"extra skill 不存在：matt skills/{ex['bucket']}/{ex['name']}/")
            continue
        current.append({**ex, "hash": skill_hash(sdir)})
    changes = []
    prev_meta = FIBER / ".claude-plugin" / "DISTILL.meta.json"
    if prev_meta.exists():
        try:
            prev = json.loads(prev_meta.read_text())
            prev_hashes = {e["name"]: e.get("hash") for e in prev.get("extra_skills", [])}
            curr_names = {c["name"] for c in current}
            for c in current:
                if c["name"] not in prev_hashes:
                    changes.append({"name": c["name"], "kind": "added"})
                elif prev_hashes[c["name"]] and prev_hashes[c["name"]] != c["hash"]:
                    changes.append({"name": c["name"], "kind": "content_changed"})
            for n in prev_hashes:
                if n not in curr_names:
                    changes.append({"name": n, "kind": "removed"})
        except (json.JSONDecodeError, KeyError):
            pass
    return errors, changes, current


def copy_extra(matt_src):
    """拷贝 extra skills 到各自 target plugin/skills/，剥离 strip 列出的文件。返回拷贝的 name。"""
    copied = []
    for ex in EXTRA_SKILLS:
        src = matt_src / "skills" / ex["bucket"] / ex["name"]
        target_skills = ROOT / "plugins" / ex["target"] / "skills"
        target_skills.mkdir(parents=True, exist_ok=True)
        dst = target_skills / ex["name"]
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        for s in ex.get("strip", []):
            sf = dst / s
            if sf.is_file():
                sf.unlink()
            elif sf.is_dir():
                shutil.rmtree(sf)
        copied.append(f"{ex['target']}/{ex['name']}")
    return copied


def clean_agents():
    """蒸馏后通用清理：移除每个 skill 的 agents/openai.yaml（Codex 配置，Claude Code 不用）；
    agents/ 清空后删空目录。作用于 fiber + spin 的所有 skill。返回 (删 yaml 的 skill, 删空 dir 的 skill)。"""
    removed = []
    emptied = []
    for skills_root in [FIBER / "skills", ROOT / "plugins" / "spin" / "skills"]:
        if not skills_root.exists():
            continue
        for skill_dir in skills_root.iterdir():
            if not skill_dir.is_dir():
                continue
            agents_dir = skill_dir / "agents"
            oy = agents_dir / "openai.yaml"
            if oy.is_file():
                oy.unlink()
                removed.append(skill_dir.name)
            if agents_dir.is_dir() and not any(agents_dir.iterdir()):
                agents_dir.rmdir()
                emptied.append(skill_dir.name)
    return removed, emptied


def copy_skills_flat(skills):
    if SKILLS_DIR.exists():
        shutil.rmtree(SKILLS_DIR)
    SKILLS_DIR.mkdir(parents=True)
    names = []
    for entry in skills:
        rel = entry.replace("./", "", 1)            # skills/engineering/ask-matt
        name = Path(rel).name                        # ask-matt
        src = TMP / rel
        dst = SKILLS_DIR / name
        if not src.is_dir():
            print(f"  ⚠ skip (not dir): {entry}", file=sys.stderr)
            continue
        shutil.copytree(src, dst)
        names.append(name)
    return names


# ============================ ASCII 目录树重写（issue #21） ============================
# GLOBAL_REPLACEMENTS 的裸字符串替换对 ASCII 树跨行路径失配：docs/ 与 adr/ 被树干拆到
# 两行，`docs/adr/` 命中不了。结果同一棵树被半改——单行（CONTEXT.md）改了、跨行（docs/adr/）
# 漏改；multi-context 时 GLOBAL 还误伤 src/<ctx>/ 下的 per-context 文档，SRC_FIX 想还原
# 同样跨行失灵。双向错误集中在 domain-modeling/SKILL.md 两棵树。
#
# 机制（/prototype 验证）：把树展平成节点完整路径 → 对路径应用窄前缀重写规则 →
# 按新路径重建树 → serialize。拓扑重排（src/ 提升为顶层）是路径重写的副产品。per-context
# 与根级同名文档（CONTEXT.md）在完整路径上可区分，跨行也不再失配。parse 失败（框图、多根、
# 无节点）保留原文，--check diff 暴露「需关注」信号（延续 distill.py:565-566 容错哲学）。

# 节点行：前导（|│ 空格）+ 分支（├└，ASCII fallback +）+ 连接（──/--，2+）+ 空格 + 名字[ ← 注释]
_TREE_NODE = re.compile(r'^([|│ ]*)([├└+])([─-]{2,}) (.+?)\s*$')
# 框图字符出现（角落 ┌┐┘┤ + 连线 ┬┴┼）→ 判为非树（原样保留，不当作目录树处理）
_BOX_ART = re.compile(r'[┌┐┘┤┬┴┼]')
# 根级系统文档名：规则 A 下进 .fiber/；per-context（src/ 下）靠完整路径第一段区分，不动。
# 与 GLOBAL_REPLACEMENTS 同源：字面量替换管正文连续路径，此处管树节点路径段——新增系统
# 文档时两处都要加（GLOBAL 加 old→.fiber/old 对，此处加路径段名）。
_SYSTEM_NAMES = frozenset({'CONTEXT.md', 'CONTEXT-MAP.md', 'docs', '.scratch', '.out-of-scope'})

# 代码 fence：```lang\n ... \n```（非贪婪，跨行）
_FENCE = re.compile(r'```[^\n]*\n.*?\n```', re.S)


def _parse_tree(body_lines):
    """把 fence 内的行解析成 (root_name, children)。

    返回:
      ('skip', reason) — 多根树，fail-loud 原样保留（--check 报警，不静默合并）
      None             — 非树（框图 / 无节点 / 非法结构），调用方按 passthrough 处理
      (root, children) — 解析成功；children=[{'name','is_dir','comment','children'}, ...]
    """
    if _BOX_ART.search('\n'.join(body_lines)):
        return None
    root_name = None
    node_lines = []
    for raw in body_lines:
        if not raw.strip():
            continue
        if _TREE_NODE.match(raw):
            node_lines.append(raw)
            continue
        # 非节点非空行：root 或多根信号
        if root_name is None:
            if raw[0].isspace() or raw[0] in '│|':
                return None  # 首个非节点行带前导，非法
            root_name = raw.strip()
        else:
            if not (raw[0].isspace() or raw[0] in '│|'):
                # 顶格第二行：仅当确有节点行才是 multi-root fail-loud；否则是普通文本（非树）
                return ('skip', f'multi-root: {raw.strip()!r}') if node_lines else None
            return None  # root 之后又出现带前导的非节点行，非标准树
    if root_name is None or not node_lines:
        return None

    children = []
    stack = [(-1, children)]  # (depth, sibling_list)
    for raw in node_lines:
        m = _TREE_NODE.match(raw)
        leading, rest = m.group(1), m.group(4)
        if '←' in rest:
            name_part, _, comment = rest.partition('←')
            name, comment = name_part.rstrip(), comment.strip()
        else:
            name, comment = rest.rstrip(), None
        depth = len(leading) // 4
        node = {'name': name, 'is_dir': name.endswith('/'), 'comment': comment, 'children': []}
        while stack and stack[-1][0] >= depth:
            stack.pop()
        stack[-1][1].append(node)
        stack.append((depth, node['children']))
    return (root_name, children)


def _flatten_tree(root_name, children):
    """展平成 [(full_path, is_dir, comment)]，DFS 序（保留原树顺序，供 rebuild 保序）。

    匿名根 `/` 不产出路径条目（其子直接为顶层）；命名根（如 .out-of-scope/）本身作为
    一条路径，使规则 A 把整棵命名树移进 .fiber/。
    """
    paths = []
    if root_name == '/':
        base = ''
    else:
        base = root_name.rstrip('/')
        paths.append((base + '/', True, None))
    def dfs(prefix, nodes):
        for node in nodes:
            full = prefix + node['name']
            paths.append((full, node['is_dir'], node['comment']))
            if node['children']:
                dfs(full if full.endswith('/') else full + '/', node['children'])
    dfs(base + '/' if base else '', children)
    return paths


def _rewrite_a(full):
    """规则 A（默认）：根级系统文档进 .fiber/，src/ 下 per-context 不动。

    per-context 靠完整路径第一段区分：src/ordering/CONTEXT.md 第一段是 src，不在
    _SYSTEM_NAMES，自动不动——这是「路径重写」相对「裸字符串替换」的根本优势。
    """
    first = full.lstrip('/').split('/')[0]
    if first in _SYSTEM_NAMES:
        return '.fiber/' + full.lstrip('/')
    return full.lstrip('/')


def _rewrite_b(full):
    """规则 B（占位）：per-context 的系统文档也带 .fiber（放各 context 自己的 .fiber/ 下）。

    A/B 的最终决策不阻塞本机制（issue #21 Out of Scope）；引擎参数化支持两模式，默认 A。
    """
    out = []
    for seg in full.split('/'):
        if seg in _SYSTEM_NAMES:
            out.append('.fiber')
        out.append(seg)
    return '/'.join(out).lstrip('/')


def _rebuild_tree(paths):
    """按重写后路径重建森林（trie，子节点按首次出现顺序保持）。返回顶层 dict。"""
    forest = {}
    for (full, is_dir, comment) in paths:
        segs = [s for s in full.split('/') if s]
        if not segs:
            continue
        cur_children = forest
        node = None
        for seg in segs:
            if seg not in cur_children:
                cur_children[seg] = {'children': {}, 'is_dir': False, 'comment': None}
            node = cur_children[seg]
            cur_children = node['children']
        node['is_dir'] = is_dir  # 最后一段：原始节点是否目录（中间段由有 children 隐含目录）
        if comment:
            node['comment'] = comment
    return forest


def _serialize_forest(forest):
    """森林 → 行列表（box-drawing，多根顶格紧邻，注释单空格不对齐）。"""
    lines = []
    for name in forest:
        node = forest[name]
        display = name + ('/' if (node['children'] or node['is_dir']) else '')
        lines.append(display + (f' ← {node["comment"]}' if node['comment'] else ''))
        _serialize_children(node['children'], '', lines)
    return lines


def _serialize_children(children, prefix, lines):
    names = list(children)
    for i, name in enumerate(names):
        node = children[name]
        last = i == len(names) - 1
        display = name + ('/' if (node['children'] or node['is_dir']) else '')
        connector = '└── ' if last else '├── '
        lines.append(prefix + connector + display + (f' ← {node["comment"]}' if node['comment'] else ''))
        if node['children']:
            _serialize_children(node['children'], prefix + ('    ' if last else '│   '), lines)


def _rewrite_tree_body(body, rule='a'):
    """对单个 fence body（不含围栏）尝试树重写。

    返回 (kind, new_body):
      ('tree', str)        — 是树，已重写
      ('skip', body)       — 多根 fail-loud，原样
      ('passthrough', body)— 非树（框图/无节点/非法），原样
    """
    parsed = _parse_tree(body.splitlines())
    if isinstance(parsed, tuple) and parsed and parsed[0] == 'skip':
        return ('skip', body)
    if parsed is None:
        return ('passthrough', body)
    root_name, children = parsed
    fn = _rewrite_a if rule == 'a' else _rewrite_b
    paths = [(fn(p), d, c) for (p, d, c) in _flatten_tree(root_name, children)]
    forest = _rebuild_tree(paths)
    return ('tree', '\n'.join(_serialize_forest(forest)))


def _apply_tree_rewrite(text, base_transform=None):
    """对 text 内的树 fence 应用路径重写。

    base_transform: 对非 fence 文本与 passthrough fence 的额外变换（None=原样）。
    树 fence 走树重写（不经 base_transform，避免 GLOBAL 对跨行树半改）；
    skip（多根）原样保留（fail-loud，diff 暴露）；passthrough（非树）走 base_transform
    保持现状语义。
    """
    out, pos = [], 0
    for m in _FENCE.finditer(text):
        before = text[pos:m.start()]
        out.append(base_transform(before) if base_transform else before)
        fence_text = m.group(0)
        first_nl = fence_text.index('\n')
        last_nl = fence_text.rindex('\n')
        lang = fence_text[3:first_nl]
        body = fence_text[first_nl + 1:last_nl]
        kind, new_body = _rewrite_tree_body(body)
        if kind == 'tree':
            out.append(f'```{lang}\n{new_body}\n```')
        elif kind == 'passthrough' and base_transform:
            out.append(base_transform(fence_text))
        else:  # skip 原样 / passthrough 无 base_transform
            out.append(fence_text)
        pos = m.end()
    tail = text[pos:]
    out.append(base_transform(tail) if base_transform else tail)
    return ''.join(out)


def _global_transform(text):
    """GLOBAL 路径前缀替换 + SRC_FIX 还原（原 transform_fiber_md 的字面量逻辑，纯函数）。"""
    for old, new in GLOBAL_REPLACEMENTS:
        text = text.replace(old, new)
    return SRC_FIX.sub(r'\1/\2', text)


def transform_fiber_md(text):
    """对单个非-setup skill 的 .md 文本应用路径约定（纯函数，text→text）。

    树 fence（ASCII 目录树）走路径重写（parse→flatten→rewrite→rebuild→serialize），
    克服 GLOBAL 裸字符串替换对跨行树路径的失配（issue #21）。其余文本（prose、非树
    fence）走 GLOBAL+SRC_FIX，行为不变。

    供 apply_global（写盘）与 --check dry-run（E 方案右侧上游变换）共用同一变换核心——
    「若现在重跑 distill，本地每个 .md 会变成什么样」可预测、可复现、幂等。
    """
    return _apply_tree_rewrite(text, base_transform=_global_transform)


def _global_hits(orig):
    """统计 orig 上每条 GLOBAL_REPLACEMENTS 规则的命中数（供 apply_global report）。"""
    return [(old, new, n) for old, new in GLOBAL_REPLACEMENTS if (n := orig.count(old))]


def apply_global():
    """对所有非-setup skill 的所有 .md 应用全局路径前缀替换（写盘）。"""
    report = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name == SETUP_NAME:
            continue
        for md in sorted(skill_dir.rglob("*.md")):
            orig = md.read_text()
            text = transform_fiber_md(orig)
            if text != orig:
                md.write_text(text)
                report[f"{skill_dir.name}/{md.relative_to(skill_dir)}"] = _global_hits(orig)
    return report


def transform_setup_text(fname, text):
    """对 setup skill 指定文件的文本应用 SETUP_REPLACEMENTS + 树重写（纯函数，text→text）。

    SETUP_REPLACEMENTS 只保留语义措辞规则（tracker local-first、domain root 措辞等）；
    ASCII 目录树（domain.md 的 file-structure 块）改走 _apply_tree_rewrite 路径重写，
    与 transform_fiber_md 共用同一树处理逻辑（双轨统一，issue #21）。

    与 transform_fiber_md 同理：distill_setup（写盘）与 --check dry-run（E 方案右侧上游变换）
    共用。若 SETUP_REPLACEMENTS 的 old 串在上游失配，上游原文保留——dry-run diff 会暴露
    「SETUP_REPLACEMENTS 需更新」的信号（非噪音，见 #4 子问题 3 决策）。
    """
    for old, new in SETUP_REPLACEMENTS.get(fname, []):
        text = text.replace(old, new)
    return _apply_tree_rewrite(text, base_transform=None)


def distill_setup():
    setup_dir = SKILLS_DIR / SETUP_NAME
    if not setup_dir.exists():
        print(f"  ⚠ setup skill not found at {setup_dir}", file=sys.stderr)
        return {}
    report = {}
    for fname, pairs in SETUP_REPLACEMENTS.items():
        f = setup_dir / fname
        if not f.exists():
            print(f"  ⚠ {fname} not in setup, skip", file=sys.stderr)
            continue
        orig = f.read_text()
        text = transform_setup_text(fname, orig)
        if text != orig:
            f.write_text(text)
        report[fname] = [(old, new, orig.count(old)) for old, new in pairs]
    return report


def copy_license():
    dst_dir = FIBER / "reference" / "matt"
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(TMP / "LICENSE", dst_dir / "LICENSE")


def write_meta(commit, version, count, skills_by_bucket, extra_skills):
    meta = {
        "source": {
            "repo": "mattpocock/skills",
            "url": REPO,
            "version": version,
            "commit": commit,
            "license": "MIT",
        },
        "distilled_at": date.today().isoformat(),
        "included_buckets": INCLUDED_BUCKETS,
        "skills_hash_by_bucket": skills_by_bucket,
        "extra_skills": extra_skills,
        "distilled_skills": count,
        "distill_strategy": "config-driven + global path-prefix: all non-setup skills "
                            "path-replaced to .fiber/ (docs/agents .scratch .out-of-scope "
                            "docs/adr CONTEXT.md); setup separately fine-tuned (tracker "
                            "default→local, domain file-structure, multi-context src/ kept); "
                            "filenames preserved; included buckets flattened",
        "namespace": ".fiber/",
        "update_note": "Only included_buckets distilled (deprecated/in-progress/misc/personal "
                       "intentionally skipped). git diff <commit>..HEAD -- skills/{engineering,productivity}; rerun distill.py",
    }
    meta_file = FIBER / ".claude-plugin" / "DISTILL.meta.json"
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


# ============================ --check HTML 报告 ============================
# 报告形态：#5 prototype 选定方案——A 卡片总览（全量 skill + 状态徽章，变更卡可点跳转）
# + A 折叠外壳（details/summary + note）+ C unified 红绿 diff + 右下角悬浮导航。
# diff 数据源：#4 E 方案——左=本地原样、右=上游在内存跑蒸馏变换后（双边同形态，消除前缀噪音）。
# 产物约定：ADR-0001——默认 distill-check.html（仓库根），每次覆盖，--check-out 可改路径，不入库。

_REPORT_CSS = """
:root { --g:#1f2328; --muted:#57606a; --bg:#f6f8fa; --card:#fff; --bd:#d0d7de;
  --add:#1a7f37; --addbg:#dafbe1; --del:#cf222e; --delbg:#ffebe9; --chg:#bf8700; --chgbg:#fff8c5;
  --addbd:#2da44e; --delbd:#cf222e; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body { font: 14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; margin:0; color:var(--g); background:var(--bg); }
.wrap { max-width: 1100px; margin: 0 auto; padding: 24px 20px 80px; }
h1 { font-size: 18px; margin: 0 0 4px; }
.sub { color: var(--muted); font-size: 12px; margin-bottom: 16px; }
.summary { display:flex; gap:8px; flex-wrap:wrap; font-size:13px; background:var(--card);
  border:1px solid var(--bd); border-radius:8px; padding:10px 14px; margin-bottom:18px; align-items:center; }
.summary b { font-variant-numeric: tabular-nums; }
.pill { padding:1px 8px; border-radius:999px; font-size:12px; font-weight:600; }
.pill.chg { background:var(--chgbg); color:var(--chg); }
.pill.add { background:var(--addbg); color:var(--add); }
.pill.del { background:var(--delbg); color:var(--del); }
.pill.unc { background:#eaeef2; color:var(--muted); }
section { background:var(--card); border:1px solid var(--bd); border-radius:8px; padding:14px 16px; margin-bottom:16px; }
section > h2 { font-size:13px; margin:0 0 10px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }
.cards { display:grid; grid-template-columns: repeat(auto-fill, minmax(220px,1fr)); gap:8px; }
.card { border:1px solid var(--bd); border-radius:6px; padding:8px 10px; background:#fff; }
.card.changed { border-color:var(--chg); background:#fffbe8; }
.card.added { border-color:var(--addbd); background:var(--addbg); }
.card.removed { border-color:var(--delbd); background:var(--delbg); }
.card .n { font-weight:600; }
.card .h { font: 11px ui-monospace,monospace; color:var(--muted); margin-top:2px; }
a.card { text-decoration:none; color:inherit; display:block; }
a.card.jump { cursor:pointer; }
a.card.jump:hover { box-shadow: 0 0 0 2px var(--chg); transform: translateY(-1px); transition: box-shadow .12s, transform .12s; }
.badge { float:right; font-size:11px; font-weight:700; }
.badge.unchanged{color:var(--muted);} .badge.changed{color:var(--chg);}
.badge.added{color:var(--add);} .badge.removed{color:var(--del);}
details.diff { border:1px solid var(--bd); border-radius:6px; margin-top:8px; background:#fff; scroll-margin-top: 12px; }
details.diff > summary { cursor:pointer; padding:8px 12px; font-weight:600; font-size:13px; }
.note { color:var(--muted); font-size:11px; padding:0 12px 4px; }
pre.unified { font:12px ui-monospace,monospace; background:#fff; margin:0; padding:8px 12px;
  overflow:auto; white-space:pre-wrap; }
pre.unified span.a { color:var(--add); background:var(--addbg); display:block; }
pre.unified span.d { color:var(--del); background:var(--delbg); display:block; }
pre.unified span.h { color:var(--chg); display:block; }
.collapsed-list { color:var(--muted); font-size:12px; }
.hint { font-size:11px; color:var(--muted); margin-top:6px; }
.fab-nav { position: fixed; right: 22px; bottom: 22px; z-index: 50; }
.fab-orb { width: 40px; height: 40px; border-radius: 50%; background: var(--chg);
  color: #fff; display:flex; align-items:center; justify-content:center;
  font-weight:700; font-size:14px; box-shadow: 0 2px 10px rgba(0,0,0,.22);
  cursor: pointer; margin-left: auto; transition: transform .12s; }
.fab-icon { width: 20px; height: 20px; }
.fab-nav:hover .fab-orb { transform: scale(1.08); }
.fab-list { position: absolute; right: 0; bottom: 48px; width: 280px; max-height: 0;
  overflow: hidden; background: var(--card); border: 1px solid var(--bd);
  border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,.16); opacity: 0;
  transform: translateY(6px); transition: opacity .18s ease, transform .18s ease, max-height .18s ease; }
.fab-nav:hover .fab-list { opacity: 1; transform: translateY(0); max-height: 60vh; overflow:auto; }
.fab-head { font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); padding: 8px 12px 4px; }
.fab-list a { display:block; padding: 8px 12px; font-size: 12px; border-top: 1px solid #eaeef2;
  text-decoration:none; color: var(--g); }
.fab-list a:hover { background: #f6f8fa; color: var(--chg); }
"""

_STATUS_CN = {"unchanged": "未变", "changed": "变更", "added": "新增", "removed": "删除"}


def _slug(s):
    """标题 → HTML id 片段（小写、非字母数字归一为 -）。"""
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def _badge(status):
    return f'<span class="badge {status}">{_STATUS_CN[status]}</span>'


def _pill_row(s):
    parts = [f'<span><b>{s["total"]}</b> skills</span>',
             f'<span class="pill chg">{s["chg"]} 变更</span>',
             f'<span class="pill add">{s["add"]} 新增</span>',
             f'<span class="pill del">{s["del"]} 删除</span>',
             f'<span class="pill unc">{s["unc"]} 未变</span>']
    if s.get("extra_n") is not None:
        parts.append(f'<span><b>{s["extra_n"]}</b> extra</span>')
    return "".join(parts)


def _unified_body(lines):
    """unified diff 行 → 红绿 HTML（增行绿、删行红、hunk/文件头黄）。"""
    body = []
    for l in lines:
        esc = _html.escape(l)
        if l.startswith("+++") or l.startswith("---") or l.startswith("@"):
            body.append(f'<span class="h">{esc}</span>')
        elif l.startswith("+"):
            body.append(f'<span class="a">{esc}</span>')
        elif l.startswith("-"):
            body.append(f'<span class="d">{esc}</span>')
        else:
            body.append(esc + "\n")
    return "".join(body)


def _load_prev_hashes():
    """从 DISTILL.meta.json 读上次基准。返回 (prev_by_bucket, prev_extra, prev_commit)。"""
    prev_meta = FIBER / ".claude-plugin" / "DISTILL.meta.json"
    if not prev_meta.exists():
        return {}, {}, ""
    try:
        m = json.loads(prev_meta.read_text())
    except json.JSONDecodeError:
        return {}, {}, ""
    by_bucket = {}
    for b, skills in m.get("skills_hash_by_bucket", {}).items():
        if isinstance(skills, list):  # 旧 schema（list，无 hash）
            skills = {s: None for s in skills}
        by_bucket[b] = skills
    extra = {e["name"]: e.get("hash") for e in m.get("extra_skills", [])}
    return by_bucket, extra, m.get("source", {}).get("commit", "")


def _build_diff_blocks(matt_src, changes, ex_changes):
    """对 content_changed 的 skill 产 unified diff 块（#4 E 方案：右=上游在内存跑变换）。

    added/removed 无 side-by-side 对应，仅在总览标状态。返回 [{title,lines,note,id,skill_key}]。
    """
    blocks = []
    for bucket, ch in changes.items():
        for skill in ch.get("content_changed", []):
            is_setup = (skill == SETUP_NAME)
            up_dir = matt_src / "skills" / bucket / skill
            local_dir = SKILLS_DIR / skill
            if not local_dir.is_dir():
                continue
            for up_md in sorted(up_dir.rglob("*.md")):
                rel = up_md.relative_to(up_dir).as_posix()
                local_md = local_dir / rel
                if not local_md.exists():
                    continue
                left = local_md.read_text()
                right_raw = up_md.read_text()
                if is_setup:
                    right = transform_setup_text(rel, right_raw)
                    note = ("E 方案 · 左=本地原样 · 右=上游跑 SETUP_REPLACEMENTS"
                            "（old 失配保留上游原文 → 暴露「规则需更新」信号，非噪音）")
                    tofile = f"upstream-transformed/{rel}"
                else:
                    right = transform_fiber_md(right_raw)
                    note = "E 方案 · 左=本地原样 · 右=上游跑 GLOBAL_REPLACEMENTS+SRC_FIX"
                    tofile = f"upstream-transformed/{rel}"
                lines = list(difflib.unified_diff(
                    left.splitlines(), right.splitlines(),
                    fromfile=f"local/{rel}", tofile=tofile, lineterm=""))
                if not lines:
                    continue
                blocks.append({
                    "title": f"{bucket}/{skill} · {rel}", "lines": lines, "note": note,
                    "id": f"diff-{_slug(bucket)}-{_slug(skill)}-{_slug(rel)}",
                    "skill_key": f"{bucket}/{skill}",
                })
    for ch in ex_changes or []:
        if ch["kind"] != "content_changed":
            continue
        name = ch["name"]
        ex = next((e for e in EXTRA_SKILLS if e["name"] == name), None)
        if not ex:
            continue
        up_dir = matt_src / "skills" / ex["bucket"] / name
        local_dir = ROOT / "plugins" / ex["target"] / "skills" / name
        if not local_dir.is_dir():
            continue
        for up_md in sorted(up_dir.rglob("*.md")):
            rel = up_md.relative_to(up_dir).as_posix()
            local_md = local_dir / rel
            if not local_md.exists():
                continue
            lines = list(difflib.unified_diff(
                local_md.read_text().splitlines(), up_md.read_text().splitlines(),
                fromfile=f"local/{rel}", tofile=f"upstream/{rel}", lineterm=""))
            if not lines:
                continue
            blocks.append({
                "title": f"extra/{name} · {rel}", "lines": lines,
                "note": "左=本地原样 · 右=上游原样（extra 不变换）",
                "id": f"diff-extra-{_slug(name)}-{_slug(rel)}",
                "skill_key": f"extra/{name}",
            })
    return blocks


def _render_card(r, label, sub, first_diff):
    """有 diff 的变更卡渲染成 <a>（跳转到首个 diff），否则普通 <div>。"""
    target = first_diff.get(r["skill_key"])
    prev_str = f' ← {r["prev"]}' if r.get("status") == "changed" and r.get("prev") else ""
    inner = f'{_badge(r["status"])}<div class="n">{label}</div><div class="h">{sub}{prev_str}</div>'
    if target:
        return f'<a class="card {r["status"]} jump" href="#{target}">{inner}</a>'
    return f'<div class="card {r["status"]}">{inner}</div>'


def write_check_report(out_path, matt_src, prev_commit, changes, ex_changes):
    """生成 --check HTML 报告并写盘。返回退出码：有变更=2，无变更=0。"""
    prev_by_bucket, prev_extra, _ = _load_prev_hashes()

    rows = []
    for bucket in INCLUDED_BUCKETS:
        bdir = matt_src / "skills" / bucket
        if not bdir.is_dir():
            continue
        prev = prev_by_bucket.get(bucket, {})
        seen = set()
        for d in sorted(bdir.iterdir()):
            if not (d.is_dir() and (d / "SKILL.md").exists()):
                continue
            name, h = d.name, skill_hash(d)
            seen.add(name)
            if name not in prev:
                status = "added"
            elif prev[name] is None or prev[name] == h:
                status = "unchanged"
            else:
                status = "changed"
            rows.append({"name": name, "bucket": bucket, "hash": h,
                         "prev": prev.get(name) or "—", "status": status,
                         "skill_key": f"{bucket}/{name}"})
        for name in sorted(set(prev) - seen):
            rows.append({"name": name, "bucket": bucket, "hash": "—",
                         "prev": prev[name], "status": "removed",
                         "skill_key": f"{bucket}/{name}"})

    extra_rows = []
    for ex in EXTRA_SKILLS:
        sdir = matt_src / "skills" / ex["bucket"] / ex["name"]
        if not (sdir.is_dir() and (sdir / "SKILL.md").exists()):
            continue
        name, h = ex["name"], skill_hash(sdir)
        if name not in prev_extra:
            status = "added"
        elif prev_extra[name] is None or prev_extra[name] == h:
            status = "unchanged"
        else:
            status = "changed"
        extra_rows.append({"name": name, "target": ex["target"], "bucket": ex["bucket"],
                           "hash": h, "prev": prev_extra.get(name) or "—", "status": status,
                           "skill_key": f"extra/{name}"})

    blocks = _build_diff_blocks(matt_src, changes, ex_changes)
    first_diff = {}
    for b in blocks:
        first_diff.setdefault(b["skill_key"], b["id"])

    summary = {
        "total": len([r for r in rows if r["status"] != "removed"]),
        "chg": len([r for r in rows if r["status"] == "changed"]),
        "add": len([r for r in rows if r["status"] == "added"]),
        "del": len([r for r in rows if r["status"] == "removed"]),
        "unc": len([r for r in rows if r["status"] == "unchanged"]),
        "extra_n": len(extra_rows) if extra_rows else None,
    }
    has_change = bool(changes or ex_changes)

    out = [f'<!doctype html><html lang=zh><meta charset=utf8>'
           f"<meta name=viewport content='width=device-width,initial-scale=1'>"
           f"<title>蒸馏检查报告</title><style>{_REPORT_CSS}</style><body><div class=wrap>"]
    out.append(f'<h1>蒸馏检查报告 <span class="sub">dry-run · vs 上次 meta {prev_commit[:8] or "—"}</span></h1>')
    out.append(f'<div class="summary">{_pill_row(summary)}</div>')
    for bucket in INCLUDED_BUCKETS:
        bs = [r for r in rows if r["bucket"] == bucket]
        out.append(f'<section><h2>bucket: {bucket} · {len(bs)} skills</h2><div class="cards">')
        out.extend(_render_card(r, r["name"], r["hash"], first_diff) for r in bs)
        out.append('</div></section>')
    if extra_rows:
        out.append('<section><h2>extra skills</h2><div class="cards">')
        out.extend(_render_card(r, f'{r["target"]}/{r["name"]}',
                                f'from {r["bucket"]} · {r["hash"]}', first_diff)
                  for r in extra_rows)
        out.append('</div></section>')
    out.append('<section><h2>变更详情（unified diff）</h2>')
    for b in blocks:
        out.append(f'<details class="diff" open id="{b["id"]}"><summary>{_html.escape(b["title"])}</summary>'
                   f'<div class="note">{b["note"]}</div>'
                   f'<pre class="unified">{_unified_body(b["lines"])}</pre></details>')
    if not blocks:
        out.append('<p class="collapsed-list">无内容变更。</p>')
    out.append('</section>')
    out.append('<p class="hint">dry-run 检查报告 · E 方案 diff（左=本地原样，右=上游跑蒸馏变换）· 不写入任何蒸馏产物</p>')

    if blocks:
        items = "".join(f'<a href="#{b["id"]}">{_html.escape(b["title"])}</a>' for b in blocks)
        orb = ('<svg class="fab-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
               'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round">'
               '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/>'
               '<path d="M9 10h6"/><path d="M12 13V7"/><path d="M9 17h6"/></svg>')
        out.append(f'<div class="fab-nav"><div class="fab-orb" title="变更导航">{orb}</div>'
                   f'<div class="fab-list"><div class="fab-head">变更详情 · {len(blocks)}</div>'
                   f'{items}</div></div>')

    out.append('</div></body></html>')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(out), encoding="utf-8")
    return 2 if has_change else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="distill.py",
        description="蒸馏 mattpocock/skills。--check 进入 dry-run 检查模式（只检查 + 产 HTML 报告，不写入）。",
    )
    parser.add_argument("--check", action="store_true",
                        help="dry-run：clone + 检查 + 产 HTML 报告，跳过所有蒸馏写入")
    parser.add_argument("--check-out", metavar="PATH", default="distill-check.html",
                        help="--check 的 HTML 报告输出路径（默认：仓库根 distill-check.html，每次覆盖）")
    args = parser.parse_args(argv)

    step("dry-run 检查模式" if args.check else "蒸馏开始")
    commit = clone()
    skills, version = read_skill_list()
    step(f"matt version={version} commit={commit[:8]} skills={len(skills)}")

    # 检查（蒸馏前 / dry-run 共用）：bucket 存在 + skill 增删 + 内容变更 + extra skills
    errors, changes, current = check_buckets(TMP)
    ex_errors, ex_changes, ex_current = check_extra(TMP)
    prev_meta = FIBER / ".claude-plugin" / "DISTILL.meta.json"
    prev_commit = ""
    if prev_meta.exists():
        try:
            prev_commit = json.loads(prev_meta.read_text()).get("source", {}).get("commit", "")
        except Exception:
            pass
    print_check_report(errors, changes, current, prev_commit, ex_current, ex_changes)
    if errors or ex_errors:
        print("\n❌ 终止（bucket 或 extra skill 缺失）")
        for e in list(errors) + list(ex_errors):
            print(f"  ERROR: {e}")
        sys.exit(1)

    if args.check:
        out_path = Path(args.check_out)
        if not out_path.is_absolute():
            out_path = ROOT / out_path
        rc = write_check_report(out_path, TMP, prev_commit, changes, ex_changes)
        print(f"\nHTML 报告：{out_path}")
        print(f"  打开：open '{out_path}'")
        sys.exit(rc)

    names = copy_skills_flat(skills)
    step(f"拷贝 {len(names)} skills（平铺）→ {SKILLS_DIR.relative_to(ROOT)}")
    global_report = apply_global()
    step(f"全局路径替换：{len(global_report)} 个文件命中")
    setup_report = distill_setup()
    copy_license()
    step("LICENSE → plugins/fiber/reference/matt/")
    ex_copied = copy_extra(TMP)
    if ex_copied:
        step(f"extra skills → {', '.join(ex_copied)}")
    rm_oy, rm_dirs = clean_agents()
    if rm_oy:
        step(f"清理 agents/openai.yaml：{len(rm_oy)} skill（{', '.join(rm_oy)}）；删空 agents/：{len(rm_dirs)}")
    write_meta(commit, version, len(names), current, ex_current)
    step("DISTILL.meta.json 已写")

    print("\n=== GLOBAL 路径替换（非-setup skill）===")
    for path, hits in global_report.items():
        print(f"\n[{path}]")
        for old, new, n in hits:
            print(f"  ✓ ({n}x) {old!r} → {new!r}")

    print("\n=== SETUP 精细替换（setup-matt-pocock-skills）===")
    for fname, hits in setup_report.items():
        miss = [h for h in hits if h[2] == 0]
        flag = " ⚠ 有未命中" if miss else " ✓"
        print(f"\n[{fname}]{flag}")
        for old, new, n in hits:
            mark = "✓" if n else "✗"
            print(f"  {mark} ({n}x) {old!r} → {new!r}")

    print(f"\n✅ 完成：{len(names)} skills + {len(ex_copied)} extra，commit {commit[:8]}")
    if changes or ex_changes:
        sys.exit(2)


if __name__ == "__main__":
    main()
