---
slug: connect-and-deploy
id: zcj2ykfryvmc
type: challenge
title: Connect to Elastic Cloud & Deploy
teaser: Deploy the demo, then connect **declared usage** (dashboards, SLOs, alerts,
  workflows) to **downsampling** and **retention** for governed TCO on Elastic.
notes:
- type: text
  contents: |
    ## Lab 1 — Connect to Elastic Cloud & Deploy

    **Workshop through-line:** Many teams need to find **unused** time series and decide on **aggregation, dimension trims, or policy-driven drops**—without surprise data loss. On Elastic you tell that **TCO / cardinality** story with **downsampling**, **Kibana Workflows** (for **incidents and SLO operations**), and **server-side shaping** (for example **Elastic Streams**). This lab’s **pre-provisioned workflows** are for **alerts, remediation, and SLO hygiene**—they show **declared usage** when things break; **metric inventory and drop/aggregate suggestions** are something you layer on with **ES|QL**, **Streams**, and **optional workflows you author** (see Challenge 2).

    **What's happening right now:**
    Your Elastic Cloud Serverless Observability project is being provisioned and the **Elastic Observability Demo Platform** is being configured with your credentials.

    **By the end of this challenge you will:**

    - ✅ Confirm **Retail Banking Platform** is deployed and sending telemetry (or the scenario you switched to in the Demo App)
    - ✅ Open your Elastic Serverless project — no login required
    - ✅ Verify logs, metrics, and traces are flowing from 9 microservices
    - ✅ Review the auto-provisioned AI agent, alert rules, and workflows
    - ✅ Understand how **dashboards, SLOs, alerts, and workflows** become *declared usage* for metrics when you optimize cost later

    *Setup takes 3–4 minutes. Grab a coffee — it'll be ready soon.*
- type: text
  contents: |
    ## Your Lab Environment

    **Two tabs, everything you need:**

    | Tab | What it is |
    |-----|-----------|
    | **Demo App** | Control panel — view service health, manage deployments, inject faults |
    | **Elastic Serverless** | Your Observability project — pre-logged in, data already flowing |

    **Default for this track:** the sandbox auto-launches **`banking`** — **Retail Banking Platform** (digital banking, **payments** (ACH, wires, bill pay), **claims**, **policy**, **fraud**, and **document** flows). That default fits **regulated retail banking and member-services** workshops; you can still **Stop & Teardown** in the Demo App and pick another card, or set `DEMO_SCENARIO_ID` on the `es3-api` VM for a different auto-launch.

    **Retail Banking runs nine instrumented microservices across three clouds**, for example **`mobile-gateway`**, **`payment-engine`**, **`claims-processor`**, **`policy-manager`**, **`fraud-sentinel`**, **`member-portal`**, **`auth-gateway`**, **`document-vault`**, and **`quote-engine`** (plus shared infra such as nginx and MySQL in the generators).

    Every service emits **real OpenTelemetry** logs, metrics, and traces — no synthetic data.
- type: text
  contents: |
    ## What Was Auto-Deployed

    When the lab started, the setup script provisioned your full observability stack automatically:

    | Resource | Details |
    |----------|---------|
    | **Alert rules** | 20 ES\|QL rules — one per fault channel, 30s interval |
    | **AI agent** | Investigation tools + system prompt |
    | **Workflows** | Alert → investigate → create case → remediate |
    | **Dashboards** | Systems Operations + Executive (leadership KPIs) per scenario + OTel signal dashboards |
    | **Data views** | `logs.otel`, `metrics-*`, `traces-*` |

    This is the same stack you'd deploy in production — configured in code, repeatable, version-controlled.
- type: text
  contents: |
    ## Key Concepts: Elastic Serverless + OpenTelemetry

    **Elastic Serverless** scales compute and storage independently. No cluster management, no shard tuning — just ingest and query.

    **OpenTelemetry (OTel)** is the CNCF standard for vendor-neutral instrumentation. Elastic is a Platinum member and natively ingests OTLP — no Collector required.

    **ES|QL** is Elastic's pipe-based query language, purpose-built for telemetry at scale:

    ```
    FROM logs*
    | WHERE severity_text == "ERROR"
    | STATS errors = COUNT(*) BY service.name
    | SORT errors DESC
    ```

    **AI Workflows** connect alert detection to investigation to remediation — all without human intervention.
- type: text
  contents: "## While You Wait — Play O11y Survivors! \U0001F3AE\n\nSetup takes a
    few minutes. Survive the anomaly storm while Elastic provisions your environment:\n\n<iframe
    src=\"https://poulsbopete.github.io/Vampire-Clone/\" width=\"100%\" height=\"800\"
    frameborder=\"0\" allowfullscreen style=\"border-radius:8px;display:block;\"></iframe>\n"
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

Everything was **automatically provisioned** when this lab started — your Elastic Cloud project is live, the **Retail Banking** stack is sending telemetry (unless you changed the scenario), and the AI observability stack is configured. Nothing to set up.

---

## TCO, adaptive metrics, and “declared usage”

**Low-cost metrics-only** stacks often win a spreadsheet line item until **cardinality, retention, and operational load** show up. **SaaS observability suites** can win feature demos until **custom metrics and tag cardinality** drive invoice growth. Elastic answers the same *buyer problem* with a different *architecture*: **downsampling** for metrics at scale plus **Kibana Workflows** and **server-side shaping** (for example **Elastic Streams**) so policy is enforceable where the data lives—and **logs, traces, metrics, and security** stay on **one** platform for **financial services** and other regulated buyers.

For the rest of this track, treat everything the deployer created as **declared usage**: if a metric appears on a **Systems Operations** or **Executive** dashboard, in an **SLO**, in an **ES|QL alert rule**, or in a **workflow**, it is a first-class signal you would protect with longer retention or finer resolution. Everything else is a candidate for **shorter hot tiers, coarser rollups, downsampling, or human-approved policy**—not silent deletion.

---

## Explore the Demo App

Open the **Demo App** tab: a **Retail Banking** run should already be active; if not, launch **Retail Banking Platform** from the card. Use the banner on an active run for **Systems Operations** / **Executive** Kibana links and the **Chaos** button (fault injection opens from there — no separate browser tab needed).

---

## Explore Elastic Serverless

Click the **Elastic Serverless** tab — you're already logged in. Navigate to:

- **Discover → ES|QL** — query live logs from retail-banking services (`payment-engine`, `claims-processor`, `mobile-gateway`, …)
- **Applications → Service inventory** — distributed traces from the instrumented application tier
- **Observability → Infrastructure** — simulated hosts per cloud (for banking, names look like `banking-aws-host-01`, `banking-gcp-host-01`, `banking-azure-host-01`)
- **Observability → SLOs** — auto-created SLOs tied to the running scenario
- **Observability → Workflows** — pre-configured AI response workflows for your deployment

> **Tip:** Set the time range to **Last 15 minutes** to see the freshest data.

---

## What Was Auto-Deployed

| Resource | Details |
|----------|---------|
| Alert rules | 20 ES\|QL rules — one per fault channel, 30s interval |
| AI agent | Investigation tools + system prompt |
| Workflows | Alert → investigate → create case → remediate |
| Dashboards | Systems Operations + Executive (all scenarios) + OTel signal dashboards |
| SLOs | Auto-created SLOs for your running scenario |
| Data views | `logs.otel`, `logs.otel.*`, `metrics-*` |

✅ **You're ready for the next challenge when** you can see logs, services, or SLOs in the Elastic Serverless tab.
