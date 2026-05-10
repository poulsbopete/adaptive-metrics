#!/usr/bin/env python3
"""
Create the metric governance dashboard on Elastic Serverless / Instruqt Kibana.

Uses POST /api/dashboards with **Elastic-Api-Version** set to a **YYYY-MM-DD** string (Kibana rejects
bare ``1``). Default **2023-10-31**; override with **KIBANA_DASHBOARDS_API_VERSION** if your stack
documents a newer dashboards API date.

Payload: dashboard-as-code panels (**metric**, **gauge**, **xy**, **DASHBOARD_MARKDOWN**).

Environment:
  KIBANA_URL or ES_URL  — Kibana base URL (Instruqt often uses the same host for both)
  ES_API_KEY or ELASTIC_API_KEY or KIBANA_API_KEY

Body defaults to dashboards/instruqt-metric-governance-dashboard.json (title + panels only;
the script merges time_range, options, query, filters).

Optional:
  GOVERNANCE_DASHBOARD_JSON — path to override JSON spec
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


def kibana_post_dashboard(base: str, key: str, body: dict) -> tuple[int, str]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base.rstrip('/')}/api/dashboards",
        data=data,
        method="POST",
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
    code, text = kibana_post_dashboard(base, key, spec)
    if code not in (200, 201):
        print(f"HTTP {code}", text[:4000], file=sys.stderr)
        return 1
    try:
        out = json.loads(text)
    except json.JSONDecodeError:
        print(text[:2000])
        return 0
    did = out.get("id", "?")
    print("Dashboard created.")
    print("id:", did)
    print("open:", f"{base.rstrip('/')}/app/dashboards#/view/{did}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
