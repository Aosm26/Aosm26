#!/usr/bin/env python3
"""
generate_headers.py
Generates minimalist SVG section headers with lowercase monospace typography
and hairline rules extending to the edge.
"""

import html
import os
from pathlib import Path

HEADERS = [
    ("about", "about"),
    ("focus", "focus & interests"),
    ("projects", "selected projects"),
    ("stack", "tech & tools"),
    ("stats", "activity & metrics"),
    ("connect", "connect"),
]

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 26" width="800" height="26">
  <style>
    .label {{
      font-family: "JetBrains Mono", "SF Mono", "Consolas", "Courier New", monospace;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.08em;
      fill: #58a6ff;
    }}
    .prefix {{
      fill: #8b949e;
      font-weight: 400;
    }}
    .line {{
      stroke: #30363d;
      stroke-width: 1;
      stroke-dasharray: 4 2;
    }}
  </style>
  <text x="0" y="17" class="label"><tspan class="prefix"># </tspan>{text}</text>
  <line x1="{line_start}" y1="13" x2="800" y2="13" class="line" />
</svg>
"""


def estimate_width(text: str) -> int:
    # "# " (2 chars) + text length; approx 8.2px per character at 13px mono
    full_text = f"# {text}"
    return int(len(full_text) * 8.6) + 16


def main():
    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    for key, label in HEADERS:
        line_start = estimate_width(label)
        escaped_label = html.escape(label)
        svg_content = SVG_TEMPLATE.format(text=escaped_label, line_start=line_start)
        target_file = out_dir / f"hd-{key}.svg"
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(svg_content.strip() + "\n")
        print(f"Generated: {target_file}")


if __name__ == "__main__":
    main()
