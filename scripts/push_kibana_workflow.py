#!/usr/bin/env python3
"""POST (or PUT) the retail banking metric governance workflow to Kibana Serverless.

Requires environment variables (no secrets in repo):
  KIBANA_URL or ES_URL
  ES_API_KEY or ELASTIC_API_KEY or KIBANA_API_KEY

Optional:
  WORKFLOW_ID  — defaults to adaptive-metrics-metric-governance-starter
  WORKFLOW_YAML — path to workflow file (defaults to repo workflows/kibana/metric-governance-retail-banking-starter.yaml)

On HTTP 409 or known \"already exists\" responses, tries PUT .../workflow/{id} with {\"yaml\": ...}.
"""
from __future__ import annotations

import gzip
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request


def main() -> int:
    kb = (os.environ.get("KIBANA_URL") or os.environ.get("ES_URL", "")).rstrip("/")
    key = os.environ.get("ES_API_KEY") or os.environ.get("ELASTIC_API_KEY") or os.environ.get("KIBANA_API_KEY")
    if not kb or not key:
        print(
            "error: set KIBANA_URL or ES_URL and ES_API_KEY or ELASTIC_API_KEY in the environment or .env",
            file=sys.stderr,
        )
        return 1

    root = pathlib.Path(__file__).resolve().parents[1]
    default_yaml = root / "workflows" / "kibana" / "metric-governance-retail-banking-starter.yaml"
    yaml_path = pathlib.Path(os.environ.get("WORKFLOW_YAML", str(default_yaml)))
    wid = os.environ.get("WORKFLOW_ID", "adaptive-metrics-metric-governance-starter")
    yaml_text = yaml_path.read_text(encoding="utf-8")

    def decode_body(raw: bytes) -> str:
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", errors="replace")

    headers = {
        "Authorization": f"ApiKey {key}",
        "kbn-xsrf": "true",
        "Content-Type": "application/json; charset=utf-8",
    }

    def request(method: str, url: str, data: bytes | None = None) -> tuple[int, str]:
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.status, decode_body(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, decode_body(e.read())

    post_url = f"{kb}/api/workflows/workflow"
    put_url = f"{kb}/api/workflows/workflow/{wid}"
    body_post = json.dumps({"id": wid, "yaml": yaml_text}).encode("utf-8")
    body_put = json.dumps({"yaml": yaml_text}).encode("utf-8")

    code, text = request("POST", post_url, body_post)
    if code in (200, 201):
        print(f"workflow POST {code}", text[:500])
        return 0
    err_lower = text.lower()
    # Same fallback as instruqt setup-es3-api: conflict / duplicate → PUT update.
    if code in (400, 409) or "already exists" in err_lower or "duplicate" in err_lower:
        code2, text2 = request("PUT", put_url, body_put)
        print(f"workflow PUT {code2}", text2[:800])
        return 0 if code2 == 200 else 1

    print(f"workflow POST {code}", text[:800], file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
