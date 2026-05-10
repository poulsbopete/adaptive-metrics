#!/usr/bin/env python3
"""
Set data retention on existing Observability Streams (Serverless / stateful Kibana).

Elastic classic streams are registered when telemetry lands; you cannot *create* new
classic stream names via PUT /api/streams/{name} — only update them. This script
updates **retention** on streams you already see under Observability → Streams.

Primary path: PUT /api/streams/{name}/_ingest with a DSL retention (e.g. 7d, 30d).
Fallback: GET /api/streams/{name}, merge stream.ingest.lifecycle, PUT /api/streams/{name}.

Environment (same family as push_governance_dashboard.py):
  KIBANA_URL or ES_URL  — Kibana base URL
  ES_API_KEY or ELASTIC_API_KEY or KIBANA_API_KEY

Usage:
  python3 scripts/set_streams_retention.py --list
  python3 scripts/set_streams_retention.py 'metrics-hostmetricsreceiver.otel-default=7d' \\
      'metrics-k8sclusterreceiver.otel-default=30d'
  python3 scripts/set_streams_retention.py --dry-run 'metrics-generic.otel-default=14d'
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def kibana_base() -> str:
    base = os.environ.get("KIBANA_URL") or os.environ.get("ES_URL")
    if not base:
        print(
            "error: set KIBANA_URL or ES_URL and ES_API_KEY or ELASTIC_API_KEY",
            file=sys.stderr,
        )
        sys.exit(1)
    return base.rstrip("/")


def api_key() -> str:
    key = os.environ.get("ES_API_KEY") or os.environ.get("ELASTIC_API_KEY") or os.environ.get("KIBANA_API_KEY")
    if not key:
        print(
            "error: set ES_API_KEY, ELASTIC_API_KEY, or KIBANA_API_KEY",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def decode_body(raw: bytes) -> str:
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def _req(
    method: str,
    url: str,
    key: str,
    data: bytes | None = None,
) -> tuple[int, str]:
    headers = {
        "Authorization": f"ApiKey {key}",
        "kbn-xsrf": "true",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "identity",
    }
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return resp.status, decode_body(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, decode_body(e.read())


def stream_path_segment(name: str) -> str:
    return urllib.parse.quote(name, safe="")


def list_streams(base: str, key: str) -> int:
    code, text = _req("GET", f"{base}/api/streams", key)
    print(f"HTTP {code}")
    if code != 200:
        print(text[:8000], file=sys.stderr)
        return 1
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(text[:8000])
        return 0
    # Response shape varies by version; try common keys.
    streams = data.get("streams") or data.get("items") or data
    if isinstance(streams, dict) and "streams" in streams:
        streams = streams["streams"]
    if isinstance(streams, list):
        for item in streams:
            if isinstance(item, str):
                print(item)
            elif isinstance(item, dict):
                n = item.get("name") or item.get("id") or item.get("stream", {}).get("name")
                if n:
                    print(n)
    else:
        print(json.dumps(data, indent=2)[:12000])
    return 0 if code == 200 else 1


def put_ingest_retention(base: str, key: str, stream_name: str, retention: str, dry_run: bool) -> tuple[bool, str]:
    """Try narrow _ingest upsert."""
    path = f"{base}/api/streams/{stream_path_segment(stream_name)}/_ingest"
    body = {"ingest": {"lifecycle": {"dsl": {"data_retention": retention}}}}
    raw = json.dumps(body).encode("utf-8")
    if dry_run:
        return True, f"DRY-RUN PUT {path}\n{json.dumps(body)}"
    code, text = _req("PUT", path, key, raw)
    if code == 200:
        return True, f"OK {_ingest_marker(stream_name, retention)} via _ingest (HTTP {code})"
    return False, f"_ingest HTTP {code} for {stream_name}: {text[:4000]}"


def _ingest_marker(name: str, retention: str) -> str:
    return f"{name} -> {retention}"


def put_full_stream_retention(base: str, key: str, stream_name: str, retention: str, dry_run: bool) -> tuple[bool, str]:
    path = f"{base}/api/streams/{stream_path_segment(stream_name)}"
    code, text = _req("GET", path, key)
    if code != 200:
        return False, f"GET {stream_name} HTTP {code}: {text[:4000]}"
    doc = json.loads(text)
    stream_obj = doc.get("stream")
    if not isinstance(stream_obj, dict):
        return False, f"GET {stream_name}: missing top-level 'stream' object keys={list(doc)[:20]}"
    ingest = stream_obj.setdefault("ingest", {})
    ingest["lifecycle"] = {"dsl": {"data_retention": retention}}
    put_body: dict = {"stream": stream_obj}
    for k in ("dashboards", "queries", "rules"):
        if k in doc:
            put_body[k] = doc[k]
    raw = json.dumps(put_body).encode("utf-8")
    if dry_run:
        return True, f"DRY-RUN PUT {path} (full stream merge)\n{raw.decode()[:2000]}"
    code, text = _req("PUT", path, key, raw)
    if code == 200:
        return True, f"OK {_ingest_marker(stream_name, retention)} via full PUT (HTTP {code})"
    return False, f"PUT {stream_name} HTTP {code}: {text[:4000]}"


def apply_one(base: str, key: str, assignment: str, dry_run: bool) -> int:
    if "=" not in assignment:
        print(f"error: expected stream_name=7d got {assignment!r}", file=sys.stderr)
        return 1
    name, retention = assignment.split("=", 1)
    name, retention = name.strip(), retention.strip()
    if not name or not retention:
        print(f"error: empty name or retention in {assignment!r}", file=sys.stderr)
        return 1
    ok, msg = put_ingest_retention(base, key, name, retention, dry_run)
    print(msg)
    if ok:
        return 0
    print("retry: full stream GET+PUT merge", file=sys.stderr)
    ok2, msg2 = put_full_stream_retention(base, key, name, retention, dry_run)
    print(msg2)
    return 0 if ok2 else 1


def main() -> int:
    argv = sys.argv[1:]
    dry_run = False
    if argv and argv[0] == "--dry-run":
        dry_run = True
        argv = argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__ or "")
        return 0
    base, key = kibana_base(), api_key()
    if argv[0] == "--list":
        return list_streams(base, key)
    rc = 0
    for spec in argv:
        rc |= apply_one(base, key, spec, dry_run)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
