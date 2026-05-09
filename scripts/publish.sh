#!/usr/bin/env bash
# Publish lab changes to Git (origin) and Instruqt (elastic-adaptive-metrics track).
# Usage:
#   ./scripts/publish.sh ["commit message"]
# Skip Instruqt (e.g. CI or no CLI auth):
#   SKIP_INSTRUQT=1 ./scripts/publish.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRACK_DIR="${REPO_ROOT}/instruqt/elastic-adaptive-metrics"
COMMIT_MESSAGE="${1:-chore: sync lab and Instruqt track}"

cd "${REPO_ROOT}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "error: not a git repository. Run: git init && git remote add origin <url>" >&2
  exit 1
fi

git add -A
if git diff --cached --quiet; then
  echo "git: nothing to commit (clean index after add)."
else
  git commit -m "${COMMIT_MESSAGE}"
fi

if git remote get-url origin >/dev/null 2>&1; then
  branch="$(git branch --show-current)"
  if git rev-parse --abbrev-ref "${branch}@{upstream}" >/dev/null 2>&1; then
    git push
  else
    git push -u origin "${branch}"
  fi
  echo "git: push complete."
else
  echo "git: no 'origin' remote; skipped push. Add: git remote add origin git@github.com:ORG/adaptive-metrics.git" >&2
fi

if [[ "${SKIP_INSTRUQT:-}" == "1" ]]; then
  echo "instruqt: skipped (SKIP_INSTRUQT=1)."
  exit 0
fi

cd "${TRACK_DIR}"
instruqt track validate

if grep -q 'REPLACE_WITH' track.yml; then
  echo "error: instruqt/elastic-adaptive-metrics/track.yml still has REPLACE_* placeholders (id and/or developers)." >&2
  echo "      Set a real track id from Instruqt after creating the track, and your email under developers." >&2
  exit 1
fi

if ! instruqt track push; then
  echo "" >&2
  echo "instruqt: track push failed." >&2
  echo "" >&2
  echo "If you see [ERROR] Entity not found, common causes are:" >&2
  echo "  1) Version control — Tracks linked to GitHub should be published via GitHub + Instruqt" >&2
  echo "     Publish, not only CLI push. See:" >&2
  echo "     https://docs.instruqt.com/tracks/manage/version-control.md" >&2
  echo "  2) Stale track id — Run: ./scripts/fetch-instruqt-track-id.sh" >&2
  echo "     then copy id (and checksum if present) into instruqt/elastic-adaptive-metrics/track.yml" >&2
  echo "  3) Wrong team — Run: instruqt config get team   (expect: elastic)" >&2
  exit 1
fi
echo "instruqt: track push complete."
