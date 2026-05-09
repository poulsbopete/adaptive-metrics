---
slug: welcome
type: challenge
title: Welcome — adaptive metrics & TCO
teaser: >-
  Connect this lab to autonomous observability positioning and adaptive-style metrics governance on Elastic.
notes:
  - type: text
    contents: >-
      Track scripts install Python and copy fixtures to /opt/adaptive-metrics-lab.
tabs:
  - title: Shell
    type: terminal
    hostname: sandbox
difficulty: basic
timelimit: 600
---

## Context

Elastic’s internal **Autonomous observability** tracks (for example the managed lab you linked) focus on AI-assisted workflows across logs, metrics, and traces. This workshop is a **deliberate companion**: it teaches a **governance and TCO** story that procurement teams understand when comparing managed Elastic to “free” metrics stacks.

If you maintain both tracks, keep **terminology aligned** (same Kibana base URL tab, same secret names for Elasticsearch) so learners feel a single narrative.

## What you will do

You will:

1. Treat **declared usage** (dashboards, alerts, SLOs) as the primary signal for “important” metrics.
2. Separate **classification** from **execution**: recommendations first; silent deletion is not the default story.
3. Draft **server-side shaping** policy as YAML you could map to **Kibana Streams** and retention controls in real deployments.

## Verify the lab files

In the **Shell** tab:

```bash
ls -la /opt/adaptive-metrics-lab
test -f /opt/adaptive-metrics-lab/.track-setup-complete && echo "lab ready"
```

Click **Check** when ready.
