---
name: setup-ship
description: Scan a project's version files and generate a tailored project-level `ship` skill — commits delegate to `snap`, with automatic version bumps and an optional CHANGELOG / release flow. Run on init, update, or remove.
disable-model-invocation: true
---

# setup-ship

Scan a project's version files and generate a tailored project-level `ship` skill — the project's commit, version, and CHANGELOG automation. `ship` delegates every commit to `snap` and never invents its own commit flow.

Three duties, chosen from context: **init** (scan, configure, generate), **update** (reconfigure), **remove** (delete).

## Process

### 0. Decide intent

Pick init / update / remove from context. Ask the user when the intent is unclear.

Completion: one of the three duties is chosen before any file is read or written.

### 1. Init

#### 1.1 Scan the version files

Check each candidate for existence with `ls`, then read its version field. Priority order:

| File | Field path | How to read |
|------|------------|-------------|
| `package.json` | `.version` | `jq .version` or read JSON |
| `Cargo.toml` | `[package].version` | `grep '^version'` |
| `pyproject.toml` | `[project].version` | `grep 'version'` |
| `pubspec.yaml` | `version:` | `grep 'version:'` |
| `build.gradle(.kts)` | `version = "..."` | `grep 'version'` |
| `pom.xml` | `<version>` | `grep '<version>'` |
| `*.csproj` | `<Version>` | `find` + `grep` |
| `VERSION` | whole line | read |
| `version.txt` | whole line | read |

For every file found, record:

- `path` — relative to the project root
- `field_path` — the version field location
- `current_version` — the version string as stored
- `format` — `bare` (`1.0.0`) or `v-prefixed` (`v1.0.0`)

**Normalise two-segment versions** (`1.0` → `1.0.0`). When a two-segment version is found, tell the user and write the normalised form back to the file.

**No version file detected:** ask the user for the file path and field name.

Completion: every version file in the project is on the list with path, field, version, and format — or the user has supplied them by hand.

#### 1.2 Ask the two config questions

Two AskUserQuestion calls.

**Q1 — CHANGELOG**

| Option | Meaning |
|--------|---------|
| Enable | update `CHANGELOG.html` on every commit |
| Disable | no CHANGELOG |

**Q2 — Release flow**

| Option | Meaning |
|--------|---------|
| Enable | on version release, auto-create PR, merge, and tag (forces CHANGELOG on) |
| Disable | no automated release flow |

Enabling the release flow **forces CHANGELOG on**, overriding Q1.

Completion: both answers are recorded; if the release flow is on, CHANGELOG is on too.

#### 1.3 Generate the `ship` skill

1. Read [ship-template.md](reference/ship-template.md).
2. Substitute the placeholders:

| Placeholder | Replace with |
|-------------|--------------|
| `{{VERSION_FILES_TABLE}}` | one table row per file: `\| <path> \| <field_path> \| <format> \|` |
| `{{ENABLE_CHANGELOG}}` | `enabled` or `disabled` |
| `{{ENABLE_RELEASE}}` | `enabled` or `disabled` |

3. Write to `<project>/.claude/skills/ship/SKILL.md` — the substituted template, verbatim. `mkdir -p` the directory first.

Completion: `.claude/skills/ship/SKILL.md` exists with every placeholder substituted and no template marker left behind.

#### 1.4 Confirm

```
✅ ship skill generated

Version files:
- <path> (<field_path>): <version> [<format>]

Config:
- CHANGELOG: ✅ enabled / ❌ disabled
- release flow: ✅ enabled / ❌ disabled

Run /ship to commit + bump. Commits delegate to /snap.
```

Completion: the summary lists every version file, both config flags, and how to invoke `ship`.

### 2. Update

Trigger: version files changed, or a feature flag toggled.

1. Read `.claude/skills/ship/SKILL.md`.
2. Ask which item to update.
3. Re-scan (version files) or toggle a flag.
4. Regenerate `.claude/skills/ship/SKILL.md` from the template.
5. Print a diff of what changed.

Completion: the regenerated skill reflects the new config; the user sees the delta.

### 3. Remove

1. Confirm `.claude/skills/ship/` exists.
2. Ask the user to confirm the removal.
3. Delete `.claude/skills/ship/`.
4. Print a removal confirmation.

Completion: `.claude/skills/ship/` no longer exists; the user has confirmed the deletion.

## Out of scope

- **Executing commits or version bumps** — `setup-ship` only generates / updates / removes the `ship` skill. Running commits and bumps is the generated `ship`'s job, not this skill's.
- **`plugin.json` / `marketplace.json` sync** — that is project-level plugin versioning (in this repo, `/b3oy1-manage-version`). `setup-ship` serves any project's version files, not plugin packaging — the #27 split.
- **Cursor / Codex deployment** — `ship` lands at `.claude/skills/ship/` only. spin is permanently Claude Code-only — #31.

## Reference

- [ship-template.md](reference/ship-template.md) — the template the generated `ship` skill is built from.
