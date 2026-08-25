# GitHub Profile Architecture & Self-Generation Guide

> Reference architecture and implementation details for a self-generating GitHub profile using scheduled repository actions, custom SVG vector graphics, and zero third-party dependencies.
> 
> *Based on the minimalist design principles by Andrii Drok (`github.com/andriidrok1`).*

---

## Why Self-Generated Graphics?

Most profile READMEs pull graphics from external services (e.g. `github-readme-stats`, streak counters, activity charts). Two major problems arise:

1. **Third-Party Fragility:** External services often experience 503 outages, rate-limiting (`ERROR: Cards are temporarily rate limited`), or service disruptions.
2. **Design Cohesion:** Third-party widgets force pre-made themes, making the profile feel fragmented rather than unified.

> [!NOTE]
> All SVG assets are generated directly inside the repository via GitHub Actions using Python's standard library. Zero external API keys, zero rate-limiting risks, and zero tracking dependencies.

---

## GitHub Markdown Constraints & Capabilities

Tested by posting markdown directly to GitHub's rendering API (`POST /markdown`):

```text
STRIPPED
  <style> blocks        style="..." attributes      class="..."
  inline <svg>          <font>   <small>   <big>

KEPT
  <sub>  <sup>  <kbd>  <samp>  <blockquote>  <details>  <hr>  <picture>
  align="..."   width="..." on <img> and <td>
```

### Key Takeaways
1. **Typography Limits:** You cannot change README fonts using CSS or `<font>` tags. Monospace styling is achieved via `<code>` or `<samp>` tags.
2. **Animation Medium:** Embedded JavaScript is stripped; dynamic motion must live inside standalone SVG files using **SMIL** (`<animate>`, `<set>`).
3. **Custom Headers:** Custom brand typography for section headings must be rendered as SVGs.

---

## Part 1 — The Typing ASCII Portrait Pipeline

*(Optional / Reference component)*

### Photo Capture & Lighting
- **Side Light:** Light source at ~45° to provide strong facial shadow contours.
- **Tight Framing:** Chin to top of hair.
- **High Resolution:** 1200px+ crop to retain facial structure upon downsampling.

### Processing Pipeline
| Stage | Purpose |
| :--- | :--- |
| `rembg` cut-out | Forces background to pure white (mapped to empty character in ramp). |
| Bilateral filter | Smooths skin tones while preserving sharp boundary edges. |
| CLAHE (clip ≈ 3.0) | Local adaptive contrast per tile. |
| Darkening Curve `(v/255)^1.7` | Preserves brow, glasses, and shadow definition. |
| Ramp Mapping | Maps brightness to 13-character monospace ramp: ` .:-=+*cs#%@` |

### Monospace Advance Width
- Standard advance width assumes **0.600 em** (`CHAR_W = 7.74` at `font-size: 12.9`).
- JetBrains Mono / DejaVu Sans Mono / Noto Sans Mono match 0.600 ✅.

---

## Part 2 — Self-Drawn Stats Engine

Four custom SVG graphics drawn via the GitHub GraphQL API:
- `stats.svg`: Total contributions + 52-week sparkline column graph.
- `streak.svg`: Current and longest streaks with active date windows.
- `langs.svg`: Top repository languages by byte volume and percentage.
- `year.svg`: Full 365-day ASCII ramp contribution matrix.

### Determinism Rules
1. **Fixed UTC Window:** `from` = today − 364 days at `00:00:00Z`, and `to` = today at `23:59:59Z`.
2. **Public Filtering:** Always filter `privacy: PUBLIC` so CI tokens produce identical results to local runs.

### GitHub Actions Automation
```yaml
name: refresh stats
on:
  schedule:
    - cron: "17 5 * * *"
  workflow_dispatch:
permissions:
  contents: write
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate Assets
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GH_LOGIN: ${{ github.repository_owner }}
        run: |
          python scripts/generate_headers.py
          python scripts/generate_stats.py
      - name: Commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add assets/
          git diff --staged --quiet || (git commit -m "stats: refresh graphics [skip ci]" && git push)
```

---

## Part 3 — Typography & Markdown Design

- **SVG Section Headers:** Lowercase monospace text paired with an understated hairline rule (`#30363d`).
- **`<samp>` Tag:** Preferred over backticks for a clean monospace stack without distracting gray boxes.
- **`<blockquote>` Lede:** Provides an elegant left accent border for summary introductions.

---

## Part 4 — Font Subsetting & Inlining

For completely independent SVG rendering across all operating systems without external font fetching:
```bash
pip install fonttools brotli

# Subset only the 13 ramp characters
pyftsubset JetBrainsMono-Regular.ttf --text=' .:-=+*cs#%@' \
  --flavor=woff2 --layout-features='' --no-hinting -o ramp.woff2
```

| Subset | Covers | Size |
| :--- | :--- | :--- |
| ramp | 13 characters | ~1.3 KB |
| headings | used letters | ~1.4 KB |
| basic latin (2 weights) | data graphics | ~4.5 KB each |
| **Total Inlined Footprint** | whole page | **~57 KB** |

---

## Gotchas & Best Practices

- **SMIL Headless Screenshotting:** Full-page screenshots can restart SMIL timers; use tall viewports when testing headlessly.
- **Avoid Per-Character Coloring:** Uniform monochromatic fills produce far clearer ASCII and data visualizations.
- **Cache Invalidation:** If a new profile README does not immediately show updates, edit once in the web UI to trigger GitHub cache purge.
