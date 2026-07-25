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
        # file structure 块：产物根 / → .fiber/，src/（代码目录）移出平级不挪
        ("/\n├── CONTEXT.md\n├── docs/adr/\n│   ├── 0001-event-sourced-orders.md\n│   └── 0002-postgres-for-write-model.md\n└── src/",
         ".fiber/\n├── CONTEXT.md\n└── docs/adr/\n    ├── 0001-event-sourced-orders.md\n    └── 0002-postgres-for-write-model.md\nsrc/"),
        ("/\n├── CONTEXT-MAP.md\n├── docs/adr/                          ← system-wide decisions\n└── src/\n    ├── ordering/\n    │   ├── CONTEXT.md\n    │   └── docs/adr/                  ← context-specific decisions\n    └── billing/\n        ├── CONTEXT.md\n        └── docs/adr/",
         ".fiber/\n├── CONTEXT-MAP.md\n└── docs/adr/                          ← system-wide decisions\nsrc/\n├── ordering/\n│   ├── CONTEXT.md\n│   └── docs/adr/                  ← context-specific decisions\n└── billing/\n    ├── CONTEXT.md\n    └── docs/adr/"),
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


def apply_global():
    """对所有非-setup skill 的所有 .md 应用全局路径前缀替换。"""
    report = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name == SETUP_NAME:
            continue
        for md in sorted(skill_dir.rglob("*.md")):
            text = md.read_text()
            orig = text
            hits = []
            for old, new in GLOBAL_REPLACEMENTS:
                n = text.count(old)
                if n:
                    text = text.replace(old, new)
                    hits.append((old, new, n))
            text = SRC_FIX.sub(r"\1/\2", text)  # 还原 src/<context>/ 下误伤
            if text != orig:
                md.write_text(text)
                report[f"{skill_dir.name}/{md.relative_to(skill_dir)}"] = hits
    return report


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
        text = f.read_text()
        hits = []
        for old, new in pairs:
            n = text.count(old)
            if n:
                text = text.replace(old, new)
            hits.append((old, new, n))
        f.write_text(text)
        report[fname] = hits
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


def main():
    step("蒸馏开始")
    commit = clone()
    skills, version = read_skill_list()
    step(f"matt version={version} commit={commit[:8]} skills={len(skills)}")

    # 蒸馏前检查：bucket 存在 + skill 增删 + 内容变更 + extra skills
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
        print("\n❌ 终止蒸馏（bucket 或 extra skill 缺失）")
        for e in list(errors) + list(ex_errors):
            print(f"  ERROR: {e}")
        sys.exit(1)

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
