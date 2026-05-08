---
slug: draft-streams-policy
type: challenge
title: "Challenge 4: Draft server-side shaping (Streams-ready YAML)"
teaser: >-
  Turn classification into explicit retention and downsampling intent—human acknowledgement required.
notes:
  - type: text
    contents: >-
      This YAML is illustrative. Map fields to your real Streams / ingest controls when teaching inside Elastic.
tabs:
  - title: Shell
    type: terminal
    hostname: sandbox
difficulty: intermediate
timelimit: 900
---

## Goal

Edit the policy sketch at:

`/opt/adaptive-metrics-lab/policies/streams-snippet.yaml`

## Required change

Set:

```yaml
learner_acknowledged: true
```

This models **human-in-the-loop** approval for governance changes (contrast with dangerous silent drops).

Optional: tighten `retention_hot_days` for `kube_pod_status_phase` based on your inventory from challenge 2.

## Validate locally

```bash
grep -n '^learner_acknowledged' /opt/adaptive-metrics-lab/policies/streams-snippet.yaml
python3 -c "import yaml; yaml.safe_load(open('/opt/adaptive-metrics-lab/policies/streams-snippet.yaml')); print('yaml ok')"
```

Click **Check**.
