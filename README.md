# Adaptive metrics workshop (Instruqt)

This repository holds an **Instruqt track** that complements Elastic’s internal **Autonomous observability** style labs (for example [elastic-autonomous-observability](https://play.instruqt.com/manage/elastic/tracks/elastic-autonomous-observability)) by focusing on **TCO control**: metric inventory, **declared usage** (dashboards / alerts / SLOs), and **server-side shaping** (retention tiers, aggregation, Streams-style policy snippets)—without treating silent metric deletion as the default outcome.

Track in Instruqt: [elastic / elastic-adaptive-metrics](https://play.instruqt.com/manage/elastic/tracks/elastic-adaptive-metrics).

Because the managed track content is not exportable from here, align challenge copy and any shared hosts with whatever you use in Autonomous observability (same Kibana URL tab, same secret names, and so on). If you have access in Instruqt, pull the [elastic-autonomous-observability](https://play.instruqt.com/manage/elastic/tracks/elastic-autonomous-observability) track locally and reconcile hostnames, secrets, and browser tabs with this repo.

## Layout

- `instruqt/elastic-adaptive-metrics/` — track root (`track push` from this directory).
- `instruqt/elastic-adaptive-metrics/scripts/` — offline-friendly analysis scripts plus optional Elasticsearch checks.

## Prerequisites

- [Instruqt CLI](https://docs.instruqt.com/getting-started/set-up-instruqt) authenticated to your org (`instruqt auth login`).
- In `instruqt/elastic-adaptive-metrics/track.yml`, **`id`** and **`developers`** are set for [elastic-adaptive-metrics](https://play.instruqt.com/manage/elastic/tracks/elastic-adaptive-metrics). Re-sync with `instruqt track pull elastic-adaptive-metrics` if the remote track is recreated.

## Publish Git and Instruqt together

After `git remote add origin <your-repo-url>` (for example `git@github.com:poulsbopete/adaptive-metrics.git`), use the repo script so every change goes to **both** Git and Instruqt:

```bash
./scripts/publish.sh "Describe your change"
```

What it does: `git add -A`, commit (if there are changes), `git push` to `origin`, then `instruqt track validate` and `instruqt track push` from `instruqt/elastic-adaptive-metrics/`. If `track.yml` still contains `REPLACE_WITH`, the script stops before Instruqt so you do not push a broken track definition.

To push **Git only** (skip Instruqt): `SKIP_INSTRUQT=1 ./scripts/publish.sh`.

## Push and test (Instruqt only)

```bash
cd instruqt/elastic-adaptive-metrics
instruqt track push
instruqt track open
```

## Optional live cluster

Define sandbox secrets (for example `ELASTIC_URL`, `ELASTIC_API_KEY`) in Instruqt to enable challenge 05 checks. Challenge 02–04 run **fully offline** using bundled fixtures under `fixtures/`.
