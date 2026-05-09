---
slug: explore-telemetry
id: 98kwdohjlsof
type: challenge
title: Explore Live OpenTelemetry Data
teaser: >-
  Navigate Elastic Serverless for logs, traces, and metrics—then map which
  signals are tied to dashboards and SLOs (declared usage) for adaptive metrics
  thinking.
notes:
- type: text
  contents: |
    ## Lab 2 — Explore Live OpenTelemetry Data

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

    **9 scenario microservices** (application logs + traces):
    Auction Engine · Card Printing · Payment Processing · Fan Engagement · Loyalty Rewards · Streaming CDN · Navigation · Fraud Detection · Fulfillment

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

    **Latency trend over time:**
    ```
    TS metrics*
    | WHERE @timestamp > NOW() - 30 MINUTES
    | EVAL minute = DATE_TRUNC(1 minute, @timestamp)
    | STATS avg_latency = AVG(auction.bid_latency_ms) BY minute
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

Now that your scenario is running, let's explore the data flowing into Elastic. Open the **Elastic Serverless** tab.

---

## What's Generating Telemetry

The platform runs several background generators simultaneously:

| Generator | What It Produces |
|-----------|-----------------|
| **9 scenario services** | Application logs, traces, errors |
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
- `service.name`: `auction-engine`, `card-printing-system`, `digital-marketplace`, `packaging-fulfillment`, `cloud-inventory-scanner`, `nginx-proxy`, `mysql-primary`, and more
- `severity_text`: `INFO`, `WARN`, `ERROR`
- `body.text` contains the raw log message and error type

---

## Explore #2 — ES|QL Time Series Queries

In the **Elastic Serverless** tab → **Discover** → **ES|QL** mode, try these queries against the live metrics stream.

### Auction health at a glance
```esql
TS metrics*
| WHERE @timestamp > NOW() - 15 MINUTES
| EVAL minute = DATE_TRUNC(1 minute, @timestamp)
| STATS
    active_auctions = AVG(auction.active_auctions),
    bid_latency_ms  = AVG(auction.bid_latency_ms),
    bids_per_min    = AVG(auction.bids_per_min),
    websocket_conns = AVG(auction.websocket_connections)
  BY minute
| SORT minute DESC
```

### Spot a latency spike before users notice
```esql
TS metrics*
| WHERE @timestamp > NOW() - 30 MINUTES
| EVAL minute = DATE_TRUNC(1 minute, @timestamp)
| STATS avg_latency = AVG(auction.bid_latency_ms) BY minute
| EVAL status = CASE(
    avg_latency > 45, "🔴 CRITICAL",
    avg_latency > 30, "🟡 DEGRADED",
    "🟢 HEALTHY"
  )
| SORT minute DESC
```

### Card printing throughput vs queue depth
```esql
TS metrics*
| WHERE @timestamp > NOW() - 20 MINUTES
| EVAL minute = DATE_TRUNC(1 minute, @timestamp)
| STATS
    queue_depth    = AVG(card_printing.queue_depth),
    throughput     = AVG(card_printing.throughput),
    substrate_temp = AVG(card_printing.substrate_temp)
  BY minute
| EVAL backlog_ratio = ROUND(queue_depth / throughput, 2)
| SORT minute DESC
```

### Multi-cloud compliance drift
```esql
TS metrics*
| WHERE @timestamp > NOW() - 30 MINUTES
| EVAL bucket5m = DATE_TRUNC(5 minutes, @timestamp)
| STATS
    aws_compliance   = AVG(cloud_inventory.aws.compliance_pct),
    gcp_compliance   = AVG(cloud_inventory.gcp.compliance_pct),
    azure_compliance = AVG(cloud_inventory.azure.compliance_pct)
  BY bucket5m
| EVAL lowest = LEAST(aws_compliance, gcp_compliance, azure_compliance)
| EVAL at_risk_cloud = CASE(
    lowest == aws_compliance, "AWS",
    lowest == gcp_compliance, "GCP",
    "Azure"
  )
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

The deployer creates **two** Kibana saved dashboards for **every** scenario. Open the **Elastic Serverless** tab → **Dashboards** → search by your **scenario name** (e.g. *Fanatics Collectibles*).

### Systems Operations

Saved object id ends in **`-exec-dashboard`**. This is the engineering view: service health, RED-style signals, logs, traces, and infrastructure context tied to the running demo.

### Executive (business KPIs)

Saved object id ends in **`-business-exec-dashboard`**. This is a **synthetic executive / revenue narrative** built from the same live OTLP metric stream as the rest of the demo — not a separate data source.

**How the data is produced**

- Each scenario designates **one** microservice to emit all `business.*` gauges each telemetry cycle (so KPIs are not duplicated across services). For **Fanatics Collectibles**, that service is **`digital-marketplace`**; other verticals follow the same pattern with their own emitter service.
- Values are **real-time generated** for the lab (plausible ranges), then shipped like any other metric so you can correlate dips with chaos, latency, or errors on **Systems Operations**.

**What to scan on the dashboard** (grouped the way leadership lenses usually run the business)

| Lens | Examples (metric themes) |
|------|---------------------------|
| **Audience & engagement** | Live concurrent viewers, video minutes, page views, app sessions, content completion, push CTR, newsletter opens, social clip shares |
| **Monetization & commerce** | Ad revenue, programmatic fill rate, betting handle / hold / gross win, subscription MRR, merch GMV, live-event ticketing, active fantasy entries |
| **Partners & B2B** | Sponsorship revenue, sponsored inventory, API / data-partner revenue |
| **Health & retention proxies** | Premium-tier ARPU, loyalty points redeemed, churn-risk index, satisfaction proxy (NPS-style score) |

Use **Executive** for stakeholder-style storytelling; use **Systems Operations** when you need to prove *why* a KPI moved (drill to services, logs, and traces).

---

## Adaptive metrics — declared usage and tiers (same sandbox)

You already have the **same sandbox** as a full observability workshop. Use it to practice **governance**:

1. **Declared usage** — Open **Dashboards** and note which services and metric charts your scenario ships. Those charts (and the **SLOs** under Observability) are the usage signal you would import from Kibana in a real “adaptive metrics” workflow—not every raw series in the index.
2. **Hot vs cold** — High-volume generators (for example Kubernetes pod metrics or nginx access patterns) are exactly where **tiered retention** and **downsampling** pay off, while SLO-driving series stay hot longer.
3. **Positioning** — Competitors market unused-series discovery as [Adaptive Metrics](https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/). Elastic’s answer is the same *classification* story plus **downsampling** and **Streams** for **server-side** policy without maintaining brittle edge-only rules.

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
2. You should see **7 services** — the 5 application services plus `nginx-proxy` and `mysql-primary`
   > The remaining 2 network/infrastructure services (`wifi-controller`, `network-controller`, `firewall-gateway`, `dns-dhcp-service`) emit logs only — no traces — so they won't appear here
3. Click any service to see latency, throughput, and error rate
4. Open a transaction to see the **distributed trace waterfall**

---

## Explore #5 — Infrastructure / Hosts

1. In the **Elastic Serverless** tab → **Observability → Infrastructure**
2. You should see 3 hosts — one per cloud provider:
   - `fanatics-aws-host-01`
   - `fanatics-gcp-host-01`
   - `fanatics-azure-host-01`
3. Click a host to see CPU, memory, disk, and network metrics

> **Note:** If hosts don't appear immediately, wait 1–2 minutes for the host metrics generator to send its first batch.

---

✅ **Ready to continue when** you've seen logs, traces, or metrics in Elastic Serverless and confirmed services are healthy.
