---
slug: explore-telemetry
id: 98kwdohjlsof
type: challenge
title: Explore Live OpenTelemetry Data
teaser: Map live metrics to dashboards and SLOs—that **declared usage** signal—then
  relate **write volume** to **downsampling** and **retention** on Elastic Serverless.
notes:
- type: text
  contents: |
    ## Lab 2 — Explore Live OpenTelemetry Data

    **Declared usage lens:** This track defaults to **Retail Banking Platform**. Some products automate “adaptive” metrics discovery (unused series, aggregation, drops). In this lab you do the **discovery** manually—**which metric families show up on shipped dashboards and SLOs vs raw generator volume**—using **ES|QL** and the **Systems Operations** / **Executive** dashboards. That is the input to **downsampling** and **Streams** policy. **Kibana Workflows** here are **incident- and SLO-oriented** (see list under **Observability → Workflows**); they do **not** include a separate tile that auto-scans every metric and proposes drops—that pattern is **custom automation** you can add on the same platform (scheduled workflow + ES|QL + case for human approval).

    **By the end of this challenge you will:**

    - ✅ Query live logs with ES|QL in Discover
    - ✅ Run time-series ES|QL queries against live metric streams
    - ✅ Explore Systems Operations (telemetry) and Executive (`business.*` leadership KPIs) dashboards
    - ✅ View distributed traces and service maps in APM
    - ✅ Inspect host metrics across 3 simulated cloud providers
    - ✅ Relate **Systems Operations** and **Executive** dashboards to which metric families you would keep under longer retention in production

    **Your data is real.** Every log, trace, and metric is generated fresh and shipped via OTLP directly to Elastic — no recordings, no synthetic replay.
- type: text
  contents: |
    ## Three Signals, One Store

    Elastic correlates logs, metrics, and traces in a single data store — no switching tools, no context loss.

    | Signal | Where to look | Index pattern |
    |--------|--------------|---------------|
    | **Logs** | Discover → ES\|QL | `logs*` |
    | **Traces** | Applications → Service inventory | `traces-*` |
    | **Metrics** | Observability → Infrastructure | `metrics-*` |

    Signals connect automatically — a trace span links to its log lines via `trace.id`, and error spikes correlate with host CPU in the same timeline.
- type: text
  contents: |
    ## What's Generating Telemetry

    **Nine instrumented microservices** for **Retail Banking** (application logs + traces): for example **`mobile-gateway`**, **`payment-engine`**, **`claims-processor`**, **`policy-manager`**, **`fraud-sentinel`**, **`member-portal`**, **`auth-gateway`**, **`document-vault`**, and **`quote-engine`**. If you switched scenarios in the Demo App, service names follow that card instead.

    **Background generators** (infrastructure telemetry):
    - 3 cloud hosts (AWS, GCP, Azure) — CPU, memory, disk, network
    - Kubernetes node + pod metrics
    - Nginx access logs and MySQL slow query logs
    - VPC flow logs and distributed trace chains

    > **Tip:** Set the time range to **Last 15 minutes** to see the freshest data.
- type: text
  contents: |
    ## ES|QL: Query Telemetry Like a Pipeline

    ES|QL is Elastic's pipe-based query language. Run these in **Discover → ES|QL** during the challenge:

    **Error spike by service:**
    ```
    FROM logs*
    | WHERE @timestamp > NOW() - 15 MINUTES
    | WHERE severity_text == "ERROR"
    | STATS errors = COUNT(*) BY service.name
    | SORT errors DESC
    ```

    **Latency trend (Retail Banking — mobile API):**
    ```
    TS metrics*
    | WHERE @timestamp > NOW() - 30 MINUTES
    | EVAL minute = DATE_TRUNC(1 minute, @timestamp)
    | STATS avg_api_ms = AVG(mobile_gateway.api_latency_ms) BY minute
    | SORT minute DESC
    ```
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

# Explore Live OpenTelemetry Telemetry

