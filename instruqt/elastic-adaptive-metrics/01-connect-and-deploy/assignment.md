---
slug: connect-and-deploy
id: zcj2ykfryvmc
type: challenge
title: Connect to Elastic Cloud & Deploy
teaser: Confirm Retail Banking is live — one ES|QL query + one dashboard in **under
  5 minutes**.
notes:
- type: text
  contents: |
    <div style="width:100vw;max-width:100vw;margin-left:calc(50% - 50vw);box-sizing:border-box;">
    <iframe src="https://poulsbopete.github.io/adaptive-metrics/" width="100%" height="920" frameborder="0" allowfullscreen title="Adaptive Metrics slides" style="display:block;width:100%;min-height:78vh;border:0;border-radius:8px;"></iframe>
    </div>
tabs:
- id: qchxpuxaamyj
  title: Demo App
  type: service
  hostname: es3-api
  path: /
  port: 8090
- id: ljorg10ryfzj
  title: Elastic Serverless
  type: service
  hostname: es3-api
  path: /app/dashboards#/list?_g=(filters:!(),refreshInterval:(pause:!f,value:30000),time:(from:now-30m,to:now))
  port: 8080
  custom_request_headers:
  - key: Content-Security-Policy
    value: 'script-src ''self'' https://kibana.estccdn.com; worker-src blob: ''self'';
      style-src ''unsafe-inline'' ''self'' https://kibana.estccdn.com; style-src-elem
      ''unsafe-inline'' ''self'' https://kibana.estccdn.com'
  custom_response_headers:
  - key: Content-Security-Policy
    value: 'script-src ''self'' https://kibana.estccdn.com; worker-src blob: ''self'';
      style-src ''unsafe-inline'' ''self'' https://kibana.estccdn.com; style-src-elem
      ''unsafe-inline'' ''self'' https://kibana.estccdn.com'
difficulty: basic
timelimit: 0
enhanced_loading: null
---

# Connect to Elastic Cloud & Deploy

Your Serverless project and demo stack are **already running**.

First boot usually takes **3–4 minutes**. If a tab spins, wait and refresh.

---

## Steps (~5 minutes)

1. **Demo App** tab → confirm a deployment is **Running**. If not, launch **Retail Banking Platform**.
2. **Elastic Serverless** tab → set **Last 15 minutes** (clock, top right).
3. **Discover** → switch to **ES|QL** → run:

```esql
FROM logs*
| WHERE @timestamp > NOW() - 15 MINUTES
| LIMIT 25
```

4. **Dashboards** → search **`Retail Banking`** → open **Systems Operations** *or* **Executive**.
5. *(Recommended)* Search **`Adaptive`** or **`governance`** → open **Retail Banking — Adaptive Metrics · Streams savings & governance (TCO)**.
   If it does not appear yet, wait ~1 minute and click **Refresh** on the dashboard list (track setup POSTs it after Kibana is ready). Still missing? Ask your host — the VM **`setup-es3-api`** log shows **`Adaptive Metrics dashboard created`** or retry errors.

✅ **Continue** when you see **log rows** or **any** populated dashboard.

> **Tip:** **Last 15 minutes** keeps panels fresh.

---

## Context (optional)

Metrics that appear on **dashboards, SLOs, alerts, or workflows** are **declared usage** — what you protect when tuning retention and cost. Everything else is fair game for **Streams**, rollups, and **downsampling**. Deeper story: [`README.md`](https://github.com/poulsbopete/adaptive-metrics/blob/main/README.md) in this repo.
