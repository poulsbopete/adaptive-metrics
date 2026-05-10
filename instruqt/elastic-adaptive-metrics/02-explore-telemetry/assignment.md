---
slug: explore-telemetry
id: 98kwdohjlsof
type: challenge
title: Explore Live OpenTelemetry Data
teaser: Follow a **short checklist** — Discover, dashboards (including **Adaptive
  Metrics**), APM, SLOs.
notes:
- type: text
  contents: |
    ## Lab 2 — Explore telemetry

    **Goal:** Click through the main Observability surfaces once — **no mastery required.**

    **You'll:**
    - Run ES|QL in Discover
    - Open Retail Banking **and** **Adaptive Metrics / governance** dashboards
    - Peek at **APM** and **SLOs**

    Keep **Last 15 minutes** everywhere.

    **Adaptive Metrics dashboard:** Search **`Adaptive`** or **`Streams savings`** — title contains **Adaptive Metrics · Streams savings & governance (TCO)**.

    **Want the full workshop** (workflows YAML, Streams API, Executive Lens)? See [`metric-streams-governance-workflow.md`](https://github.com/poulsbopete/adaptive-metrics/blob/main/instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md) in the repo.
- type: text
  contents: |
    ## Three signals

    | Signal | Menu |
    |--------|------|
    | Logs | Discover → ES\|QL |
    | Traces | Applications → Service inventory |
    | Metrics | Dashboards / Infrastructure |
- type: text
  contents: |
    ## Optional — sample ES|QL (errors by service)

    ```
    FROM logs*
    | WHERE @timestamp > NOW() - 15 MINUTES
    | WHERE severity_text == "ERROR"
    | STATS errors = COUNT(*) BY service.name
    | SORT errors DESC
    ```

    **Governance noise (if shipped):** filter `service.name == "noisy-governance-shipper"` to practice Streams — see repo docs.
tabs:
- id: v7hvexx2xbyr
  title: Demo App
  type: service
  hostname: es3-api
  path: /
  port: 8090
- id: siyyboa1ig6j
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

# Explore Live OpenTelemetry Data

Default scenario: **Retail Banking**. Use **Elastic Serverless** with **Last 15 minutes**.

---

## Checklist (do in order)

| Step | Where | What |
|:---:|:---|:---|
| 1 | **Discover** → ES\|QL | Run: `FROM logs* \| WHERE @timestamp > NOW() - 15 MINUTES \| LIMIT 50` — confirm rows |
| 2 | **Dashboards** | Search **`Retail Banking`** → open **Systems Operations** *or* **Executive** |
| 3 | **Dashboards** | Search **`Adaptive`** or **`governance`** → open **Adaptive Metrics · Streams savings & governance (TCO)** |
| 4 | **Applications** → **Service inventory** | Click any retail service → open **one transaction / trace** |
| 5 | **Observability** → **SLOs** | Open **one** SLO |

✅ **Continue** after steps **1–3** (minimum). Steps 4–5 recommended.

**Bonus:** **Observability → Workflows** → search **`governance`** → **Retail Banking Metric governance snapshot** (Adaptive Metrics / Cases — installed by lab setup).

> **Tip:** If ES|QL errors on `TS metrics*` time-series rules, use `FROM metrics*` + `STATS` for counts — see [ES\|QL TS docs](https://www.elastic.co/docs/reference/query-languages/esql/commands/ts).

---

## Optional next steps

- **Workflows:** **Observability → Workflows** — six **Retail Banking Platform** demos ship from the launcher; **Retail Banking Metric governance snapshot** (Adaptive Metrics / Cases / ES|QL) is **installed by track setup** (`adaptive-metrics-metric-governance-starter`). Re-import from repo only if you edit YAML: [`metric-governance-retail-banking-starter.yaml`](https://github.com/poulsbopete/adaptive-metrics/blob/main/workflows/kibana/metric-governance-retail-banking-starter.yaml).
- **Cases:** **`[Governance]`** cases appear if that workflow is enabled — tie **modeled_policy_savings_pct** to FinOps narrative with **Observability AI Assistant**.
- **Deep dive:** [`metric-streams-governance-workflow.md`](https://github.com/poulsbopete/adaptive-metrics/blob/main/instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md) — Streams API, safety checklist, K8s retention example.
