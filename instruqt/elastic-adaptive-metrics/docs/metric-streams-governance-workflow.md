# Metric governance loop: Workflows + Streams + AI (blueprint)

This document is the **implementation guide** for a **Kibana Observability Workflow** on a **short schedule** (for example every five minutes) that **inspects Streams**, asks an **AI assistant** for safe changes (sub-routes, retention, or drops), and **applies** updates via the **Streams API**—while **Elastic Agent** continues to ship telemetry under **Fleet** policy.

**Start from code:** import [`workflows/kibana/metric-governance-retail-banking-starter.yaml`](../../../workflows/kibana/metric-governance-retail-banking-starter.yaml) (scheduled **`kibana.streams.list`** + **`elasticsearch.esql.query`** + **Observability Case**), then extend with AI steps and `kibana.request` / `PUT` as below.

> **Scope:** Validate step types and request bodies against **your** Serverless / Kibana minor version before production use. The Streams HTTP API and **`kibana.streams.*`** steps are still evolving; see Elastic’s technical preview notes in the [Streams API group](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-streams) and [Streams action steps](https://www.elastic.co/docs/explore-analyze/workflows/steps/streams).

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

The repo workflow `workflows/kibana/metric-governance-retail-banking-starter.yaml` adds two derived fields on the ES|QL snapshot row:

| Field | Meaning |
|--------|--------|
| **streams_eligible_pct** | `100 * (metric_points - points_core_services) / metric_points`, where `points_core_services` counts documents whose `service.name` is one of the nine retail-banking app services. This is a **proxy for volume eligible** for Streams child routes, coarser rollups, or shorter hot retention—not a guarantee every point should be dropped. |
| **modeled_policy_savings_pct** | `ROUND(streams_eligible_pct * 0.35, 2)` — an **illustrative** fraction of that eligible share (tune `0.35`) until you connect real downsampling factors and **declared usage** from SLOs, dashboards, and alert rules instead of the fixed `IN (...)` list. |

Replace the service allowlist and the `0.35` factor with **your** governance model before production.

**Workshop UX:** mirror **`modeled_policy_savings_pct`** on the **Executive** dashboard with the same ES|QL in a **Lens** metric (Challenge 2), then use **Observability AI Assistant** on the Case for **$/month** language so the savings story is obvious to finance.

---

## Prompt sketch (AI step)

Ask the assistant to:

- Prefer **child wired streams** + **processing steps** over hard deletes.
- Never drop series that appear in the attached **SLO** or **alert rule** list.
- Prefer **shorter hot retention** or **rollup/downsample** language that maps to your Elasticsearch **ILM** or stream processing capabilities.
- Return `{"actions":[]}` when confidence is low.

---

## Safety checklist

- Start in a **lab project** with synthetic traffic only.
- **Dry-run** mode for the first week: AI + Case, no `PUT`.
- Separate **API keys** per environment; rotate on any workflow change.
- Log every `PUT` body to an **audit index** for forensics.

---

## Relation to this Instruqt track

The track teaches **declared usage** and **Streams** as concepts, then **this blueprint + starter YAML** are the build: import **`workflows/kibana/metric-governance-retail-banking-starter.yaml`**, validate in a lab project, add AI + `PUT` when ready, and version the YAML beside this repo.

**Cursor / MCP side:** `workflows/retail-banking-streams-governance-dryrun.yaml` is an optional **MCP** `run_workflow` helper (agent calls `discover_o11y_data` + ES|QL) for dry runs from the IDE; it does **not** register a workflow in Kibana. For the Kibana UI list, use **Create a new workflow** or `POST /api/workflows/workflow` (see `.cursor/skills/kibana-observability-workflows-api/SKILL.md`).
