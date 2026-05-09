# adaptive-metrics

Canonical **Instruqt** track: **[elastic / elastic-adaptive-metrics](https://play.instruqt.com/manage/elastic/tracks/elastic-adaptive-metrics)**.

## Workshop goal

Use **live Elastic Serverless** data and **Kibana Workflows** (alert → investigate → case) the way vendors frame **“adaptive metrics”**: discover which metrics are *not* driving dashboards or operations, then **suggest** aggregation, dropping high-cardinality dimensions, or dropping unused series—always with governance, not silent surprises. [Grafana Adaptive Metrics](https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/) is the familiar name for that pattern on Grafana Cloud.

**Elastic differentiation in this story:** **downsampling** for metrics at scale (a capability this workshop positions alongside Grafana / Mimir stacks) plus **server-side** policy (Streams, retention tiers) and **workflows** that show which signals actually matter when incidents fire—so TCO and reliability stay aligned.

### Competitive context (regulated enterprises)

Large **financial institutions**, insurers, and similarly **regulated** enterprises often run **VictoriaMetrics** for “cheap metrics” and **Datadog** for SaaS depth. This lab is written so you can show **Elastic as the metrics leader** on dimensions those bake-offs actually score:

| If the buyer brings up… | Elastic answer (what this track demonstrates) |
|-------------------------|-----------------------------------------------|
| **VictoriaMetrics** — low ingest $/GB | **TCO is not only storage.** VM excels at lean ingestion; Elastic wins on **governed cardinality** (downsampling, retention tiers, Streams), **one platform** for metrics + logs + traces + security analytics on the same store, and **predictable** enterprise pricing when volume spikes—without your team owning every scaling and HA edge case. |
| **Datadog** — feature-rich SaaS | Same signals, **controlled cost**: custom metrics and high-cardinality bills are a known pain. Elastic **Serverless** + **ES\|QL** + **downsampling** + **workflows** tie spend to **declared usage** (dashboards, SLOs, alerts)—so you lead on **metrics economics and governance**, not only on “more charts.” |

You are not arguing Elastic is the cheapest raw scraper—you are showing **why Elastic wins the metrics decision** for regulated enterprises that need **reliability, auditability, and cost discipline** in one stack.

The directory `instruqt/elastic-adaptive-metrics/` is the **track root** you edit and push (see `track.yml` / `config.yml` / challenges). Sync with Instruqt via Git and/or the CLI as below.

An earlier **offline sandbox lab** (fixtures + five challenges on a container host) is preserved under `archive/adaptive-metrics-sandbox-prototype/` if you want to port pieces into this track or a new slug later.

## Layout

| Path | Purpose |
|------|---------|
| `instruqt/elastic-adaptive-metrics/` | **Source of truth** for the live Instruqt track (challenges, `config.yml`, `track.yml`, lifecycle scripts). |
| Sandbox secrets | `config.yml` lists **`LLM_PROXY_PROD`** and **`ESS_CLOUD_API_KEY`** by name only. Set values in Instruqt (**Sandbox → Secrets**); Git never stores secret material. |
| `archive/adaptive-metrics-sandbox-prototype/` | Archived prototype lab (not deployed as its own track). |
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
