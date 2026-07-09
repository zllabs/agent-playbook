"""Generate SVG charts for contract test coverage and example categories."""

from __future__ import annotations

import math
from pathlib import Path

from tests.validate_brief import parse_examples_markdown

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
EXAMPLES = (ROOT / "examples.md").read_text()

# 16 contract tests grouped by what they validate
CONTRACT_TEST_GROUPS = {
    "Structure compliance": 3,
    "Brief quality": 4,
    "Design behavior": 3,
    "Package integrity": 5,
    "Example coverage": 1,
}

COLORS = {
    "Structure compliance": "#4C78A8",
    "Brief quality": "#F58518",
    "Design behavior": "#54A24B",
    "Package integrity": "#E45756",
    "Example coverage": "#B279A2",
}

CATEGORY_COLORS = [
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#B279A2",
    "#72B7B2",
]


def _pie_chart(
    data: dict[str, int],
    colors: dict[str, str],
    title: str,
    width: int = 480,
    height: int = 320,
) -> str:
    total = sum(data.values())
    cx, cy, r = width * 0.35, height * 0.52, min(width, height) * 0.28
    start = -math.pi / 2
    slices: list[str] = []
    legend: list[str] = []

    for i, (label, value) in enumerate(data.items()):
        angle = (value / total) * 2 * math.pi
        end = start + angle
        x1 = cx + r * math.cos(start)
        y1 = cy + r * math.sin(start)
        x2 = cx + r * math.cos(end)
        y2 = cy + r * math.sin(end)
        large = 1 if angle > math.pi else 0
        color = colors.get(label, CATEGORY_COLORS[i % len(CATEGORY_COLORS)])
        slices.append(
            f'<path d="M{cx:.1f},{cy:.1f} L{x1:.1f},{y1:.1f} '
            f'A{r:.1f},{r:.1f} 0 {large} 1 {x2:.1f},{y2:.1f} Z" '
            f'fill="{color}" stroke="#fff" stroke-width="1.5"/>'
        )
        pct = value / total * 100
        legend.append(
            f'<rect x="{width * 0.62:.0f}" y="{48 + i * 28}" width="14" height="14" '
            f'fill="{color}" rx="2"/>'
            f'<text x="{width * 0.62 + 22:.0f}" y="{59 + i * 28}" '
            f'font-family="system-ui,sans-serif" font-size="13" fill="#333">'
            f"{label} ({value}, {pct:.0f}%)</text>"
        )
        start = end

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#fafafa" rx="8"/>
  <text x="{width/2:.0f}" y="28" text-anchor="middle" font-family="system-ui,sans-serif"
        font-size="15" font-weight="600" fill="#222">{title}</text>
  <text x="{width/2:.0f}" y="46" text-anchor="middle" font-family="system-ui,sans-serif"
        font-size="12" fill="#666">{total} contract tests</text>
  {''.join(slices)}
  {''.join(legend)}
</svg>"""


def _bar_chart(
    data: dict[str, int],
    title: str,
    subtitle: str,
    width: int = 520,
    height: int = 300,
) -> str:
    labels = list(data.keys())
    values = list(data.values())
    max_val = max(values) if values else 1
    margin_left, margin_bottom, margin_top = 120, 48, 56
    chart_w = width - margin_left - 24
    chart_h = height - margin_bottom - margin_top
    bar_h = chart_h / len(labels) * 0.55
    gap = chart_h / len(labels)

    bars: list[str] = []
    for i, (label, value) in enumerate(data.items()):
        y = margin_top + i * gap + (gap - bar_h) / 2
        bar_w = (value / max_val) * chart_w
        color = CATEGORY_COLORS[i % len(CATEGORY_COLORS)]
        bars.append(
            f'<text x="{margin_left - 8}" y="{y + bar_h * 0.72:.0f}" text-anchor="end" '
            f'font-family="system-ui,sans-serif" font-size="12" fill="#444">{label}</text>'
            f'<rect x="{margin_left}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
            f'fill="{color}" rx="3"/>'
            f'<text x="{margin_left + bar_w + 6:.0f}" y="{y + bar_h * 0.72:.0f}" '
            f'font-family="system-ui,sans-serif" font-size="12" fill="#333">{value}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#fafafa" rx="8"/>
  <text x="{width/2:.0f}" y="28" text-anchor="middle" font-family="system-ui,sans-serif"
        font-size="15" font-weight="600" fill="#222">{title}</text>
  <text x="{width/2:.0f}" y="46" text-anchor="middle" font-family="system-ui,sans-serif"
        font-size="12" fill="#666">{subtitle}</text>
  {''.join(bars)}
</svg>"""


def _structure_diagram() -> str:
    width, height = 520, 200
    boxes = [
        ("Task", "What to do", "#4C78A8", 20),
        ("Context", "Known scope", "#F58518", 140),
        ("Requirements", "Constraints", "#54A24B", 260),
        ("Verification", "How to check", "#E45756", 380),
    ]
    parts: list[str] = []
    for label, sub, color, x in boxes:
        parts.append(
            f'<rect x="{x}" y="70" width="110" height="72" fill="{color}" rx="6" opacity="0.9"/>'
            f'<text x="{x + 55}" y="100" text-anchor="middle" font-family="system-ui,sans-serif" '
            f'font-size="13" font-weight="600" fill="#fff">{label}</text>'
            f'<text x="{x + 55}" y="120" text-anchor="middle" font-family="system-ui,sans-serif" '
            f'font-size="11" fill="#fff" opacity="0.9">{sub}</text>'
        )
        if x < 380:
            parts.append(
                f'<polygon points="{x + 112},106 {x + 128},106 {x + 120},114" fill="#999"/>'
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#fafafa" rx="8"/>
  <text x="{width/2:.0f}" y="28" text-anchor="middle" font-family="system-ui,sans-serif"
        font-size="15" font-weight="600" fill="#222">What Agent Brief adds</text>
  <text x="{width/2:.0f}" y="48" text-anchor="middle" font-family="system-ui,sans-serif"
        font-size="12" fill="#666">Missing structure in a vague request</text>
  <rect x="20" y="155" width="200" height="28" fill="#eee" rx="4"/>
  <text x="120" y="174" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="#666">
    "fix login bug" — no structure
  </text>
  <text x="270" y="174" font-family="system-ui,sans-serif" font-size="18" fill="#999">→</text>
  {''.join(parts)}
</svg>"""


def example_category_counts() -> dict[str, int]:
    examples = parse_examples_markdown(EXAMPLES)
    counts: dict[str, int] = {}
    for example in examples:
        if example.kind != "brief":
            continue
        counts[example.category] = counts.get(example.category, 0) + 1
    return counts


def generate_reports() -> list[Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    contract_svg = _pie_chart(
        CONTRACT_TEST_GROUPS,
        COLORS,
        "Contract tests by invariant",
    )
    p = REPORTS_DIR / "contract-tests.svg"
    p.write_text(contract_svg)
    paths.append(p)

    categories = example_category_counts()
    examples_svg = _bar_chart(
        categories,
        "Example briefs by category",
        f"{sum(categories.values())} request types covered",
    )
    p = REPORTS_DIR / "example-categories.svg"
    p.write_text(examples_svg)
    paths.append(p)

    structure_svg = _structure_diagram()
    p = REPORTS_DIR / "brief-structure.svg"
    p.write_text(structure_svg)
    paths.append(p)

    return paths


def main() -> None:
    paths = generate_reports()
    for path in paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
