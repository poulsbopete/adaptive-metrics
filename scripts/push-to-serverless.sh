#!/usr/bin/env bash
# Push versioned governance assets to Elastic Cloud Serverless (Kibana Workflows API).
#
# Prerequisites (export or put in repo-root .env — never commit secrets):
#   KIBANA_URL or ES_URL
#   ES_API_KEY or ELASTIC_API_KEY
#
# Usage:
#   ./scripts/push-to-serverless.sh
#   PUSH_GOVERNANCE_DASHBOARD=1 ./scripts/push-to-serverless.sh   # also create metric governance dashboard
#
# Optional:
#   PUSH_GOVERNANCE_DASHBOARD=1  — also run push_governance_dashboard.py (POST /api/dashboards, v1 panels).
#
# Dashboard: `dashboards/instruqt-metric-governance-dashboard.json` + scripts/push_governance_dashboard.py
# (`POST /api/dashboards`, Elastic-Api-Version **2023-10-31** by default — KPI metric / gauge / xy charts).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "${ROOT}/.env" ]]; then
  # shellcheck disable=SC1091
  set -a && source "${ROOT}/.env" && set +a
fi
python3 "${ROOT}/scripts/push_kibana_workflow.py"
if [[ "${PUSH_GOVERNANCE_DASHBOARD:-}" == "1" ]]; then
  python3 "${ROOT}/scripts/push_governance_dashboard.py"
fi
