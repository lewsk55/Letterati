# Letterati build tools

Working tools for changing and testing Letterati. The live game is `index.html` at the repo root (served by GitHub Pages). Every change ships as a **new version**; versions are never overwritten.

## Setup (once per machine or chat workspace)

```bash
git clone https://github.com/lewsk55/Letterati.git && cd Letterati
npm i playwright            # tests drive headless Chromium
python3 -m http.server 8765 # serve the repo root; leave running (tests hit localhost:8765)
```

## How a version gets built

Each version is a Python patch script that turns the previous build into the next one with exact text replacements. Every `rep(a, b, n)` asserts its match count, so a patch fails loudly instead of silently missing.

```bash
python3 tools/patches/patch_051q.py index.html letterati_v0.51q.html
```

- `tools/patches/` holds every patch from 0.51a (`patch_letterati.py`) to 0.51p, in order. Read the newest one or two to see the conventions.
- Start each new patch by bumping both `gameVersion:"0.51x"` and `const VERSION`.
- Keep a dated `// v0.51x:` comment on each change.
- Player-facing text and code comments: no em dashes, no AI-tell wording.

## Checks to run before shipping

| Check | Command | Must show |
|---|---|---|
| Daily seeds unchanged | `node tools/checks/seeds_check.js letterati_v0.51q.html` | `30/30 dates identical` |
| Play screen layout | `node tools/checks/layout_check.js letterati_v0.51q.html` | exit 0: no scroll, bank at most 2 rows, canvas in bounds, 0 moves while tapping |
| Perk inventory | `node tools/checks/count_perks.js letterati_v0.51q.html` | lists general and character perks |
| Balance sim | `CHAR=writer OUT=res.json node tools/sim/runner_char.js 45 regular 0 letterati_v0.51q.html 7 3` then `python3 tools/sim/summ.py` (expects `res_<name>.json`) | win rate and challenge clear rate (45 runs is about ±7%) |

**Daily seed rule:** the predictor (`predictSeed`, `predShop`, `predRoll`, `anaSetPred`) is pinned to v0.5h so every player gets the same daily press. A live-play change that touches word validity, shop rolls or targets must leave those functions alone, or use separate live-only constants or rng keys. `seed_baseline.json` was recorded from v0.5h. Only re-record it (`--write`) if the daily is deliberately being re-seeded.

**Sim notes:**
- `sim v2.html` at the repo root is the sim agent; `runner_char.js` loads it from the local server.
- Characters: `writer`, `detective`, `shortking`, `scholar`, `editor`, or `mix`.
- Same seed and parallel settings (seed 7, parallel 3) give comparable runs across builds.

## Shipping

1. Build and check as above.
2. `cp letterati_v0.51q.html index.html`, commit, push. Pages updates in about 1 to 2 minutes; confirm with `curl -s https://lewsk55.github.io/Letterati/ | grep -o 'VERSION *= *"[^"]*"'`.
3. Keep the versioned file too (Adam's Mac folder holds every version).
4. Update the project doc for the version.

Push live automatically once a build passes the checks (Adam's standing rule since Oct 20, 2026). No need to wait for his ok.
