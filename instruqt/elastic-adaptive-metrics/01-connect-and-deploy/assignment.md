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
    ## Lab 1 — Quick orientation

    **Goal:** Prove telemetry is flowing in Kibana. **Nothing to install.**

    **You will:**
    - See a **Running** deployment in the **Demo App**
    - Use **Elastic Serverless** (already logged in)
    - Run **one** ES|QL query and open **one** dashboard

    **Optional while you wait:** **[Adaptive Metrics — slides](https://poulsbopete.github.io/adaptive-metrics/)** (keyboard **←** **→** Home End).

    First boot usually takes **3–4 minutes**. If a tab spins, wait and refresh.
- type: text
  contents: |
    ## Two tabs

    | Tab | Use it for |
    |-----|------------|
    | **Demo App** | Status, scenario cards, **Chaos** (later) |
    | **Elastic Serverless** | Kibana — Discover, Dashboards, APM |

    **Default:** **Retail Banking Platform** (payments, claims, fraud, …). Pick another card in the Demo App if you prefer.
- type: text
  contents: |
    ## Already provisioned

    | | |
    |-|--|
    | Alerts | ES\|QL rules on fault channels |
    | Workflows | Incident playbooks |
    | Dashboards | Systems Ops + Executive + **Adaptive Metrics · governance / TCO** |
    | Telemetry | OTel logs, metrics, traces |
- type: text
  contents: |
    ## Optional — Adaptive Metrics slides (embedded)

    Same deck as **[poulsbopete.github.io/adaptive-metrics](https://poulsbopete.github.io/adaptive-metrics/)**.

    <iframe src="https://poulsbopete.github.io/adaptive-metrics/" width="100%" height="650" frameborder="0" allowfullscreen style="border-radius:8px;display:block;"></iframe>
- type: text
  contents: |
    ## Optional — mini-game while provisioning loads

    <iframe src="https://poulsbopete.github.io/Vampire-Clone/" width="100%" height="650" frameborder="0" allowfullscreen style="border-radius:8px;display:block;"></iframe>
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
