---
slug: inject-fault
id: idjcheiijoey
type: challenge
title: Inject a Fault and Watch Elastic Detect It
teaser: 'Fault → alert → workflow → case: see the signals that define **declared usage**,
  then tie RCA windows to downsampling and retention on Elastic.'
notes:
- type: text
  contents: |
    ## Lab 3 — Inject a Fault and Watch Elastic Detect It

    **Workshop payoff:** The **Significant Event Notification** workflow is a concrete **Elastic Workflow**: it shows which logs, metrics, and traces participate when something breaks—the same operational surface you would *never* silently drop in a governance program. That is **declared usage under stress**—distinct from a separate “metric catalog cleanup” workflow, which you would add as **custom** automation on the same platform.

    **By the end of this challenge you will:**

    - ✅ Trigger a realistic fault using the Demo App Chaos controller
    - ✅ Watch the error spike appear in Elastic's log stream within seconds
    - ✅ See an ES|QL alert rule fire within 30–60 seconds
    - ✅ Observe the AI agent begin its investigation automatically
    - ✅ Connect incident response to **why** hot retention and governed metrics matter for TCO

    **You have 20 fault channels to choose from** — for **Retail Banking** they map to **digital banking, payments, claims, policy, fraud, identity, documents, and core infra** across AWS, GCP, and Azure. Pick any channel and watch Elastic light up.
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
    ## 20 Fault Channels — Pick One (Retail Banking)

    | Category | Cloud | Example channels |
    |----------|-------|------------------|
    | **Digital banking** | AWS | Mobile app API timeout, mobile deposit failure, push notification storm |
    | **Payments & treasury** | AWS | ACH direct deposit delay, bill pay failure, wire OFAC block, debit auth failure |
    | **Claims & loss** | AWS | FNOL intake backlog, photo damage estimate timeout, claims disbursement failure |
    | **Policy & underwriting** | AWS | Policy renewal batch failure, rules engine error, VA loan rate lock failure |
    | **Identity & access** | Azure | Biometric auth degradation, MFA delivery failure |
    | **Fraud & member channel** | GCP | Fraud false-positive surge, member session timeout cascade |
    | **Documents & data** | Azure | Document upload failure, DB replication lag, certificate expiration cascade |

    **Recommended:** **Channel 4 — ACH Direct Deposit Delay** (payments + member impact) or **Channel 6 — Wire Transfer OFAC Block** (treasury / compliance story). **Channel 1 — Mobile App API Timeout** is also a strong **digital banking** demo.
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

> **Recommended:** Start with **Channel 4 — ACH Direct Deposit Delay** or **Channel 6 — Wire Transfer OFAC Block** for a clear **retail banking** payments story; **Channel 1 — Mobile App API Timeout** highlights the **mobile / API** path.

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

Within 1–2 minutes of injecting the fault, the **Significant Event Notification** workflow for **your running scenario** will show a recent execution (the workflow title includes the scenario name). Click it to see each step:

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

Most **agentic RCA** and war-room analysis happens in the **first hours to days** after a spike. That is the business case for **predictable retention**: keep rich resolution on series tied to **alerts, SLOs, dashboards, and workflows** (everything you touched in Challenges 1–3—the **declared usage** surface), and use **shorter hot windows**, **coarser rollups**, or **downsampling** for high-cardinality metrics that never appear in those surfaces. **Elastic downsampling** plus **one correlated store and workflows** is how you answer finance and architecture reviewers without splitting observability across silos.

**Elastic Streams** and server-side ingest shaping are how you encode that policy in one place—without shipping complex edge rules to every cluster. When you talk to finance or architecture reviewers at **large banks and insurers**, you are not “deleting observability,” you are **tiering cost** to the signals that actually drive incidents and customer outcomes—**workflows** make that list objective, not guessed.
