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
    <div style="width:100vw;max-width:100vw;margin-left:calc(50% - 50vw);box-sizing:border-box;">
    <iframe src="https://poulsbopete.github.io/adaptive-metrics/" width="100%" height="920" frameborder="0" allowfullscreen title="Adaptive Metrics slides" style="display:block;width:100%;min-height:78vh;border:0;border-radius:8px;"></iframe>
    </div>
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

Use the **copy boxes** — click inside the gray block, select all (`⌘A` / `Ctrl+A`), copy (`⌘C` / `Ctrl+C`), paste into Kibana.

### Step 1 — Discover → ES|QL

1. Open **Discover** and switch to **ES|QL**.
2. Paste:

```
FROM logs*
| WHERE @timestamp > NOW() - 15 MINUTES
| LIMIT 50
```

3. Run the query and confirm you see rows.

### Step 2 — Dashboards (Retail Banking)

1. Open **Dashboards**.
2. Paste into the dashboard search field:

```
Retail Banking
```

3. Open **Systems Operations** or **Executive**.

### Step 3 — Dashboards (Adaptive Metrics)

1. Open **Dashboards** again (or stay on the list).
2. Paste **one** of these into search:

```
Adaptive
```

```
governance
```

3. Open **Retail Banking — Adaptive Metrics · Streams savings & governance (TCO)**.
   *(Optional — paste the full title if the list is long:)*

```
Retail Banking — Adaptive Metrics · Streams savings & governance (TCO)
```

### Step 4 — Applications → Service inventory

1. Open **Applications** → **Service inventory**.
2. Click any retail banking service and open **one** transaction or trace.

### Step 5 — SLOs

1. Open **Observability** → **SLOs** and open **one** SLO.

✅ **Continue** after steps **1–3** (minimum). Steps **4–5** recommended.

### Bonus — Workflows

1. Open **Observability** → **Workflows**.
2. Paste into search:

```
governance
```

3. Open **Retail Banking Platform — Adaptive Metrics · Metric governance snapshot** (Cases / ES|QL — installed by track setup).

> **Tip:** If ES|QL errors on `TS metrics*` time-series rules, use `FROM metrics*` + `STATS` for counts — see [ES\|QL TS docs](https://www.elastic.co/docs/reference/query-languages/esql/commands/ts).

---

## Optional next steps

- **Workflows:** **Observability → Workflows** — **six** demos ship from the launcher; **Retail Banking Platform — Adaptive Metrics · Metric governance snapshot** (Adaptive Metrics / Cases / ES|QL) is **installed by track setup** (`adaptive-metrics-metric-governance-starter`). Re-import from repo only if you edit YAML: [`metric-governance-retail-banking-starter.yaml`](https://github.com/poulsbopete/adaptive-metrics/blob/main/workflows/kibana/metric-governance-retail-banking-starter.yaml).
- **Cases:** **`[Governance]`** cases appear if that workflow is enabled — tie **modeled_policy_savings_pct** to FinOps narrative with **Observability AI Assistant**.
- **Deep dive:** [`metric-streams-governance-workflow.md`](https://github.com/poulsbopete/adaptive-metrics/blob/main/instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md) — Streams API, safety checklist, K8s retention example.
