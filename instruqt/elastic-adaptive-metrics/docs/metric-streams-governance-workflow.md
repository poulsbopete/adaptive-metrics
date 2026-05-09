# Metric governance loop: Workflows + Streams + AI (blueprint)

This document describes how to implement the pattern you described: a **Kibana Observability Workflow** on a **short schedule** (for example every five minutes) that **inspects Streams**, asks an **AI assistant** for safe changes (sub-routes, retention, or drops), and **applies** updates via the **Streams API**—while **Elastic Agent** continues to ship telemetry under **Fleet** policy.

> **Scope:** Architecture and API pointers for workshop authors. Validate step types and request bodies against **your** Serverless / Kibana minor version before production use. The Streams HTTP API is still evolving; see Elastic’s note on technical preview where it appears in the [Streams API group](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-streams).

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

Use **`kibana.request`** (or equivalent HTTP-to-Kibana step) with `kbn-xsrf` and an API key that has at least **`read_stream`** and **`manage_stream`** where needed.

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
  S[Scheduled trigger 5m] --> L[List streams GET /api/streams]
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

1. **Scheduled trigger** — cron-style `*/5 * * * *` (or UI “every 5 minutes”).
2. **List + filter** — Parse JSON from `GET /api/streams`. Select **wired** parents that are allowed to receive **child** routes (your naming convention, e.g. `otel-metrics-*`).
3. **Context pack** — Run **ES|QL** (workflow step or pre-request) for top-N noisy metric families; attach **dashboard/SLO** identifiers the way you already teach in the lab (**declared usage**).
4. **AI step** — Prompt the model to output **only** a JSON patch: suggested `child` stream names, routing predicates, retention intent, and explicit **“no change”** when uncertain. Enforce JSON schema validation in a small **inline script** step if your workflow product supports it.
5. **Governance gate** — Default to **Case** + `@mention` SRE. Auto-apply only after the Case transitions to approved, or only in non-prod.
6. **Apply** — `PUT /api/streams/{name}` with the body shape required by your version (see API docs for `stream`, `rules`, `queries`, `dashboards` fields).
7. **Elastic Agent (optional branch)** — If the AI recommends **reducing collectors** (fewer datasets), use **Fleet API** to adjust the relevant integration policy **after** human approval—not from the same unguarded loop as Streams edits.

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

The track teaches **declared usage** and **Streams** as concepts. This blueprint is the **next implementation step**: build or import the workflow in Kibana, then version the workflow definition alongside this repo when your team is ready.
