#!/usr/bin/env python3
"""Assemble the single self-contained index.html (GitHub Pages ready)."""
import json, pathlib

root = pathlib.Path(__file__).parent
css   = (root / "src/style.css").read_text(encoding="utf-8")
body  = (root / "src/body.html").read_text(encoding="utf-8")
js    = (root / "src/app.js").read_text(encoding="utf-8")
data  = (root / "ideas.json").read_text(encoding="utf-8")

# keep the JSON script block safe no matter what the idea text contains
data = data.replace("</", "<\\/")

ideas = json.loads((root / "ideas.json").read_text(encoding="utf-8"))
n_leg = sum(1 for i in ideas if i["r"] == "Legendary")
n_cat = len({i["c"] for i in ideas})

FAVICON = ("data:image/svg+xml,"
  "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
  "%3Crect width='64' height='64' rx='12' fill='%2304070f'/%3E"
  "%3Cpolygon points='32,6 58,20 58,44 32,58 6,44 6,20' fill='none' stroke='%2325e8ff' stroke-width='2.5'/%3E"
  "%3Ctext x='32' y='43' font-family='monospace' font-size='30' font-weight='bold' "
  "text-anchor='middle' fill='%23ff2fb3'%3E%3F%3C/text%3E%3C/svg%3E")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>MYSTERY DECK — 500 Sealed Web-App Ideas</title>
<meta name="description" content="A neon deck of 500 sealed web-app idea cards. Hover to charge, click to break the seal, filter by category and rarity, deal a random concept. One HTML file, no dependencies.">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#03050c">
<meta property="og:type" content="website">
<meta property="og:title" content="MYSTERY DECK — 500 Sealed Web-App Ideas">
<meta property="og:description" content="{len(ideas)} sealed concept cards, {n_cat} categories, {n_leg} legendary pulls. Break the seal.">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{FAVICON}">
<style>
{css}
</style>
</head>
<body>
{body}
<noscript>
  <div style="position:fixed;inset:0;display:grid;place-items:center;background:#03050c;z-index:999;
              font-family:ui-monospace,monospace;color:#25e8ff;text-align:center;padding:24px;letter-spacing:.2em">
    JAVASCRIPT REQUIRED TO BREAK THE SEALS
  </div>
</noscript>
<script id="deck-data" type="application/json">{data}</script>
<script>
{js}
</script>
</body>
</html>
"""

out = root / "index.html"
out.write_text(html, encoding="utf-8")
kb = out.stat().st_size / 1024
print(f"wrote {out} — {kb:.0f} KB, {len(ideas)} cards, {n_cat} categories, {n_leg} legendary")