This track defaults to **Retail Banking Platform** — digital banking, payments, claims, policy, and fraud signals. Open the **Elastic Serverless** tab.

---

## What the Workflows list is (and is not)

Under **Observability → Workflows** you will see **six operational workflows** for your deployment (titles are prefixed with the scenario name — for the default, **Retail Banking Platform**). They cover **SLO maintenance**, **significant event notification**, **remediation**, **escalation**, and **daily reporting**—the same surfaces that prove **declared usage** when production breaks.

You will **not** see a built-in workflow whose only job is to “automatically determine which metrics are unused and suggest dropping or aggregating dimensions.” That outcome is not a single stock tile in this demo; on Elastic it is typically delivered by combining **(1)** **Streams** and ingest rules **(2)** **downsampling / rollup** settings **(3)** **ES|QL** or ML jobs that compare metric volume to dashboard and SLO references **(4)** optional **custom** Kibana workflows you create (for example a **scheduled** run that writes recommendations to a **Case** for human approval). This workshop teaches the discovery and positioning; the **implementation** of step (4) is a **custom** Kibana workflow you author (see below).

---

## Stretch design: Streams governance loop (Workflows + AI + Agent)

**Goal:** A workflow that runs **every five minutes** (or on your chosen schedule), **lists Streams** (`GET /api/streams`), identifies **wired** parents that can accept **child routes** (“sub-streams”), gathers **ES|QL + declared-usage** context, calls an **AI** step for a JSON-safe plan, optionally opens a **Case** for approval, then **`PUT /api/streams/{name}`** to create/update child streams and processing—**not** silent deletes.

