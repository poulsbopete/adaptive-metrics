# adaptive-metrics

Canonical **Instruqt** track: **[elastic / elastic-adaptive-metrics](https://play.instruqt.com/manage/elastic/tracks/elastic-adaptive-metrics)**.

## Workshop goal

Use **live Elastic Serverless** data — track default **Retail Banking Platform** (payments, claims, policy, fraud) — to show **governed metrics at scale**: discover which metrics are *not* driving dashboards or operations, then **recommend** aggregation, trimming high-cardinality dimensions, or retiring unused series—with **human governance**, not silent surprises. The demo ships **six** incident- and SLO-oriented **Kibana Workflows** from the launcher; **track setup** (`setup-es3-api`) installs the **seventh** — **Adaptive metrics — Retail Banking · Metric governance snapshot** — on the same project using **ES|QL**, **Streams**, **downsampling**, **Cases**, and **AI workflow steps** (see **`workflows/kibana/metric-governance-retail-banking-starter.yaml`** and **`instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md`**).

**Elastic differentiation in this story:** **downsampling** for metrics at scale, **server-side** policy (Streams, retention tiers), and **workflows** that prove which signals matter when incidents fire—so **TCO** and reliability stay aligned on one platform.

### Competitive context (regulated enterprises)

Large **financial institutions**, insurers, and similarly **regulated** enterprises often evaluate **lean metrics-only stacks** (low $/ingest) alongside **full-stack SaaS observability**. This lab is written so you can show **Elastic as the metrics leader** on dimensions those bake-offs typically score:

| If the buyer brings up… | Elastic answer (what this track demonstrates) |
|-------------------------|-----------------------------------------------|
| **Cheap raw ingest** | **TCO is not only storage.** Elastic wins on **governed cardinality** (downsampling, retention tiers, Streams), **one platform** for metrics + logs + traces + security analytics on the same store, and **predictable** enterprise posture when volume spikes—without your team owning every scaling and HA edge case for a separate metrics tier. |
| **SaaS depth and charts** | Same signals, **controlled cost**: high-cardinality and custom-metric bill risk is a common buyer pain. Elastic **Serverless** + **ES\|QL** + **downsampling** + **workflows** tie spend to **declared usage** (dashboards, SLOs, alerts)—so you lead on **metrics economics and governance**, not only on more widgets. |

You are not arguing Elastic is the cheapest raw scraper—you are showing **why Elastic wins the metrics decision** for regulated enterprises that need **reliability, auditability, and cost discipline** in one stack.

The directory `instruqt/elastic-adaptive-metrics/` is the **track root** you edit and push (see `track.yml` / `config.yml` / challenges). Sync with Instruqt via Git and/or the CLI as below.

An earlier **offline sandbox lab** (fixtures + five challenges on a container host) is preserved under `archive/adaptive-metrics-sandbox-prototype/` if you want to port pieces into this track or a new slug later.

## Layout

| Path | Purpose |
|------|---------|
| `instruqt/elastic-adaptive-metrics/` | **Source of truth** for the live Instruqt track (challenges, `config.yml`, `track.yml`, lifecycle scripts). |
| `DEMO_SCENARIO_ID` | In `config.yml` under `es3-api` environment. Default **`banking`** (**Retail Banking Platform**: ACH/wires/bill pay, claims, policy, fraud, mobile). Override per customer in Instruqt Sandbox → VM environment. |
| Sandbox secrets | `config.yml` lists **`LLM_PROXY_PROD`** and **`ESS_CLOUD_API_KEY`** by name only. Set values in Instruqt (**Sandbox → Secrets**); Git never stores secret material. |
| `instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md` | Blueprint: **scheduled Workflow → Streams API → AI → Case → Agent/Fleet** for metric governance. |
| `workflows/kibana/metric-governance-retail-banking-starter.yaml` | **Metric governance** workflow — **scheduled `every: 5m`**, **`kibana.streams.list`**, optional **cost-control partitions** on **`logs.otel.banking`** via **`POST /api/streams/.../_fork`** + child **`_ingest` retention**, ES\|QL + Cases (optional **`ai.prompt`**). **`POST`/`PUT`** via **`scripts/push_kibana_workflow.py`**. **Instruqt** bundles **`track_scripts/workflows/metric-governance-retail-banking-starter.yaml`** — sync from this path; setup POSTs id **`adaptive-metrics-metric-governance-starter`** after demo deploy. |
| `docs/product/ELASTIC_PRODUCT_INTAKE_ADAPTIVE_METRICS.md` | **Elastic Product intake pack:** Adaptive Metrics narrative, gaps, success criteria, plus pointers to production-oriented workflow YAML for formal submission. |
| `workflows/kibana/adaptive-metrics-governance-production-template.yaml` | **Production-oriented** governance workflow template (**`every: 24h`**) — pair with the intake doc for Product review; lab demos use **`metric-governance-retail-banking-starter.yaml`** (`every: 5m`). |
| `dashboards/metric-governance-retail-banking-as-code.json` | **Streams savings & TCO** shape for **MCP** `kibana_create_dashboard` (or other tooling). Do **not** assume it matches **`POST /api/dashboards`** with **`Elastic-Api-Version: 2023-10-31`** without checking the payload — use **`instruqt-metric-governance-dashboard.json`** for that path. |
| `dashboards/instruqt-metric-governance-dashboard.json` | **`POST /api/dashboards`** payload for metric governance tiles (**ES\|QL** as **`vis` + `data_table`**). **Instruqt** bundles a copy at **`instruqt/elastic-adaptive-metrics/track_scripts/dashboards/instruqt-metric-governance-dashboard.json`** — keep it in sync when you edit the root file (setup script POSTs it after demo deploy). |
| `workflows/retail-banking-streams-governance-dryrun.yaml` | **MCP** `run_workflow` dry run only (not a Kibana tile). |
| `.cursor/skills/kibana-observability-workflows-api/` | Project skill: create **Kibana** workflows via `POST /api/workflows/workflow` vs MCP YAML. |
| `archive/adaptive-metrics-sandbox-prototype/` | Archived prototype lab (not deployed as its own track). |
| `scripts/push-to-serverless.sh` | Push `metric-governance-retail-banking-starter.yaml` to **Kibana Workflows** (`POST`/`PUT` `/api/workflows/workflow`). Needs `KIBANA_URL` or `ES_URL` + `ES_API_KEY` or `ELASTIC_API_KEY`. |
| `scripts/push_governance_dashboard.py` | Push `dashboards/instruqt-metric-governance-dashboard.json` to **Kibana** (`POST /api/dashboards` creates a **new** id each run unless **`GOVERNANCE_DASHBOARD_ID`** is set — then **`PUT /api/dashboards/{id}`** updates in place). Needs `KIBANA_URL` or `ES_URL` + API key. |
| `instruqt/.../track_scripts/noisy_otlp_metrics.py` | **Instruqt VM**: optional systemd **`noisy-metrics-otlp`** ships high-cardinality OTLP metrics (`noisy-governance-shipper`) for **Streams** retention / aggregation labs (needs **mOTLP** URL — see `metric-streams-governance-workflow.md`). |
| `scripts/publish.sh` | Git commit/push + `instruqt track push` for the track above. |
| `scripts/fetch-instruqt-track-id.sh` | Prints `id` / `checksum` from Instruqt after a temp pull (debugging). |

## Prerequisites

- [Instruqt CLI](https://docs.instruqt.com/getting-started/set-up-instruqt) with `instruqt auth login` and team **`elastic`** (`instruqt config get team`).
- Track slug for CLI: **`elastic/elastic-adaptive-metrics`** (see [Edit locally](https://docs.instruqt.com/tracks/manage/pull-a-track.md)).

## Publish Git and Instruqt together

```bash
./scripts/publish.sh "Describe your change"
```

`SKIP_INSTRUQT=1` skips the Instruqt step. The script no longer checks for `REPLACE_WITH` in `track.yml` (the live file uses real `id` and `checksum` from Instruqt).

## Re-sync from Instruqt (overwrite local with remote)

```bash
cd instruqt
rm -rf _pull-tmp && mkdir _pull-tmp && cd _pull-tmp
instruqt track pull elastic/elastic-adaptive-metrics --force
cd ..
rm -rf elastic-adaptive-metrics
mv _pull-tmp/elastic-adaptive-metrics .
rmdir _pull-tmp
```

## Troubleshooting: `Entity not found` on `instruqt track push`

1. **Version control (GitHub)** — If [Version control](https://docs.instruqt.com/tracks/manage/version-control.md) is enabled, publish via GitHub + **Publish** in Instruqt; avoid mixing undocumented CLI behavior with VC.
2. **Stale `id` / `checksum`** — Run `./scripts/fetch-instruqt-track-id.sh` and merge values into `instruqt/elastic-adaptive-metrics/track.yml`, or pull with `--force` as above.
3. **Manage URL** — [elastic-adaptive-metrics](https://play.instruqt.com/manage/elastic/tracks/elastic-adaptive-metrics).

## Push and test (Instruqt only)

```bash
cd instruqt/elastic-adaptive-metrics
instruqt track validate
instruqt track push
instruqt track open
```
