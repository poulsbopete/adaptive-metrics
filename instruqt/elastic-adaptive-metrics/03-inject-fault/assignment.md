---
slug: inject-fault
id: idjcheiijoey
type: challenge
title: Inject a Fault and Watch Elastic Detect It
teaser: >-
  Inject a multi-cloud fault, watch ES|QL alerts and the AI agent respond—then tie
  that RCA window to retention and server-side shaping (adaptive metrics in practice).
notes:
- type: text
  contents: |
    ## Lab 3 — Inject a Fault and Watch Elastic Detect It

    **By the end of this challenge you will:**

    - ✅ Trigger a realistic fault using the Demo App Chaos controller
    - ✅ Watch the error spike appear in Elastic's log stream within seconds
    - ✅ See an ES|QL alert rule fire within 30–60 seconds
    - ✅ Observe the AI agent begin its investigation automatically
    - ✅ Connect incident response to **why** hot retention and governed metrics matter for TCO

    **You have 20 fault channels to choose from** — each simulates a realistic incident across AWS, GCP, and Azure services. Pick any one and watch Elastic light up.
- type: text
  contents: |
    ## How Fault Detection Works

    Every fault channel is monitored by a dedicated **ES|QL alert rule** running on a 30-second schedule:

    ```
    FROM logs*
    | WHERE @timestamp > NOW() - 2 MINUTES
    | WHERE body.text : "MacAddressFlappingException"
    | STATS error_count = COUNT(*)
    | WHERE error_count > 5
    ```

    When errors exceed the threshold:
    1. The alert fires and appears in **Observability → Alerts**
    2. The alert triggers the **Significant Event Notification** workflow
    3. The workflow calls the **AI agent** with the error context
    4. The agent queries logs, correlates signals, and produces a root-cause analysis
- type: text
  contents: |
    ## Fault Cascade: Why Observability Is Hard

    A single fault channel doesn't just affect one service — it cascades:

    | Step | What happens |
    |------|-------------|
    | **1** | Primary service emits `ERROR` logs with a specific exception type |
    | **2** | Downstream services emit `WARN` — degraded upstream responses |
    | **3** | Trace spans show elevated latency at integration boundaries |
    | **4** | Host metrics spike on the affected cloud provider |

    This cascade across logs, metrics, and traces is what makes incidents hard to diagnose manually — and what makes Elastic's correlated view so powerful.
- type: text
  contents: |
    ## 20 Fault Channels — Pick One

    | Category | Cloud | Example Faults |
    |----------|-------|---------------|
    | **Network Core** | Azure | MAC flapping, BGP peer drop, spanning tree change |
    | **Security** | Azure | Firewall session exhaustion, SSL cert expiry |
    | **WiFi / Network Access** | GCP | AP disconnect storm, channel interference |
    | **Network Services** | Azure | DNS failure, DHCP lease storm |
    | **Commerce** | AWS | Bid latency spike, payment timeout, catalog sync failure |
    | **Manufacturing** | AWS | Print queue overflow, QC rejection spike |
    | **Logistics** | GCP | Label printer failure, warehouse scanner desync |
    | **Cloud Ops** | GCP | Orphaned resource alert, VPN tunnel flapping |

    Start with **Channel 12 — Auction Bid Latency Spike** for the clearest end-to-end demo.
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

Trigger a fault from the **Demo App**, then watch Elastic automatically investigate and create a case — no human intervention required.

---

## Step 1 — Inject a Fault

1. Open the **Demo App** tab. On your running deployment, click **Chaos** (opens the incident simulator).
2. Select any fault channel and click **Inject Fault**

> **Recommended:** Start with **Channel 12 — Auction Bid Latency Spike** for the clearest end-to-end demo.

While the fault propagates, run this query in **Elastic Serverless → Discover → ES|QL** to watch the error spike in real time:

```esql
FROM logs*
| WHERE @timestamp > NOW() - 15 MINUTES
| WHERE severity_text == "ERROR"
| STATS errors = COUNT(*) BY service.name
| SORT errors DESC
```

> **Tip:** Re-run this every 30 seconds after injecting the fault — you'll see the affected service's error count climb while all other services stay flat.

---

## Step 2 — Watch the Workflow Run

In the **Elastic Serverless** tab, go to **Observability → Workflows**.

Within 1–2 minutes of injecting the fault, the **Fanatics Collectibles Significant Event Notification** workflow will show a recent execution. Click it to see each step:

- **count_errors** — ES|QL query counting recent errors from the affected service
- **run_rca** — AI agent root-cause analysis
- **create_case** — Kibana case created with RCA findings

Click **View Full Conversation** to open the AI agent's complete chat thread — you can see exactly what it queried, what it found, and why it drew its conclusions. You can even type follow-up questions or ask the agent to take a remediation action.

---

## Step 3 — Review the Case

Go to **Observability → Cases** (or click **Cases** in the left nav).

A new case will appear automatically with:
- The fault name and affected service in the title
- The AI agent's root-cause analysis in the description
- Severity set to **High**

✅ **Ready to continue when** you can see a workflow execution and an auto-created case in Elastic Serverless.

---

## After the incident — retention, downsampling, and Streams

Most **agentic RCA** and war-room analysis happens in the **first hours to days** after a spike. That is the business case for **predictable retention**: keep rich resolution on series tied to **alerts, SLOs, and dashboards** (everything you touched in Challenges 1–2), and use **shorter hot windows or coarser rollups** for high-cardinality metrics that never appear in those surfaces.

**Elastic Streams** and server-side ingest shaping are how you encode that policy in one place—without shipping complex edge rules to every cluster. Pair that story with [Adaptive Metrics](https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/)–style positioning when you talk to finance: you are not “deleting observability,” you are **tiering cost** to the signals that actually drive incidents and customer outcomes.
