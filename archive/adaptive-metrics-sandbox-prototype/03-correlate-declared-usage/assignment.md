---
slug: correlate-declared-usage
type: challenge
title: "Challenge 3: Correlate metrics with declared usage"
teaser: Classify metrics using dashboards, alerts, and SLO references (fixtures).
notes:
  - type: text
    contents: >-
      Declared usage is a practical stand-in for “used in production analysis” when agents are not modeled yet.
tabs:
  - title: Shell
    type: terminal
    hostname: sandbox
difficulty: intermediate
timelimit: 900
---

## Goal

Produce an **adaptive metrics report**: each metric is tagged against **declared usage** derived from `declared-usage.ndjson` (dashboards, alerts, SLOs).

This is the same *class* of signal described in Grafana’s **Adaptive Metrics** documentation for unused time series discovery—useful positioning when comparing to VictoriaMetrics-style “free” storage that still carries operational and cardinality risk ([Grafana Adaptive Metrics](https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/)).

## Steps

```bash
python3 /opt/adaptive-metrics-lab/scripts/correlate_usage.py
grep -n "legacy_batch_job_queue_depth" -n /opt/adaptive-metrics-lab/reports/adaptive-metrics-report.md
grep -n "http.server.duration" /opt/adaptive-metrics-lab/reports/adaptive-metrics-report.md
```

You should see `legacy_batch_job_queue_depth` classified as **no** declared usage, and `http.server.duration` as **yes**.

Click **Check**.
