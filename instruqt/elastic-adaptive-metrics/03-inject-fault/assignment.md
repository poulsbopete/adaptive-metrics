---
slug: inject-fault
id: idjcheiijoey
type: challenge
title: Inject a Fault and Watch Elastic Detect It
teaser: One fault from **Demo App** → see alerts, workflow, and **Case** in Kibana.
notes:
- type: text
  contents: |
    ## Lab 3 — Chaos → detection

    **Goal:** Prove alert → workflow → case — **three clicks**, then watch Kibana.

    **You'll:**
    - Inject **one** fault from the Demo App
    - Confirm errors in Discover (optional query below)
    - Open **Workflows** then **Cases**

    **Retail Banking channels** cover payments, claims, mobile, fraud, infra (20 channels). Pick any channel you like.

    **Suggested first run:** **ACH Direct Deposit Delay** or **Mobile App API Timeout** — easy to narrate.

    **Fault vs sliders:** **Inject Fault** drives channel alerts → workflows → cases (the lab “process”). **Infrastructure spikes** are separate sliders—when finished, dial them **down** so you aren’t mixing lingering infra stress with fault demos.
tabs:
- id: slqip2bp1bjo
  title: Demo App
  type: service
  hostname: es3-api
  path: /
  port: 8090
- id: ydocxzfj1yyn
  title: Elastic Serverless
  type: service
  hostname: es3-api
  path: /app/discover#/?_a=(columns:!(service.name,severity_text,body.text),index:logs.otel,interval:auto,query:(esql:'FROM+logs.otel%2Clogs.otel.*+%7C+WHERE+%40timestamp+>+NOW()+-+30+minutes+%7C+WHERE+severity_text+%3D%3D+%22ERROR%22+%7C+KEEP+service.name%2C+body.text%2C+severity_text%2C+%40timestamp+%7C+SORT+%40timestamp+DESC+%7C+LIMIT+50',language:esql),sort:!(!('@timestamp',desc)))&_g=(filters:!(),refreshInterval:(pause:!f,value:10000),time:(from:now-30m,to:now))
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

# Inject a Fault and Watch Elastic Detect It

---

## Fault channels vs infrastructure spikes

**In production**, you still resolve **capacity and metric stress** through the **same operational spine**: **alerts** (threshold / ML / SLO burn) → **workflows** → **Cases** → remediation — not ad-hoc tweaks without a record.

**In this simulator**, there are two mechanics:

| Control | Role in the lab |
|---------|-------------------|
| **Inject Fault** / **Resolve** | Scripted **fault channels** tied to ES|QL alert rules → **Significant Event Notification** workflows → **Cases**. This is the path we grade around. |
| **Infrastructure spikes** (CPU, memory, K8s OOM, latency) | Broad stress on hosts/clusters; useful to watch **Infrastructure** / metrics while narrating. **You can move these sliders as soon as the deployment is running**—no fault injection required. When a fault channel *is* active, spikes preferentially track those services’ infrastructure; with **no** fault active, stress applies platform-wide (see the note under the sliders). |

**Practice:** After exploring sliders, **reset them toward zero/low**. For the **Elastic workflow story**, complete **Inject Fault** → watch Kibana → **Resolve** on the channel when the simulator enables it.

---

## Step 1 — Inject (~1 min)

1. **Demo App** → active deployment → **Chaos**
2. Pick **any** fault channel → **Inject Fault**

*(Optional)* In **Elastic Serverless → Discover → ES|QL**, watch errors climb:

```esql
FROM logs*
| WHERE @timestamp > NOW() - 15 MINUTES
| WHERE severity_text == "ERROR"
| STATS errors = COUNT(*) BY service.name
| SORT errors DESC
```

Re-run every ~30s until you see the affected service spike.

---

## Step 2 — Workflow (~2 min)

**Observability → Workflows** → find **Significant Event Notification** (name includes your scenario, e.g. **Retail Banking Platform**) → open the **latest run**.

Skim steps: count errors → AI RCA → **create case**.

---

## Step 3 — Case (~1 min)

**Observability → Cases** — open the newest auto-created case (severity often **High**).

✅ **Done** when you see **one workflow run** and **one case**.

---

## Why operators care (optional)

Incidents stress **the same signals** you declared as important (**alerts, SLOs, dashboards, workflows**). Keep rich retention there; trim **high-cardinality** volume that never appears on those surfaces — **downsampling**, **Streams**, shorter tiers — so cost tracks operational reality.

**Closing the loop:** Real remediation for infra spikes belongs in **alert rules and Cases** too—this demo spotlights that path via **fault channels**; extend the same pattern to **your** capacity SLOs and anomaly detectors in production.
