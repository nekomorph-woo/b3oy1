# Core-first: find the core, then let it rule

For a from-zero project, the dominant risk is not building the wrong features — it is freezing the wrong invariants. This rule shapes how `wayfinder` / `grilling` / `domain-modeling` sessions explore a domain: **discover the core first, let everything else be ruled variation on it.** In an existing system it shapes the entry check instead: read the core, route the need, then touch code.

## The three layers

| Layer | What it is | Contains |
|-------|------------|----------|
| **core** | The rule subject — the domain's core flows, concepts, and data structures. Knows the domain's process semantics; never knows concrete vocabulary or customers. | flows, invariants, core data structures |
| **core-extension** | The wall between the core and every surface — contracts plus domain-blind glue. | contracts, extension points, registries / routers / composers |
| **business surface** | The implementers — everything that fills the extension points: presentation ends and execution ends. Knows vocabulary and implementations; legislates nothing. | implementations, pages, bindings |

core + core-extension form the **one core rule domain**. The layers are not three parallel boxes — they derive from the core:

- **extension ≡ the minimal boundary conditions of the core's completeness.** Every invariant that closes across the wall (a key written at configuration time ↔ the same key read at execution time) must have its cross-wall shape declared here. Test: tear the declaration away — which core invariant breaks first? None → it does not belong on the wall. Completeness is *minimal-necessary*, never a union of everything related.
- **surface ≡ all freedom beyond the boundary.** The default home; it needs no justification.

The core does not know its customers — customers reach it only through the seams the extension declares, which is what lets the core's capability serve needs it never anticipated. Dependencies point inward: the surface consumes the rules, never the reverse.

## What may live on the wall

The wall holds two kinds of sockets:

| Socket kind | Who calls it | Who depends on it |
|-------------|--------------|-------------------|
| **delegation sockets** | the core, inside its pipeline | the core's runtime — executor contracts, store contracts |
| **supply sockets** | a surface, usually at configuration time | **the core's loop** — skipped or malformed, the pipeline starves or breaks: trigger binding, compose / validate outlets |

Two rules keep the wall clean:

- **Code on the wall must be domain-blind.** Registries, dispatchers, composers may carry code — if you could move a piece unchanged to an unrelated domain, it belongs here; the moment it holds a business judgment, it demotes to the surface.
- **Mechanisms stay in the core; vocabulary grows on the wall.** Identifier syntax, parsing, registry routing: core. Which identifiers exist: declared by implementers at registration — never enumerated in the core, never in a hand-maintained catalog. A catalog is a **projection of the registry**; a hand-written id list is a second source of truth and will drift.

## Two guardrails

- **Everything flows back.** A surface may keep private structures, but every exchange with the core crosses an extension contract and lands in core data structures.
- **Nothing seeps up.** Implementation shared between businesses stays in the surface until it must bind **all** businesses — only then is it promoted to an extension contract, and the promotion is a decision (ADR), never a silent refactor.

## Core is discovered, not designed

At from-zero, the fog sits exactly on "what is the core" — deciding it up front freezes the most error-prone judgment at the highest cost to change. The order runs the other way:

1. **Triangulate.** Explore 2–3 maximally different business scenarios (`research` / `prototype` tickets). One scenario proves nothing; the core lives at the intersection of several.
2. **Anchor a working hypothesis.** Keep a "core, current version" passage in the map's Decisions (or `CONTEXT.md`'s domain model) — the concepts, the rules, and which scenarios have validated them. Every research/prototype return either shakes it or steadies it; revise the passage, don't scatter it across ticket comments.
3. **Accept revision as the norm.** An early core that keeps moving is not failure — it is the discovery process working. The anchor exists so the movement is visible and versioned.

## When the core counts as settled

Two criteria, both required — this is what terminates the grilling instead of endless rounds:

- **Closure.** The whole core rule set states in one paragraph — no trailing "etc.".
- **Load-bearing.** At least two substantially different business scenarios replay **on the core** without modifying it — additions land as new extension points or surface implementations only.

Settled → collapse a core-volume spec. From there, business needs are usually fogless: route them **straight to `to-spec`** — wayfinder retires to on-call, returning only on a core-shaking signal.

## Working in an existing system

**Core already chartered.** Open the session by reading the core anchor — the "core, current version" passage in the map's Decisions or `CONTEXT.md` — then route the need through the decision tree below **before** touching code. In existing-system work the decision tree, not the discovery flow, is the daily instrument.

**Legacy system, no core chartered.** The most common reality: rules and implementations fused in sediment. Here core-first degrades gracefully into *extract-first*: mine the core hypothesis from existing code and its bug-fix history, anchor it as the working hypothesis above, and let new work land on the extracted core. Migrate rule-bearing legacy code ticket by ticket (strangler style) — never a big-bang rewrite in the name of the core.

## When a need challenges the settled core

Decision tree, cheapest first:

1. **An existing extension point already supports it** → ordinary surface work, no design session needed.
2. **The core is intact but lacks a hook** → add the extension point / contract in core-extension (route through a decision, not through silent code); the business fills the implementation on the surface.
3. **The core itself is shaken** → the expensive one: return to `wayfinder`, revise from the bottom up, and treat every already-built piece the change touches through change tickets — never silent rewrites.

## How this hooks into the batch fences

The settled core's semantics are the **deepest frozen layer**: batch reports reconcile against them first. Code in core / core-extension is the seam every business touches — it is the part a human reviews personally, while the surface is safe AFK territory.

## Out of scope

Throwaway-layer work (prototypes that answer a question, debug harnesses, data-gathering scripts) never enters this frame — it produces no destination, so it never owes the core an answer.
