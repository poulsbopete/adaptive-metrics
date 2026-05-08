---
slug: inventory-hotspots
type: challenge
title: "Challenge 2: Inventory cardinality hotspots"
teaser: Generate a markdown inventory from bundled metric fixtures.
notes:
  - type: text
    contents: >-
      This challenge is fully offline. Output is written under /opt/adaptive-metrics-lab/reports/.
tabs:
  - title: Shell
    type: terminal
    hostname: sandbox
difficulty: basic
timelimit: 900
---

## Goal

Build a **metric inventory** that highlights **cardinality hotspots** before any policy change. This mirrors the first step of vendor “adaptive metrics” products, but keeps the data local and explainable.

## Steps

```bash
python3 /opt/adaptive-metrics-lab/scripts/inventory.py
sed -n '1,120p' /opt/adaptive-metrics-lab/reports/inventory.md
```

Confirm the report lists `kube_pod_status_phase` near the top of the hotspots section.

Click **Check**.
