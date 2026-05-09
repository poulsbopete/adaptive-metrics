# adaptive-metrics

Canonical **Instruqt** track: **[elastic / elastic-adaptive-metrics](https://play.instruqt.com/manage/elastic/tracks/elastic-adaptive-metrics)**.

The directory `instruqt/elastic-adaptive-metrics/` is a **pulled copy** of that track (same `id` and `checksum` as Instruqt). Edit there, then publish with Git and/or the Instruqt CLI as described below.

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
