#!/usr/bin/env python3
"""
Correlate metric names from fixtures with declared usage (dashboards, alerts, SLOs).

This models adaptive-style metrics "declared usage" without requiring a live cluster.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_ndjson(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def declared_metrics(usages: list[dict]) -> set[str]:
    found: set[str] = set()
    for u in usages:
        for ref in u.get("references", []):
            found.add(str(ref))
    return found


def metric_matches_declaration(metric_name: str, declared: set[str]) -> bool:
    if metric_name in declared:
        return True
    for d in declared:
        if metric_name.startswith(d):
            return True
        if d.endswith(".") and metric_name.startswith(d):
            return True
    # prefix-style declarations like "http.server." in dashboards list full name in fixture;
    # allow substring for demo robustness
    for d in declared:
        if d in metric_name:
            return True
    return False


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--manifest",
        default="/opt/adaptive-metrics-lab/fixtures/metric-manifest.json",
    )
    p.add_argument(
        "--usage",
        default="/opt/adaptive-metrics-lab/fixtures/declared-usage.ndjson",
    )
    p.add_argument(
        "--out",
        default="/opt/adaptive-metrics-lab/reports/adaptive-metrics-report.md",
    )
    args = p.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    usages = load_ndjson(Path(args.usage))
    declared = declared_metrics(usages)

    lines: list[str] = []
    lines.append("# Adaptive metrics report")
    lines.append("")
    lines.append("## Declared usage signals")
    lines.append("")
    for u in usages:
        kind = u.get("kind", "")
        title = u.get("title", "")
        refs = ", ".join(f"`{r}`" for r in u.get("references", []))
        lines.append(f"- **{kind}**: {title} → {refs}")
    lines.append("")
    lines.append("## Classification")
    lines.append("")
    lines.append("| Metric | Declared usage? | Suggested posture |")
    lines.append("|---|---|---|")

    for m in sorted(manifest.get("metrics", []), key=lambda x: str(x.get("name"))):
        name = str(m.get("name", ""))
        used = metric_matches_declaration(name, declared)
        if used:
            posture = "Keep / tiered retention; prefer rollups for very high cardinality if still hot after review"
        else:
            posture = "No declared usage in fixtures — short hot retention + coarse downsampling; require human approval before drop"
        lines.append(f"| `{name}` | {'yes' if used else 'no'} | {posture} |")

    lines.append("")
    lines.append("## Executive framing (TCO)")
    lines.append("")
    lines.append(
        "- **Control beats \"free\"**: predictable retention and server-side shaping reduce surprise growth "
        "versus unconstrained open-source stacks."
    )
    lines.append(
        "- **Downsampling and rollups** complement adaptive-style classification—Elastic-native "
        "storage, downsampling, and Streams-style governance complete the TCO story."
    )
    lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
