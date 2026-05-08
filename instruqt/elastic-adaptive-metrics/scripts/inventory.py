#!/usr/bin/env python3
"""Write a human-readable inventory from bundled metric-manifest.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--manifest",
        default="/opt/adaptive-metrics-lab/fixtures/metric-manifest.json",
        help="Path to metric-manifest.json",
    )
    p.add_argument(
        "--out",
        default="/opt/adaptive-metrics-lab/reports/inventory.md",
        help="Markdown report path",
    )
    args = p.parse_args()

    manifest_path = Path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    metrics = data.get("metrics", [])

    lines: list[str] = []
    lines.append("# Metric inventory")
    lines.append("")
    lines.append(f"_Source: `{manifest_path}`_")
    lines.append("")
    lines.append("| Metric | Est. series | GB/day (est.) |")
    lines.append("|---|---:|---:|")
    for m in sorted(metrics, key=lambda x: -float(x.get("series_estimate", 0))):
        name = m.get("name", "")
        series = int(m.get("series_estimate", 0))
        gb = float(m.get("ingest_gb_per_day", 0.0))
        lines.append(f"| `{name}` | {series:,} | {gb:.2f} |")
    lines.append("")
    lines.append("## Cardinality hotspots")
    lines.append("")
    top = sorted(metrics, key=lambda x: -float(x.get("series_estimate", 0)))[:3]
    for m in top:
        lines.append(f"- `{m.get('name')}` — **{int(m.get('series_estimate', 0)):,}** series")
    lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
