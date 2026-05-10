# Metric governance loop: Workflows + Streams + AI (blueprint)

This document is the **implementation guide** for a **Kibana Observability Workflow** on a **short schedule** (for example every five minutes) that **inspects Streams**, asks an **AI assistant** for safe changes (sub-routes, retention, or drops), and **applies** updates via the **Streams API**—while **Elastic Agent** continues to ship telemetry under **Fleet** policy.

**Start from code:** import [`workflows/kibana/metric-governance-retail-banking-starter.yaml`](../../../workflows/kibana/metric-governance-retail-banking-starter.yaml) (scheduled **`kibana.streams.list`** + **`elasticsearch.esql.query`** + **Observability Case**), then extend with AI steps and `kibana.request` / `PUT` as below.

> **Scope:** Validate step types and request bodies against **your** Serverless / Kibana minor version before production use. The Streams HTTP API and **`kibana.streams.*`** steps are still evolving; see Elastic’s technical preview notes in the [Streams API group](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-streams) and [Streams action steps](https://www.elastic.co/docs/explore-analyze/workflows/steps/streams).

---

## Lab: high-cardinality “noisy” metrics (Instruqt)

The track VM may start **`noisy-metrics-otlp`** (`instruqt/elastic-adaptive-metrics/track_scripts/noisy_otlp_metrics.py`), which sends OTLP counters to the project’s **Managed OTLP endpoint** (not the Elasticsearch URL) with **`service.name` = `noisy-governance-shipper`** and **`data_stream.dataset` = `governance.noisy`**. Use **Observability → Streams** and workflows to attach **shorter retention** or **child routes** to that dataset while keeping core **`payment-engine`**-class streams on **longer retention** (declared-usage signals). If the service did not start, set **`MOTLP_URL`** on the **es3-api** host from **Add data → OpenTelemetry**, or set **`DISABLE_NOISY_METRICS_SHIPPER=1`** to turn it off.

---

## Metric governance dashboard (Kibana)

Use [`dashboards/metric-governance-retail-banking-as-code.json`](../../../dashboards/metric-governance-retail-banking-as-code.json) as the **`kibana_create_dashboard`** payload (Observability MCP) when your **MCP `KIBANA_URL`** is the same project you want to update. **Instruqt lab** hosts often use a different URL than MCP; for those, use [`dashboards/instruqt-metric-governance-dashboard.json`](../../../dashboards/instruqt-metric-governance-dashboard.json) with **`scripts/push_governance_dashboard.py`** (`POST /api/dashboards`, **`Elastic-Api-Version`** must be a **YYYY-MM-DD** string — default **2023-10-31**, override with **`KIBANA_DASHBOARDS_API_VERSION`**) — KPI **metric** tiles, **gauge**, **area**/**bar** charts for **Retail Banking — Streams savings & metric governance (TCO)**.

---

## Example: Kubernetes metrics — shorter retention (Streams)

**What you are governing:** Dashboards such as **[OTEL][Metrics Kubernetes] Cluster Overview** read OTel **metrics** stored under streams whose names usually include **`metrics-kubernetes.*`** and **`metrics-k8sclusterreceiver.*`** (for example **`metrics-kubernetes.container.otel-default`**, **`metrics-kubernetes.node.otel-default`**, **`metrics-k8sclusterreceiver.otel-default`**). Names can vary slightly by integration and namespace; use **Observability → Streams** and search **`kubernetes`** or **`k8s`** to match document volume to the UI.

**Declared usage:** That Kubernetes dashboard (and any SLOs or alert rules you build on the same series) is your **“in use”** signal. Shortening retention **shrinks how far back** those panels can query—reasonable for noisy infra metrics in a lab; in production it is a conscious tradeoff with SRE and capacity owners.

### Option A — Kibana UI (fastest lab path)

1. Open **Observability → Streams** and select the stream that corresponds to the metric family you want to tune (container/node/pod vs cluster-receiver streams often split this way).
2. Open the **Retention** tab → **Edit data retention**. If the stream **inherits** from a template or parent, turn **inherit** off when you intentionally want a **shorter** override for this lab.
3. Choose **Custom period** and set a shorter retain-and-delete horizon (for example **7 days** on a non-production project instead of **Indefinite**).
4. Save and confirm the **Data lifecycle** / storage summary on the same tab.

Details: [Manage data retention for Streams](https://www.elastic.co/docs/solutions/observability/streams/management/retention).

### Option B — Workflow automation (same pattern as the rest of this doc)

1. **`kibana.streams.list`** (or **`kibana.request`** `GET /api/streams`) and pick the target **`name`** (URL-encode if needed when calling HTTP).
2. **`kibana.streams.get`** with `with.name: "<stream-name>"` to retrieve the **authoritative** JSON.
3. Merge only the **retention / lifecycle** fields the UI would have changed—then **`kibana.request`** `PUT /api/streams/{name}` with header **`kbn-xsrf: true`** and a principal that has **`manage_stream`**. The API expects the **full** merged `stream` object for that path ([Create or update a stream](https://www.elastic.co/docs/api/doc/kibana/operation/operation-put-streams-name)); pair with **`waitForInput`** or a **Case** step before apply.
4. Optional next lever after retention: **downsampling** when your **Streams** retention UI exposes it for that stream ([Downsampling in Streams retention](https://www.elastic.co/docs/solutions/observability/streams/management/retention#streams-retention-downsampling)). On **Serverless**, express cost discipline through **Streams policy and processing**, not self-managed index **data tiers**.

**Volume check (ES|QL)** before you change policy:

```esql
FROM metrics-kubernetes*
| WHERE @timestamp > NOW() - 30 minutes
| STATS docs = COUNT(*)
```

```esql
FROM metrics-k8s*
| WHERE @timestamp > NOW() - 30 minutes
| STATS docs = COUNT(*)
```

Use the counts in a **Case** or **`cases.addComment`** so approvers see *why* you picked that stream.

---

## Roles: who does what

| Component | Role |
|-------------|------|
| **Kibana Workflow** | Orchestration only: schedule, call Kibana/Elasticsearch APIs, call AI connectors, open cases for approval. It does **not** run on Elastic Agent hosts. |
| **Elastic Agent** | Ships logs/metrics/traces per **Fleet** integration policy. Changing **Streams** changes how **ingested** documents are **routed and processed** in Kibana/Elasticsearch; changing **what** the agent collects is a **Fleet policy** change (separate API path). |
| **Streams (wired)** | Kibana-managed routing: documents can be **routed to child streams** by field conditions ([Streams overview](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-streams)). This is the natural place to model “sub-streams.” |
| **Observability AI Assistant / connector** | Produces **recommendations** (text + structured JSON you define in the prompt) from metrics inventory + ES|QL + dashboard/SLO context. |
| **Human gate (recommended)** | Workflow creates a **Case** or posts to Slack with the proposed `PUT` body; a human approves before the final `kibana.request` step applies changes. |

---

## APIs you will call from the workflow

Use **`kibana.streams.list`** / **`kibana.streams.get`** ([Streams action steps](https://www.elastic.co/docs/explore-analyze/workflows/steps/streams)) when the editor supports them; otherwise use **`kibana.request`** with `method: GET` and `path: /api/streams` (same privilege model). For updates, **`kibana.request`** `PUT /api/streams/{name}` matches the [Create or update a stream](https://www.elastic.co/docs/api/doc/kibana/operation/operation-put-streams-name) contract until a dedicated Streams update step exists.

| Action | HTTP | Doc |
|--------|------|-----|
| List streams | `GET /api/streams` | [Get stream list](https://www.elastic.co/docs/api/doc/kibana/operation/operation-get-streams) |
| Create / update stream | `PUT /api/streams/{name}` | [Create or update a stream](https://www.elastic.co/docs/api/doc/kibana/operation/operation-put-streams-name) |

Classic streams **cannot** be created through this API (only updated). Prefer **wired** streams when you need Kibana-managed **child routes**.

Workflow step reference: [Kibana workflow steps](https://www.elastic.co/docs/explore-analyze/workflows/steps/kibana) · Observability use cases: [Workflows](https://www.elastic.co/docs/explore-analyze/workflows/use-cases/observability).

---

## Suggested workflow graph (every 5 minutes)

```mermaid
flowchart TD
  S[Scheduled trigger 5m] --> L[List streams kibana.streams.list or GET /api/streams]
  L --> F{Filter: wired parent candidates}
  F --> M[Metrics: ES|QL volume + cardinality snapshot]
  M --> D[Declared usage: dashboards / SLOs / alert refs]
  D --> A[AI step: propose child streams + retention + drops]
  A --> G{Approval required?}
  G -->|yes| C[Create Case with diff JSON]
  G -->|no dry-run| X[Log only / Slack preview]
  C --> P[PUT /api/streams/child or update parent wired rules]
  X --> P
  P --> R[Optional: Fleet policy tweak for high-card agents]
```

1. **Scheduled trigger** — for example `every: "5m"` ([Scheduled triggers](https://www.elastic.co/docs/explore-analyze/workflows/triggers/scheduled-triggers)).
2. **List + filter** — Use **`kibana.streams.list`** output or `GET /api/streams` via **`kibana.request`**. Select **wired** parents that are allowed to receive **child** routes (your naming convention, e.g. `otel-metrics-*`).
3. **Context pack** — Run **ES|QL** with **`elasticsearch.esql.query`** for top-N noisy metric families; attach **dashboard/SLO** identifiers the way you teach in the lab (**declared usage**).
4. **AI step** — Prompt the model to output **only** a JSON patch: suggested `child` stream names, routing predicates, retention intent, and explicit **“no change”** when uncertain. Enforce JSON schema validation in a small **inline script** step if your workflow product supports it.
5. **Governance gate** — Default to **Case** + `@mention` SRE. Auto-apply only after the Case transitions to approved, or only in non-prod.
6. **Apply** — `PUT /api/streams/{name}` with the body shape required by your version (see API docs for `stream`, `rules`, `queries`, `dashboards` fields).
7. **Elastic Agent (optional branch)** — If the AI recommends **reducing collectors** (fewer datasets), use **Fleet API** to adjust the relevant integration policy **after** human approval—not from the same unguarded loop as Streams edits.

---

## Heuristic “% saved” in the starter Case (demo)

The repo workflow `workflows/kibana/metric-governance-retail-banking-starter.yaml` adds derived fields on the ES|QL snapshot row:

| Field | Meaning |
|--------|--------|
| **points_governance_lab** | Documents with **`service.name == "noisy-governance-shipper"`** (Instruqt **governance-lab** OTLP shipper when enabled). |
| **metric_points_retail_model** | `metric_points - points_governance_lab` — retail-banking **denominator** for eligible % (lab traffic does not dilute the retail share). |
| **streams_eligible_pct** | `100 * (metric_points_retail_model - points_core_services) / metric_points_retail_model`, where `points_core_services` counts the nine core retail-banking `service.name` values. **Eligible** = non-core **within the retail slice** only. |
| **modeled_policy_savings_pct** | `ROUND(streams_eligible_pct * 0.35, 2)` — **retail headline** (tune `0.35`). |
| **streams_governance_lab_pct** | Lab docs ÷ **all** metric docs × 100 (lab’s share of total ingest). |
| **modeled_governance_lab_savings_pct** | `ROUND(streams_governance_lab_pct * 0.35, 2)` — same reclaim factor on **governance-only** lab volume. |
| **points_in_savings_envelope** | Modeled reclaim **document count** proxy (retail modeled % on retail model slice + **0.35 ×** raw lab docs). |
| **estimated_monthly_observe_bill_usd** | **Observe $ proxy** — all metric docs × **$/M points/month** × `periods_per_month` (pedagogical). |
| **estimated_monthly_reclaim_usd** | **Reclaim $ proxy** — `points_in_savings_envelope` × same rate. |
| **pct_savings_of_estimated_observe_bill** | **% of proxy observe bill** saved (**reclaim ÷ observe × 100**, zero-guarded). |

Replace the service allowlist and the `0.35` factor with **your** governance model before production.

**Workshop UX:** mirror **`modeled_policy_savings_pct`** on the **Executive** dashboard with the same ES|QL in a **Lens** metric (Challenge 2), then use **Observability AI Assistant** on the Case for **$/month** language so the savings story is obvious to finance.

---

## Prompt sketch (AI step)

Ask the assistant to:

- Prefer **child wired streams** + **processing steps** over hard deletes.
- Never drop series that appear in the attached **SLO** or **alert rule** list.
- Prefer **shorter retention**, **child routes**, or **rollup/downsample** language that maps to **Observability Streams** and stream processing (not self-managed **ILM / data-tier** knobs on Serverless).
- Return `{"actions":[]}` when confidence is low.

---

## Starter YAML: gated `ai.prompt` for Streams (retention / drops)

The repo file **`workflows/kibana/metric-governance-retail-banking-starter.yaml`** includes an **`if`** step named **`gated_ai_streams_recommendations`** whose default **`condition`** is **`${{ 1 == 2 }}`** (always false) so the workflow **imports and runs** without a GenAI connector. After you configure a **default GenAI connector** (or set **`connector-id`** on the **`ai.prompt`** step), change that condition to **`${{ true }}`**.

When enabled, the branch runs **`ai.prompt`** with a **JSON Schema** so the model returns **`summary`** plus **`actions[]`** (`streamName`, `action`, optional **`retentionDaysSuggested`**, **`dropOrRouteHint`**, **`rationale`**, **`estimatedSavingsBand`**), then **`cases.addComment`** posts that object to the same governance Case.

### Automation levels (Workflows + Agent Builder)

| Level | What runs automatically | Human / tooling |
|------|-------------------------|-----------------|
| **A — Snapshot** | Schedule → **`kibana.streams.list`** + **`elasticsearch.esql.query`** + **Case** + ES|QL comment | Leadership / AI Assistant for $/month narrative |
| **B — Structured plan** | Level **A** + gated **`ai.prompt`** (or **`ai.agent`** below) | Review JSON on the Case; no Streams **PUT** in the starter |
| **C — HITL fetch** | Level **B** + **`waitForInput`** → conditional **`kibana.streams.get`** → Case comment with **live** stream JSON | Reviewer submits the form in the execution UI (or [`POST .../workflowExecutions/{id}/resume`](https://www.elastic.co/docs/explore-analyze/workflows/authoring-techniques/human-in-the-loop)); ops merge + **PUT** outside the YAML or add a gated **`kibana.request`** after merge tooling exists |
| **D — Full apply** | Merge AI deltas with **`kibana.streams.get`** output, then **`kibana.request`** `PUT` | Only after change management: dedicated agent/workflow, dry-runs, audit index |

**Agent Builder (`ai.agent`):** Build an Observability FinOps agent (tools: Streams read, ES|QL, optional Cases) in **[Elastic Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder)**, note its **`agent-id`**, then replace the **`ai_streams_plan`** step with an **`ai.agent`** step: top-level **`agent-id`**, **`connector-id`** (or **`inference-id`**), optional **`create-conversation: true`**, and **`with.message`** / optional **`with.schema`** per [AI steps — `ai.agent`](https://www.elastic.co/docs/explore-analyze/workflows/steps/ai-steps#ai-agent). The starter keeps **`ai.prompt`** so imports work without a published agent.

**Scheduling vs HITL:** A **short schedule** plus **`waitForInput`** creates **one paused execution per run** until someone resumes—use **`settings.timeout`** or a **manual / alert** trigger for approval-heavy paths ([Human-in-the-loop workflows](https://www.elastic.co/docs/explore-analyze/workflows/authoring-techniques/human-in-the-loop)).

**Applying changes to Elasticsearch/Kibana Streams** is intentionally **not** fully automated in the starter: there is still no first-class **`kibana.streams.update`** step ([Streams action steps](https://www.elastic.co/docs/explore-analyze/workflows/steps/streams)), and **`PUT /api/streams/{name}`** requires a **full merged body** from **`kibana.streams.get`**. Level **C** automates **fetch-after-approval** onto the Case; treat **PUT** as a separate, audited step once you have merge logic or an agent that outputs a validated full body.

---

## Safety checklist

- Start in a **lab project** with synthetic traffic only.
- **Dry-run** mode for the first week: AI + Case, no `PUT`.
- Separate **API keys** per environment; rotate on any workflow change.
- Log every `PUT` body to an **audit index** for forensics.

---

## Relation to this Instruqt track

The track teaches **declared usage** and **Streams** as concepts, then **this blueprint + starter YAML** are the build: import **`workflows/kibana/metric-governance-retail-banking-starter.yaml`**, validate in a lab project, enable the gated **`ai.prompt`** branch when a connector exists, add **`kibana.request`** `PUT` only after **`kibana.streams.get`** merge and approval, and version the YAML beside this repo. To push the workflow to **Elastic Cloud Serverless** from a machine with credentials, run **`./scripts/push-to-serverless.sh`** (see `README.md` — `KIBANA_URL` + `ES_API_KEY`).

**Cursor / MCP side:** `workflows/retail-banking-streams-governance-dryrun.yaml` is an optional **MCP** `run_workflow` helper (agent calls `discover_o11y_data` + ES|QL) for dry runs from the IDE; it does **not** register a workflow in Kibana. For the Kibana UI list, use **Create a new workflow** or `POST /api/workflows/workflow` (see `.cursor/skills/kibana-observability-workflows-api/SKILL.md`).