**Elastic Agent:** The workflow runs **inside Kibana** (scheduled + `kibana.request` steps per [Kibana workflow steps](https://www.elastic.co/docs/explore-analyze/workflows/steps/kibana)). Agents keep shipping under **Fleet** policy; **Streams** changes affect **routing/processing of ingested documents**. Narrowing **what** agents collect is a **separate Fleet policy** branch—only after approval.

**Authoring reference:** See the blueprint in this repository: `instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md` (API links for [list streams](https://www.elastic.co/docs/api/doc/kibana/operation/operation-get-streams) and [create/update stream](https://www.elastic.co/docs/api/doc/kibana/operation/operation-put-streams-name), mermaid graph, safety checklist).

---

## What's Generating Telemetry

The platform runs several background generators simultaneously:

| Generator | What It Produces |
|-----------|-----------------|
| **9 retail-banking services** | Application logs, traces, errors (`mobile-gateway`, `payment-engine`, `claims-processor`, …) |
| **Host metrics** | CPU, memory, disk, network for 3 cloud hosts |
| **Kubernetes metrics** | Node, pod, container metrics |
| **Nginx metrics + logs** | Access logs, error logs, request spans |
| **MySQL logs** | Slow query + error logs |
| **VPC flow logs** | Network flow telemetry |
| **Distributed traces** | Multi-service request chains |

---

## Explore #1 — Logs via ES|QL

1. In the **Elastic Serverless** tab → **Discover**
2. Switch to **ES|QL** mode (top-left toggle)
3. Run this query:

```esql
FROM logs*
| WHERE @timestamp > NOW() - 5 MINUTES
| KEEP service.name, body.text, severity_text, @timestamp
| SORT @timestamp DESC
| LIMIT 50
```

You should see a stream of logs from multiple services. Once you confirm data is flowing, try filtering to errors only:

```esql
FROM logs*
| WHERE @timestamp > NOW() - 15 MINUTES
| WHERE severity_text == "ERROR"
| STATS error_count = COUNT(*) BY service.name
| SORT error_count DESC
```

**Things to notice:**
- `service.name`: for the default **Retail Banking** card, values include **`payment-engine`**, **`claims-processor`**, **`mobile-gateway`**, **`member-portal`**, and peers from the nine-service set (hyphenated names in logs and APM)
- `severity_text`: `INFO`, `WARN`, `ERROR`
- `body.text` contains the raw log message and error type

---

## Explore #2 — ES|QL Time Series Queries

> **Note:** `TS metrics*` column names follow the demo’s OTLP gauge names (dots in metric names become fields such as `payment_engine.transactions_per_sec`). If a query returns no columns, run `FROM metrics* | WHERE @timestamp > NOW() - 15 minutes | KEEP * | LIMIT 3` once to confirm field spelling for your stack version, then adjust.

In the **Elastic Serverless** tab → **Discover** → **ES|QL** mode, try these queries against the live metrics stream.

### Payment engine throughput and ACH backlog
```esql
TS metrics*
| WHERE @timestamp > NOW() - 15 MINUTES
| EVAL minute = DATE_TRUNC(1 minute, @timestamp)
| STATS
    txn_per_sec = AVG(payment_engine.transactions_per_sec),
    ach_queue     = AVG(payment_engine.ach_queue_depth),
    auth_ok_pct   = AVG(payment_engine.auth_success_rate)
  BY minute
| SORT minute DESC
```

### Mobile API latency vs healthy band
```esql
TS metrics*
| WHERE @timestamp > NOW() - 30 MINUTES
| EVAL minute = DATE_TRUNC(1 minute, @timestamp)
| STATS avg_api_ms = AVG(mobile_gateway.api_latency_ms) BY minute
| EVAL status = CASE(
    avg_api_ms > 1200, "🔴 CRITICAL",
    avg_api_ms > 600, "🟡 DEGRADED",
    "🟢 HEALTHY"
  )
| SORT minute DESC
```

### Claims and fraud pressure (same timeline)
```esql
TS metrics*
| WHERE @timestamp > NOW() - 20 MINUTES
| EVAL minute = DATE_TRUNC(1 minute, @timestamp)
| STATS
    claims_queue = AVG(claims_processor.queue_depth),
    fraud_score    = AVG(fraud_sentinel.avg_risk_score),
    fraud_latency  = AVG(fraud_sentinel.model_latency_ms)
  BY minute
| SORT minute DESC
```

### Policy book vs quote path
```esql
TS metrics*
| WHERE @timestamp > NOW() - 30 MINUTES
| EVAL bucket5m = DATE_TRUNC(5 minutes, @timestamp)
| STATS
    active_policies = AVG(policy_manager.active_policies),
    renewal_pct       = AVG(policy_manager.renewal_rate),
    quote_latency_ms  = AVG(quote_engine.response_time_ms)
  BY bucket5m
| SORT bucket5m DESC
```

### Log volume by service and severity over time
```esql
FROM logs*
| WHERE @timestamp > NOW() - 30 MINUTES
| EVAL minute = DATE_TRUNC(1 minute, @timestamp)
| STATS
    errors = COUNT(*) WHERE severity_text == "ERROR",
    warnings = COUNT(*) WHERE severity_text == "WARN",
    total  = COUNT(*)
  BY minute, service.name
| SORT minute DESC, total DESC
```

> **Tip:** After triggering a chaos fault in the next challenge, re-run this query to watch the error count spike for the affected service in real time — while healthy services stay flat.

---

## Explore #3 — Dashboards

The deployer creates **two** Kibana saved dashboards for **every** scenario. Open the **Elastic Serverless** tab → **Dashboards** → search **`Retail Banking Platform`** (default) or the name of the card you launched.

### Systems Operations

Saved object id ends in **`-exec-dashboard`**. This is the engineering view: service health, RED-style signals, logs, traces, and infrastructure context tied to the running demo.

### Executive (business KPIs)

Saved object id ends in **`-business-exec-dashboard`**. Panels chart **`business.*`** gauges emitted from **one designated service per scenario** (for Retail Banking, **`member-portal`**). Those series are **shared across demo cards** for workshop consistency—treat them as **synthetic leadership KPIs** for the lab; in production you would rename panels to match your bank’s reporting (NII, deposits, loan growth, claims cycle time, digital adoption, and so on).

**How the data is produced**

- **`member-portal`** emits the `business.*` gauges each telemetry cycle so Executive charts are not duplicated across all nine services.
- Values are **real-time generated** for the lab (plausible ranges), then shipped like any other metric so you can correlate movement with chaos, latency, or errors on **Systems Operations**.

**How to read Executive vs Systems Operations for governance**

| Lens | What to tie to **declared usage** |
|------|-----------------------------------|
| **Digital & member experience** | Portal and mobile signals on **Systems Operations** (`member_portal.*`, `mobile_gateway.*`) plus any Executive panels you map to “digital adoption.” |
| **Payments & money movement** | **`payment_engine.*`** (throughput, ACH queue, auth success) — primary TCO hotspot when faults hit ACH, wires, or bill pay. |
| **Claims & policy** | **`claims_processor.*`**, **`policy_manager.*`**, **`quote_engine.*`** — cycle time, queues, renewal, and quote latency families. |
| **Trust & safety** | **`fraud_sentinel.*`**, **`auth_gateway.*`**, **`document_vault.*`** — risk score, MFA delivery, uploads, and storage. |

Use **Executive** for stakeholder-style storytelling; use **Systems Operations** when you need to prove *why* a KPI moved (drill to services, logs, and traces).

---

## Adaptive metrics — declared usage and tiers (same sandbox)

You already have the **same sandbox** as a full observability workshop. Use it to practice **governance**—**unused vs declared-used** series—entirely on Elastic:

1. **Declared usage** — Open **Dashboards** and list which metric charts your deployment ships for **Retail Banking** (and **SLOs** / **alert rules**). Those are the series you treat as **in use** when proposing retention or rollups; everything else is a candidate for **aggregation, dimension trimming, or shorter retention**—the same *decision classes* buyers expect from adaptive-metrics stories, executed here with Elastic **downsampling** and **Streams**-style server policy.
2. **Hot vs cold** — High-volume generators (Kubernetes pod metrics, nginx access patterns, etc.) are where **downsampling** and **tiered retention** pay off first, while SLO-driving series stay hot at full resolution for incident and executive views.
3. **Why Elastic in evaluations** — Lead with **downsampling** plus **incident workflows** that prove which signals fire under stress, **one correlated store** for logs + metrics + traces, and **declared usage** (dashboards, SLOs, alerts) driving what stays hot. For **automated unused-metric recommendations**, describe a **custom** scheduled workflow (ES|QL + AI step + case) or **Streams** rules—same product surface, governance you own in code.

Optional — get a feel for **metric write volume** over the last few minutes (tune time range if empty):

```esql
TS metrics*
| WHERE @timestamp > NOW() - 15 MINUTES
| STATS metric_points = COUNT(*)
```

If you see a large number, that is the kind of volume finance cares about when you compare Elastic Serverless to “free” self-hosted scrapes.

---

## Explore #4 — APM / Services

1. In the **Elastic Serverless** tab → **Applications → Service inventory**
2. For **Retail Banking**, you should see the nine application services (for example **`payment-engine`**, **`claims-processor`**, **`mobile-gateway`**, **`member-portal`**, **`fraud-sentinel`**, **`policy-manager`**, **`auth-gateway`**, **`document-vault`**, **`quote-engine`**) plus shared infrastructure such as **`nginx-proxy`** and **`mysql-primary`** when the deployment emits traces for them.
3. Click any service to see latency, throughput, and error rate
4. Open a transaction to see the **distributed trace waterfall**

---

## Explore #5 — Infrastructure / Hosts

1. In the **Elastic Serverless** tab → **Observability → Infrastructure**
2. You should see **3 hosts** — one per simulated cloud provider. With the default card, names look like **`banking-aws-host-01`**, **`banking-gcp-host-01`**, **`banking-azure-host-01`**.
3. Click a host to see CPU, memory, disk, and network metrics

> **Note:** If hosts don't appear immediately, wait 1–2 minutes for the host metrics generator to send its first batch.

---

✅ **Ready to continue when** you've seen logs, traces, or metrics in Elastic Serverless and confirmed services are healthy.
