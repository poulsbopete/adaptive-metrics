---
slug: optional-live-elastic
type: challenge
title: "Challenge 5 (optional): Validate Elasticsearch connectivity"
teaser: >-
  If your org injects ELASTIC_URL + ELASTIC_API_KEY secrets, prove the cluster is reachable.
notes:
  - type: text
    contents: >-
      When this track is chained after Autonomous observability, reuse the same secret names and host tabs.
tabs:
  - title: Shell
    type: terminal
    hostname: sandbox
difficulty: basic
timelimit: 600
---

## When to use this challenge

Use it when your Instruqt sandbox defines secrets:

- `ELASTIC_URL` (for example `https://my-deployment.es.region.cloud.es.io:443`)
- `ELASTIC_API_KEY` (Base64-encoded API key id:key material)

If secrets are **not** configured, the check script **passes automatically** so public demos still work.

## Steps

```bash
/opt/adaptive-metrics-lab/scripts/check_elastic_health.sh
```

Click **Check**.
