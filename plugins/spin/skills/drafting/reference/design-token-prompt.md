# Design Token Prompt — Drafting Table

A **token-locked** prompt for image / UI generation models: palette, type, and
geometry pinned — the model may compose, never invent colors. `tokens.css`
(beside this file) is the sole color source on the code side.

## Token table

| Token | Value (OKLCH / hex approx) | Role |
|---|---|---|
| `--paper` | oklch(95.5% .028 95) / `#F5F0E1` | canvas ground, cream vellum |
| `--paper-2` | oklch(92.5% .032 93) / `#EFE9D6` | inputs, legend, secondary face |
| `--panel` | oklch(98% .014 95) / `#FBF8EE` | card surface |
| `--ink` | oklch(27% .025 80) / `#2E2921` | primary text, key strokes |
| `--ink-2` | oklch(47% .03 85) / `#6E6455` | secondary text, dependency wires |
| `--hair` | oklch(83% .03 90) / `#D6CDB8` | hairlines |
| `--grid` | oklch(90.5% .025 95) / `#E9E2CF` | millimeter grid |
| `--accent` | oklch(47% .13 255) / `#3D5CA8` | sole UI accent |
| `--f0`–`--f3` | blue `#3D5CA8` · green `#44743E` · amber `#CE8A33` · violet `#6F5AA5` | the four flow-chain colors |

Hex values are eyeball approximations of the OKLCH; OKLCH is canonical.
Type: serif = brand title only · mono = all instrument chrome · sans = body.
Geometry: radii 3/5px, hairline 1px strokes, no heavy outlines.

## Image prompt (token-locked)

```
A high-fidelity straight-on screenshot of an infinite zoomable architecture-map
tool on a drafting table, drawn in ink on cream vellum paper (#F5F0E1) with a
fine millimeter grid (#E9E2CF). STRICT PALETTE, no other colors: ink #2E2921,
secondary ink #6E6455, hairlines #D6CDB8, card surfaces #FBF8EE, one UI accent
blue #3D5CA8, and exactly four muted flow colors — blue #3D5CA8, green #44743E,
amber #CE8A33, violet #6F5AA5. No neon, no gradients, no glassmorphism, no 3D.

Node cards: small rectangles (#FBF8EE, 1px hairline border, 5px radius) with a
colored title strip, a global ID like "#no.12" in small monospace, one line of
duty text. Translucent tinted region containers group cards into domains, their
labels written IN the region color like drawing annotations, e.g. "STARTUP CHAIN
(system · boot)". One tall hub card contains a CONNECTIONS list: rows prefixed
"in #no.03 / out #no.17", bezier wires converging on its edge ports, one wire
per row.

Wires: smooth bezier curves between tiny circular ports — hollow port = source,
filled port = target. Colored flow chains thread the map with small arrowheads;
faint dashed grey dependency lines (#6E6455, 55% opacity) run beneath them.

Chrome, all monospace, like a measuring instrument: serif brand title "DRAFTING
TABLE" top-left with subtitle "SINGLE-FILE CAMPAIGN MAP", search field, shortcut
hints "[L] Legend [F] Find", a right dossier panel styled as a spec sheet with
section headers DUTY / KNOWS / MUST-NOT-KNOW / DEPENDENCY / EVIDENCE, small
rotated approval stamps on card corners (○ unread ◐ read ● walked ◆ observed),
and a bottom status strip "31 BLOCKS · 29 WIRES · 3 CHAINS · WALKED 0/32 ·
DRAWN 2026-08-29 · DISPOSABLE". Generous negative space, hairline strokes,
crisp small text, 16:10.
```

## Usage rules

1. Every color/type reference cites a token name — inventing values mid-render is
   forbidden; this file and `tokens.css` are the single truth for model and code.
2. Image-model output is compared on **object-feel only** (paper, ink, mono,
   annotation style) — never used as interaction or information-architecture spec.
3. A render introducing off-palette colors is a re-roll, not a touch-up.
