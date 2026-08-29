---
name: drafting
description: Survey a codebase and draw it as a single-file interactive HTML campaign map — a disposable projection the human reads, walks, and argues with.
disable-model-invocation: true
---

# Drafting

Survey a codebase (or one region of it) and draw it as a **single-file interactive map** — a drafting table the human opens in a browser: cards with global `#no.N` IDs, port-to-port wires, named runtime chains, and a walk-state layer that keeps *what the map says* apart from *what the human has verified*.

The map is **not documentation and not a process step**. It is a lens for one campaign — takeover, region settle, or surgery — and it dies with that campaign. The human protagonist is the point: every gate stays theirs; this skill only puts the system where they can see it.

## Principles

| Principle | What it rules |
|-----------|---------------|
| **From-1 projection** | The codebase is truth. The map is read out of the code, never recalled from memory or inferred from a template. Every block carries `file:line` evidence. |
| **Session addressing** | `#no.N` IDs are how the human and AI sessions talk about the system ("walk #19 → #21", "drill into #22") — shared addressing that survives long conversations. |
| **Disposable** | The map serves one campaign, is never synced with code, and is discarded at campaign end. Redrawing is cheap; durable knowledge sinks into project docs (step 5), not into the map. |
| **Project vocabulary** | Chains, layers, and regions are declared by *this* survey. The canvas is domain-blind. Legends that look alike across projects mean template-filling, not reading — a defect, not consistency. |
| **Two datasets** | A surveyor's claim and a human-walked fact are different data. Claims carry flags (`?` unverified / `!` contradiction / `△` fragile); only the human's walk states (`○` unread / `◐` read / `●` walked / `◆` observed) upgrade them. |

## Scale

Pick the scope before surveying; a map answers the campaign it was drawn for.

| Scope | When | Shape |
|-------|------|-------|
| skeleton | the first vertical slice just closed | ≤10 blocks — prove the loop closes end to end. This is the map that catches "the system has no caller" at day 5 instead of day 30. |
| campaign | takeover, or a region just settled | ~30 blocks; past ~40, split by region rather than shrinking text |
| surgery | a change starts crossing boundaries | re-survey only the affected blocks and their seams |

## Process

### 1. Scope the campaign

Confirm with the user: the target (repo / region / module), and the question this map must answer — takeover orientation, region hand-off, or a planned surgery.

**Completion:** target and campaign question are both stated; the scope row above is chosen.

### 2. Survey the code

Read the code for real — directly for small targets, or by fanning out subagents per area for larger ones. Subagent briefs follow `reference/survey-contract.md`: each agent returns mergeable JSON keyed by `path#Name`, and never assigns `#no.N` — IDs are assigned once, at the merge. Derive from what the code does:

- **blocks** — one per unit of responsibility, with duty, knows/must-not-know boundaries, data in transit, ports, and `file:line` evidence;
- **flows** — 3–5 named runtime chains (boot, assembly, interception, prompt assembly — whatever *this* system's behaviour backbones are), each a sequence of real call edges;
- **deps** — static dependency edges, each tagged with provenance (`call` / `data` / `reg` / `order` / `infer`) — provenance decides blast radius, so type every grey wire;
- **regions** — domain containers on the domain/behavior axis, never the file tree.

Judgments worth remembering become `note` fields, flagged when unverified. Boundaries between worlds (spawn, sockets, plugin surfaces) are blocks too — the map loses its value where seams go missing.

When the campaign precedes the code (map drawn from design sessions, no code to read), evidence cites the spec or decision instead of `file:line` — and the map is redrawn from code at first slice close; from then on the code is the only truth.

**Completion:** every block has `file:line`; every flow traces real call paths; every dep carries a provenance tag; every claim without code proof carries a flag.

### 3. Emit the map

**Audit, then emit.** Spot-check a sample of the survey's `file:line` claims against the code (≈1 in 5) before anything is drawn — one wrong citation poisons the map's whole trust model. Then copy `canvas.html` (beside this skill) into the target project's `.fiber/drafting/` (create the directory on first emit) as `<slug>-map.html`, and replace the **DATA ZONE** — `META`, `LAYER_DEFS`, `DOMAIN_DEFS`, `FLOW_DEFS`, `DEPS` — with the survey; layer names and strata come from this project, not from the template's example. The machinery below the marker stays untouched. Map content language follows the project's working language.

The chrome palette is locked: `reference/tokens.css` is the sole color source, carried inline in the canvas `:root`. Region washes reuse the flow-hue families at low alpha — no new hues. To re-theme, change `reference/tokens.css` and `:root` together; never improvise colors per map.

**Behavior regression before hand-over.** A file that renders is not a file that works. Open the emitted map and drive it: drill a hub (children appear, host focuses), click empty canvas (focus releases), collapse (children and wires gone), and confirm zero console errors. A canvas that renders but throws on interaction is the failure mode the eye skips — one survey round shipped exactly this way.

When merging multiple surveyors, keep the merge decisions explicit — aliases, dedup with grafts, canonical external blocks — and hand-place regions by wire affinity when the auto-layout stretches wires across the map.

**Completion:** the file opens standalone in a browser; wires land on ports; the status bar reads honest (block/wire/chain counts, `drawn <date>`, `disposable`); the legend names this project's chains and strata.

### 4. Hand over the posture

Tell the user how the map pays off — it is walked, not admired:

- **First open:** lock each chain and read it end to end; interrogate hubs ("why does everything cross here?"), cross-domain wires ("designed boundary or convenience?"), and counterintuitive notes; jump to `file:line` and verify.
- **Walk states:** mark unread / read / walked / observed in the dossier — states persist in the browser (localStorage under `META.key`), and the status bar counts them.
- **Addressing:** point sessions at IDs, not at re-pasted context.

### 5. Distill at end of life

When the campaign closes, list the invariants worth permanence — boundary contracts, ordering semantics, load-bearing decisions — and write them into the project's durable docs. Then discard the map. Nothing in it is owed a sync; a stale map is deleted, never updated.

**Completion:** the durable docs name what survived; the map file is gone.

## Boundaries

- **Projection, not implementation.** Drafting writes the map file and nothing else — no destination code, no refactors "while we're in here".
- **Disposable artifact.** The map lives in `.fiber/drafting/` — a campaign's maps are a family (skeleton, campaign, surgery), kept together and apart from the durable `.fiber/docs/`. Never committed; the only durable output is the step-5 distillation.
- **The canvas is not the product.** Machinery under the DATA ZONE marker stays as shipped; per-project change happens in data, never in mechanism.
- **A claim is not a walk.** Surveyor judgments render as flagged notes; only the human's walk states upgrade them. Never mark a block walked on the user's behalf.
