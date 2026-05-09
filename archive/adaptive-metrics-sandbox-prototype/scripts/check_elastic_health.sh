#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${ELASTIC_URL:-}" || -z "${ELASTIC_API_KEY:-}" ]]; then
  echo "Missing ELASTIC_URL or ELASTIC_API_KEY in the environment." >&2
  exit 2
fi

code="$(
  curl -sS -o /tmp/es-health.json -w '%{http_code}' \
    -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
    "${ELASTIC_URL%/}/_cluster/health?wait_for_status=yellow&timeout=15s"
)"

if [[ "${code}" != "200" ]]; then
  echo "Unexpected HTTP ${code} from Elasticsearch health endpoint." >&2
  cat /tmp/es-health.json >&2 || true
  exit 1
fi

python3 - <<'PY'
import json
from pathlib import Path
p = Path("/tmp/es-health.json")
data = json.loads(p.read_text(encoding="utf-8"))
status = data.get("status")
if status not in {"green", "yellow", "red"}:
    raise SystemExit(f"Unrecognized health payload: {data!r}")
print(f"cluster health status: {status}")
PY
