# CLAUDE.md

工程类 skill 的 per-repo 配置入口。三项配置落在 `.fiber/docs/agents/`，
由 `/setup-matt-pocock-skills` 生成。

## Agent skills

### Issue tracker

Issues 走本仓库的 GitHub Issues（用 `gh` CLI）。见 `.fiber/docs/agents/issue-tracker.md`。

### Domain docs

Single-context：`.fiber/` 下一份 `CONTEXT.md` + `docs/adr/`。见 `.fiber/docs/agents/domain.md`。
