# MYSTERY DECK — 500 sealed web-app ideas

One self-contained `index.html` (≈233 KB). No build step, no dependencies, no CDN, no network calls —
all 500 ideas, all CSS, all JS and even the favicon are inlined in the single file.

## Host it on GitHub Pages (2 minutes)

**Option A — drag & drop in the browser**

1. Create a new repository (e.g. `mystery-deck`), public.
2. Upload `index.html` to the **root** of the repo (Add file → Upload files).
3. Repo **Settings → Pages → Source: Deploy from a branch** → branch `main`, folder `/ (root)` → Save.
4. Your deck is live at `https://<your-username>.github.io/mystery-deck/`.

**Option B — command line**

```bash
mkdir mystery-deck && cd mystery-deck
cp /path/to/index.html .
git init && git add index.html && git commit -m "mystery deck"
git branch -M main
git remote add origin https://github.com/<your-username>/mystery-deck.git
git push -u origin main
# then enable Settings → Pages → main / root
```

It also works straight off your disk: just double-click `index.html`.

## What's in it

| Thing | Detail |
|---|---|
| Cards | 500 unique web-app ideas, each sealed until you break it |
| Rarity tiers | Common · Uncommon · Rare · Epic · Legendary (Legendary = gold foil, screen flash + shake) |
| Categories | 14 (AI & Copilots, Dev Tools, Food & Drink, Outdoors, …) |
| Per card | title, one-line pitch, 4 tech tags, difficulty 1–5, MVP build time, "spark score" |
| Filters | live search, category chips, rarity chips, difficulty, seal state, 6 sort modes |
| Progress | unsealed count is saved in `localStorage`, so the deck remembers you |

## Effects

- Boot sequence, glitch/chromatic-aberration title, scrolling HUD ticker
- Live particle constellation canvas + neon perspective floor + drifting orbs + scanlines + film grain
- Cursor glow, per-card 3D tilt, pointer-tracking spotlight, border beam, holo shine sweep
- 3D card flip → text **decrypt/scramble** reveal, shockwave, spark particle burst
- Optional WebAudio synth blips (no audio files — generated live), pitch follows rarity

## Keyboard

`/` search · `R` deal a random card · `U` unseal all · `S` sound · `Esc` close

## Re-generating or editing the ideas

`.nojekyll` is included (empty file) — it tells Pages to skip Jekyll processing, so the site deploys
as plain static files and nothing can rewrite your paths.

```
gen.py     idea engine (subjects × mechanics × audiences) → ideas.json
src/       style.css · body.html · app.js
build.py   inlines everything → index.html
test.js    jsdom smoke test (50 assertions: render, reveal, filters, storage)
```

```bash
python3 gen.py && python3 build.py && node test.js
```

Prefer to hand-edit ideas? Change them directly in `ideas.json` (fields: `t` title, `b` blurb,
`c` category, `d` difficulty 1–5, `tags`, `r` rarity, `w` MVP time, `spark` 0–100, `n` number,
`id`) then run `python3 build.py`.

`prefers-reduced-motion` is respected: particles, boot, glitch, shake and scramble all stand down.
