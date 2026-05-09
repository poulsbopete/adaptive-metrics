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

## Troubleshooting: `Entity not found` on `instruqt track push`

1. **Version control (GitHub)** — If this track has [Version control](https://docs.instruqt.com/tracks/manage/version-control.md) enabled and is connected to GitHub, Instruqt expects changes through that pipeline. The docs note that **CLI pushes are not recorded in version control** and recommend **not mixing CLI push with version control**. Use **Publish** in the Instruqt UI after GitHub sync, or turn off version control for CLI-only authoring.

2. **Wrong or stale `id` in `track.yml`** — Refresh from the server: `./scripts/fetch-instruqt-track-id.sh` (pulls `elastic/elastic-adaptive-metrics` to a temp dir and prints `id` / `checksum`). Merge the printed `id` into `instruqt/elastic-adaptive-metrics/track.yml`. If the script’s pull also fails with Entity not found, the slug or team does not match your login (`instruqt config get team`).

3. **Manage URL** — [elastic-adaptive-metrics](https://play.instruqt.com/manage/elastic/tracks/elastic-adaptive-metrics) (confirm the track exists and your account can edit it).

## Push and test (Instruqt only)

```bash
cd instruqt/elastic-adaptive-metrics
instruqt track push
instruqt track open
```

## Optional live cluster

Define sandbox secrets (for example `ELASTIC_URL`, `ELASTIC_API_KEY`) in Instruqt to enable challenge 05 checks. Challenge 02–04 run **fully offline** using bundled fixtures under `fixtures/`.
