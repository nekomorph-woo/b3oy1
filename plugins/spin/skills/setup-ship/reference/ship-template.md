---
name: ship
description: Project-level commit, version, and CHANGELOG automation. Commits delegate to `snap`; the version bumps on every commit and a release flow runs when asked.
disable-model-invocation: true
---

# ship

Project-level commit, version, and CHANGELOG automation. Every commit delegates to `snap` — `ship` never invents its own commit flow.

## Project config

### Version files

| File | Field path | Format |
|------|------------|--------|
{{VERSION_FILES_TABLE}}

### Feature flags

| Feature | State |
|---------|-------|
| CHANGELOG | {{ENABLE_CHANGELOG}} |
| release flow | {{ENABLE_RELEASE}} |

---

## Version rules

- Three-segment `x.y.z`; each segment is digits, no upper bound.
- **Normal commit:** z+1 (`0.1.0` → `0.1.1`).
- **Release — normal:** y+1, z resets (`0.5.30` → `0.6.0`).
- **Release — major:** x+1, y and z reset (`1.33.2` → `2.0.0`).
- When a version file carries a `v` prefix, keep it on write-back; strip it for CHANGELOG / PR / TAG (digits only).
- Version extraction regex: `(\d+\.\d+\.\d+)`.

---

## Mode

| Signal | Mode |
|--------|------|
| `/ship` with no release keyword | normal commit |
| user message says "release" / "version release" | release commit |

---

## Normal-commit flow

### 1. Read the staged diff

Run `git diff --cached --stat` and `git diff --cached`; analyse the change and its scope.

### 2. Decide whether to split

Split when the change spans several unrelated scopes. Keep one group when the scopes match or are tightly coupled.

### 3. Commit (delegate to snap)

For each group, delegate the commit to `/snap`. `ship` does not invent its own commit flow — every commit goes through `snap`.

To split: `git reset HEAD` to unstage, then `git add` each group and run `/snap` per group.

Collect from every commit: hash, timestamp (`git log -1 --format=%ai <hash>`), type, description.

### 4. Bump the version

Read every version file, extract the current version, add z+1, write it back preserving the file's original format (`v` prefix / quotes / indentation).

### 5. Maintain the CHANGELOG

**Only when the CHANGELOG flag is enabled.**

Append one entry per commit to `CHANGELOG.html`.

Entry format: `[MM-DDTHH:MM] <emoji> <product / project / feature-level description>`

Emoji map:

| commit type | emoji | meaning |
|-------------|-------|---------|
| `fix` | 🐛 | bug fix |
| `feat` | 🎁 | feature added / improved |
| other | 📄 | neither 🐛 nor 🎁 |

Update the current month's `<details>` block `<summary>`:

- with a release: `YYYY-MM: 🎉V<ver> - <desc>` (one fused description across the month's releases)
- without a release: `YYYY-MM: <one representative product-level summary>`

**Summary prompt:** from this month's changes, distil the single most central product-capability shift into one user-perceptible line. No code details.

### 6. Commit the version + CHANGELOG change

```
git add <version files> CHANGELOG.html
git commit -m "chore(<scope>): bump version to X.Y.Z"
```

### 7. Summarise

```
✅ committed
commits: <hash1>, <hash2>, ...
version: X.Y.Z → X.Y.Z+1
CHANGELOG: ✅ updated (if enabled)
📤 to push: <N> commits ahead of origin
```

---

## Release flow

**Only when the user explicitly asks for a release, and the release-flow flag is enabled.**

### 1. Finish pending commits

If anything is staged, run the normal-commit flow first.

### 2. Ask the release type

| Option | Meaning |
|--------|---------|
| normal release | y+1, z resets (e.g. `0.5.30` → `0.6.0`) |
| major release | x+1, y and z reset (e.g. `1.33.2` → `2.0.0`) |

### 3. Compute and write the version

Read the current version → compute the new one per the release type → write it to every version file.

### 4. Maintain the CHANGELOG

**With the release flow on, the CHANGELOG is mandatory.**

Add the release entry: `🎉V<version> - [MM-DDTHH:MM] <emoji> <product-level description>`

Update the `<summary>` to the release format.

### 5. Commit the release change

```
git add <version files> CHANGELOG.html
git commit -m "release(<scope>): V<version> - <description>"
```

### 6. Open the PR

Gather every CHANGELOG entry since the last release and restate them at the product level.

```bash
gh pr create --title "🎉V<version> - <product-level title>" --body "<bullet list>"
```

Platform check: `git remote get-url origin` containing `github.com` → `gh`; `gitlab.com` → `glab`.

### 7. Merge the PR and clean up

```bash
gh pr merge <pr-number>
git push origin --delete <branch>    # delete the remote branch
git branch -d <branch>               # delete the local branch
```

### 8. Tag

```bash
git tag V<version>-<kebab-case feature summary>
```

### 9. Summarise the release

```
✅ release done
version: X.Y.Z → X+1.0.0
PR: #<number> merged
TAG: V<version>-<description>
📤 to push: <N> commits + <N> tags ahead of origin
```

---

## CHANGELOG.html format

Months in natural order (old → new), one `<details>` block per month, so appends stay cheap.

```html
<details>
<summary>2026-05: code-quality and performance pass</summary>

[05-15T14:30] 🐛 fix data-export encoding error
[05-20T10:00] 📄 restructure project layout
[05-28T16:00] 🎁 add custom dashboard layouts

</details>

<details>
<summary>2026-06: 🎉V1.2.0 - user-management upgrade</summary>

[06-05T09:00] 🐛 fix login Safari compat
[06-07T10:15] 📄 tighten build config
🎉V1.2.0 - [06-07T14:30] 🎁 user-management overhaul, adds export and bulk ops

</details>
```

**Write strategy:** rebuild the file in full every time, never append incrementally.

**Timestamp source:** `git log -1 --format=%ai <hash>` (the commit author date).

**Description constraint:** summarise at the product / project / feature level. **DO NOT** record code or doc detail.

---

## Version string in CHANGELOG / PR

Extraction and write-back live in [Version rules](#version-rules); this section fixes only how a version is *rendered* in CHANGELOG / PR / TAG.

- CHANGELOG / PR title / TAG use the `V1.2.3` form (capital V + digits) throughout.
- **DO NOT** produce a double prefix like `Vv1.0.0`.
