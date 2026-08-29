# Survey contract — subagent briefs for drafting

When a draft targets more than one area, the cartographer (the session running
the drafting skill) fans out survey subagents — one per area, 1–4 total. This
file is the brief each subagent gets, and the shape they must return. The merge
owns IDs; subagents never assign `#no.N`.

## How many, and where to cut

The count is derived, not guessed:

1. **Areas first — the count falls out.** An area is a coherent story on the
   domain axis ("how the system boots its kernel", "how behaviour gets
   customized"), briefable in one sentence. Cut where coupling is physically
   lowest — a spawn boundary, a socket, a protocol; never through shared
   modules or flows two areas would both need to tell.
2. **Arithmetic floor.** agents ≥ ceil(campaign scale ÷ per-agent cap). A
   ~30-block campaign at ≤16 blocks per agent needs ≥2 — one agent either
   blows the cap or goes shallow.
3. **The cost side counts too.** Every extra agent adds one merge seam
   (overlaps to dedup, keys to alias). Prefer the fewest count whose caps fit;
   the interaction rule catches whatever a boundary cuts through.
4. **Escalate on evidence only.** A story that cannot be briefed in one
   sentence is two stories; a codebase where 2×cap cannot cover the scale
   needs more agents, not shallower blocks.

## Brief skeleton

Each subagent prompt carries four parts:

1. **Scope + story** — the concrete paths/dirs AND the one-sentence story of the
   area ("how this system boots and spawns its kernel"). A story makes regions
   cohere; a file list alone produces inventory.
2. **Evidence rule** — read the real code; every claim needs `file:line` from a
   file opened this session. Unverifiable judgments get flagged
   (`?` unverified · `!` contradiction · `△` fragile) instead of padded.
3. **Interaction rule** — when the area touches blocks outside it, record those
   dependency edges too, addressed by best-known `path#Name`. The merge
   resolves them.
4. **Return contract** — the JSON below, as the final message. No prose around
   it, no markdown fences.

## Return contract

```json
{
  "area": "…",
  "regions": [{"name": "…", "role": "one english phrase like 'system · boot'", "why": "…"}],
  "blocks": [{
    "key": "src/cli.ts#CLI facade",
    "layer": "parent|domain|kernel|extension|channel — or the project's own stratum word",
    "name": "…", "duty": "one line",
    "know": "…", "unknow": "…",
    "data": "types/payloads in transit",
    "ports": "events/sockets/commands it plugs into",
    "note": "a judgment worth remembering", "flag": "? | ! | △ (omit when clean)",
    "files": ["src/cli.ts:10-31"],
    "children": [{"name": "…", "duty": "…", "files": ["…"]}],
    "region": 0
  }],
  "flows": [{"n": "chain name", "steps": ["key", "key"], "why": "what this backbone carries"}],
  "deps": [{"a": "key", "b": "key", "tag": "call|data|reg|order|infer", "note": "optional"}]
}
```

## Rules the brief must state

| Rule | Why |
|---|---|
| ≤16 blocks per agent; depth over breadth | campaign maps total ~30; agents over-cut when uncapped |
| blocks keyed `path.ext#Short name`, never numbered | IDs are assigned once, at the merge — two agents numbering in parallel is a collision factory |
| content language = the project's working language | the map mirrors the project |
| `know`/`unknow` only on load-bearing blocks | knowledge boundaries are the point, not decoration |
| every block carries ≥1 verified `file:line` | the map's trust model rests on citations |
| deps tagged `call`/`data`/`reg`/`order`/`infer` | provenance decides blast radius |
| flows 2–4, real execution order, only edges that exist in code | behaviour backbones, not wished-for structure |
| regions on the domain axis, never the file tree | the tree axis is the map's founding failure mode |
| children only for REAL inner semantics, ≤3 | drill is semantic decomposition, not nesting |
| plain text only — no HTML entities (`&amp;` `&lt;` `&gt;`) | entities render literally in the map |

## Merge responsibilities (cartographer, not subagents)

- resolve cross-agent keys through aliases; dedup blocks two areas both claim — and **graft** the dropped duplicate's unique findings onto the kept block before discarding it;
- create canonical blocks for recurring outside references (the kernel itself, third-party runtimes): subagents record interactions by `path#Name`, the merge decides which externals become real blocks — a spawn target that is not a block leaves the boot chain dangling;
- assign `#no.N` in region → block order, children numbered after their host;
- map the surveyed strata onto ≤5 layer slots (`LAYER_DEFS`), dropping unused slots;
- audit ≈1 in 5 `file:line` claims against the code before emit;
- hand-place regions by wire affinity when affinity is known — regions that exchange many wires belong adjacent; auto-layout otherwise.
