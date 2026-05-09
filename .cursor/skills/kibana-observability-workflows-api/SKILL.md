---
name: kibana-observability-workflows-api
description: >-
  Create or update Elastic Kibana Observability Workflows (the Workflows UI under
  Observability) via the Workflows HTTP API, and distinguish them from Elastic Serverless
  MCP save_workflow/run_workflow YAML. Use when adding scheduled Streams governance,
  AI steps, or automating workflow lifecycle outside the UI.
---

# Kibana Observability Workflows (product) vs MCP workflows

## Two different things

| Mechanism | What it is | Where it appears |
|-----------|-------------|------------------|
| **Kibana Observability Workflow** | Server-side workflow in the Elastic project (triggers, `kibana.request`, AI, cases). | **Observability → Workflows** in Kibana (e.g. *Retail Banking Platform SLO Management*). |
| **MCP `save_workflow` / `run_workflow`** | YAML checked into a repo; the **Cursor agent** runs each step by calling **MCP tools** (`esql_query`, `discover_o11y_data`, …). | **Not** listed in Kibana. Use for dry-run inventory beside Kibana. |

There is **no** separate installable Claude “agent skill” in the default skills bundle that posts to Kibana’s Workflows API; use **this project skill** or the API below.

## Create a workflow in Kibana (API)

Elastic documents **create workflow** as:

- **HTTP:** `POST /api/workflows/workflow` (space: `POST /s/{space_id}/api/workflows/workflow`)
- **Body (JSON):** `id` (optional), **`yaml`** (string) — Kibana validates the YAML before save
- **Headers:** `kbn-xsrf: true` (or common string), `Content-Type: application/json`
- **Auth:** API key or Basic
- **Privilege:** `workflowsManagement:create`

Reference: [Create a workflow](https://www.elastic.co/docs/api/doc/kibana/operation/operation-post-workflows-workflow) · [Workflows API group](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-workflows) · [Workflow steps](https://www.elastic.co/docs/explore-analyze/workflows/steps/kibana) · [Observability use cases](https://www.elastic.co/docs/explore-analyze/workflows/use-cases/observability)

### Practical authoring flow

1. In Kibana, **Create a new workflow** (or duplicate an existing scheduled workflow such as **SLO Management**).
2. Use **Export** (or copy the YAML from the editor) once the trigger and steps match your intent.
3. Version that YAML in git and optionally **POST** the same YAML to other environments with the API above.

Do **not** guess full product YAML here: step types and fields are version-sensitive. Start from an exported workflow that already runs in your Serverless project.

### Streams governance pattern

For **scheduled Streams inspection + AI + optional Case + `PUT /api/streams/{name}`**, follow the repo blueprint:

`instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md`

Implement **`kibana.request`** (or equivalent) steps against `GET /api/streams` and `PUT /api/streams/{name}` per [Streams API](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-streams). Default to **dry-run** (Case only, no `PUT`) until reviewed.

## MCP dry run in this repository

This repo includes an MCP workflow (for **Cursor** + Serverless MCP, not Kibana):

- **File:** `workflows/retail-banking-streams-governance-dryrun.yaml`
- **Name:** `retail-banking-streams-governance-dryrun`
- **Run (agent):** call MCP `run_workflow` with `name: "retail-banking-streams-governance-dryrun"` and `custom_dir` set to the repo’s `workflows/` directory (absolute path), then execute each returned step with the listed MCP tools.

That workflow snapshots **discover_o11y_data** + retail-banking **ES|QL** hotspots; it does **not** create a row in the Kibana Workflows list.
