# adaptive-metrics

Canonical **Instruqt** track: **[elastic / elastic-adaptive-metrics](https://play.instruqt.com/manage/elastic/tracks/elastic-adaptive-metrics)**.

## Workshop goal

Use **live Elastic Serverless** data — track default **Retail Banking Platform** (payments, claims, policy, fraud) — to show **governed metrics at scale**: discover which metrics are *not* driving dashboards or operations, then **recommend** aggregation, trimming high-cardinality dimensions, or retiring unused series—with **human governance**, not silent surprises. The shipped demo includes **six** incident- and SLO-oriented **Kibana Workflows**; **metric governance automation** is the **seventh workflow you add** on the same platform using **ES|QL**, **Streams**, **downsampling**, **Cases**, and **AI workflow steps** (see **`workflows/kibana/metric-governance-retail-banking-starter.yaml`** and **`instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md`**).

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
| `dashboards/metric-governance-retail-banking-as-code.json` | **Streams savings & TCO** dashboard (MCP `kibana_create_dashboard` or **POST /api/dashboards** v1): KPI **metric** tiles, **gauge**, **area**/**bar** charts — same layout as Instruqt push. |
| `dashboards/instruqt-metric-governance-dashboard.json` | **Instruqt** push target (`scripts/push_governance_dashboard.py`): ops-style **metric** / **gauge** / **xy** panels + markdown; **Elastic-Api-Version: 2023-10-31** by default (`KIBANA_DASHBOARDS_API_VERSION` overrides; must be **YYYY-MM-DD**). |
| `workflows/kibana/metric-governance-retail-banking-starter.yaml` | **Kibana** Observability workflow (import / `POST /api/workflows/workflow`): **scheduled `every: 5m`** by default, **Streams** list + ES|QL + Case — optional gated **`ai.prompt`** / **`ai.agent`**, **`waitForInput`** + **`kibana.streams.get`**, then extend with **`kibana.request`** `PUT` after merge (starter does **not** auto-**PUT** Streams). |
| `workflows/retail-banking-streams-governance-dryrun.yaml` | **MCP** `run_workflow` dry run only (not a Kibana tile). |
| `.cursor/skills/kibana-observability-workflows-api/` | Project skill: create **Kibana** workflows via `POST /api/workflows/workflow` vs MCP YAML. |
| `archive/adaptive-metrics-sandbox-prototype/` | Archived prototype lab (not deployed as its own track). |
| `scripts/push-to-serverless.sh` | Push `metric-governance-retail-banking-starter.yaml` to **Kibana Workflows** (`POST`/`PUT` `/api/workflows/workflow`). Needs `KIBANA_URL` or `ES_URL` + `ES_API_KEY` or `ELASTIC_API_KEY`. |
| `scripts/push_governance_dashboard.py` | Push `dashboards/instruqt-metric-governance-dashboard.json` to **Kibana** (`POST /api/dashboards`, **Elastic-Api-Version: 2023-10-31** by default). Needs `KIBANA_URL` or `ES_URL` + API key. |
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
