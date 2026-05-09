#!/usr/bin/env bash
# Fetch the canonical track.yml from Instruqt (team elastic) into a temp directory
# and print the track id. Use when `instruqt track push` fails with Entity not found
# and you suspect a stale id in repo.
set -euo pipefail
TMP="$(mktemp -d)"
cleanup() { rm -rf "${TMP}"; }
trap cleanup EXIT

cd "${TMP}"
echo "Pulling elastic/elastic-adaptive-metrics into ${TMP} ..." >&2
if ! instruqt track pull elastic/elastic-adaptive-metrics --force; then
  echo "error: pull failed. Check team (instruqt config get team) and track slug." >&2
  exit 1
fi

TRACK_YML="$(find "${TMP}" -name track.yml | head -1)"
if [[ -z "${TRACK_YML}" || ! -f "${TRACK_YML}" ]]; then
  echo "error: track.yml not found after pull." >&2
  exit 1
fi

echo "--- ${TRACK_YML} (id + checksum lines) ---" >&2
grep -E '^(id|checksum|slug|owner):' "${TRACK_YML}" || true
