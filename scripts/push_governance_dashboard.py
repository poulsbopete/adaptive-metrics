#!/usr/bin/env python3
"""
Create the metric governance dashboard on Elastic Serverless / Instruqt Kibana.

Uses POST /api/dashboards with **Elastic-Api-Version** set to a **YYYY-MM-DD** string (default **2023-10-31**;
Kibana rejects bare ``1``). Override with **KIBANA_DASHBOARDS_API_VERSION** if your stack documents a newer date.

Payload for **2023-10-31**: **`markdown`** panels plus **`vis`** panels whose **`config.type`** is **`data_table`**
with **`data_source.type: esql`** (and **`rows`** / **`styling`**). The same API date does **not** accept
**`vis` + `config.type: metric`** with **`esql`** (it expects **`data_view_reference`** / **`data_view_spec`** for
that path — the pattern you see in a **Systems Operations**–style export: **`metric`** / **`xy`** on **`traces-*`**
/ **`metrics-*`** with KQL **`query`** and field aggregations). Use **MCP / a newer documented `Elastic-Api-Version`**
if you need native **metric/xy** from JSON for ES|QL-driven KPIs without **`data_table`**.

Environment:
  KIBANA_URL or ES_URL  — Kibana base URL (Instruqt often uses the same host for both)
  ES_API_KEY or ELASTIC_API_KEY or KIBANA_API_KEY

Body defaults to dashboards/instruqt-metric-governance-dashboard.json. Legacy **time_from** /
**time_to** keys are stripped before POST (use **time_range** only, like a Kibana dashboard export).

Optional:
  GOVERNANCE_DASHBOARD_JSON — path to override JSON spec
  GOVERNANCE_DASHBOARD_ID — existing Kibana dashboard saved-object id to **update** via PUT (same URL as in the browser).
    When unset, POST **creates a new dashboard every run** (new id / link). Use this env after the first import so
    you overwrite the dashboard you actually open instead of spawning duplicates.
"""
from __future__ import annotations

import gzip
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

API_VERSION = os.environ.get("KIBANA_DASHBOARDS_API_VERSION", "2023-10-31")


def decode(raw: bytes) -> str:
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def kibana_dashboard_request(
    base: str,
    key: str,
    body: dict,
    *,
    method: str,
    path_suffix: str,
) -> tuple[int, str]:
    """path_suffix is '' for POST create, or '/{id}' for PUT update."""
    data = json.dumps(body).encode("utf-8")
    url = f"{base.rstrip('/')}/api/dashboards{path_suffix}"
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"ApiKey {key}",
            "kbn-xsrf": "true",
            "Content-Type": "application/json",
            "Elastic-Api-Version": API_VERSION,
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, decode(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, decode(e.read())


def main() -> int:
    base = os.environ.get("KIBANA_URL") or os.environ.get("ES_URL")
    key = os.environ.get("ES_API_KEY") or os.environ.get("ELASTIC_API_KEY") or os.environ.get("KIBANA_API_KEY")
    if not base or not key:
        print(
            "error: set KIBANA_URL or ES_URL and ES_API_KEY or ELASTIC_API_KEY",
            file=sys.stderr,
        )
        return 1

    root = pathlib.Path(__file__).resolve().parents[1]
    path = pathlib.Path(
        os.environ.get(
            "GOVERNANCE_DASHBOARD_JSON",
            str(root / "dashboards" / "instruqt-metric-governance-dashboard.json"),
        )
    )
    spec = json.loads(path.read_text(encoding="utf-8"))
    # POST /api/dashboards (2023-10-31) allows time_range only, not legacy time_from / time_to.
    spec.pop("time_from", None)
    spec.pop("time_to", None)
    # Avoid sending a stale id in the body when POST creates a new dashboard.
    spec.pop("id", None)

    dash_id = (os.environ.get("GOVERNANCE_DASHBOARD_ID") or "").strip()

    if dash_id:
        code, text = kibana_dashboard_request(
            base, key, spec, method="PUT", path_suffix=f"/{dash_id}"
        )
        action = "updated"
        if code == 404:
            print(
                f"WARN: PUT returned 404 — dashboard id not found: {dash_id}\n"
                "Retry without GOVERNANCE_DASHBOARD_ID to create a new one, then set the env to that id.",
                file=sys.stderr,
            )
            return 1
    else:
        code, text = kibana_dashboard_request(
            base, key, spec, method="POST", path_suffix=""
        )
        action = "created"

    if code not in (200, 201):
        print(f"HTTP {code}", text[:4000], file=sys.stderr)
        return 1
    did = dash_id or "?"
    if text.strip():
        try:
            out = json.loads(text)
            did = out.get("id", did)
        except json.JSONDecodeError:
            print(text[:2000])
            return 0
    print(f"Dashboard {action}.")
    print("id:", did)
    print("open:", f"{base.rstrip('/')}/app/dashboards#/view/{did}")
    if action == "created":
        print(
            "\nTip: POST creates a **new** dashboard each run. To overwrite this same dashboard next time:\n"
            f'  export GOVERNANCE_DASHBOARD_ID="{did}"',
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
