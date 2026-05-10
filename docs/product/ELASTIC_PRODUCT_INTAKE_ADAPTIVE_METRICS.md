# Elastic Product intake — **Adaptive Metrics** (governed metrics economics)

**Document type:** internal / partner product proposal pack  
**Audience:** Elastic Observability PM, Solutions Engineering, Field CTO review  
**Repo:** `adaptive-metrics` (canonical Instruqt track: **elastic / elastic-adaptive-metrics**)  
**Last updated:** 2026-05-10  

Use this file as the **cover narrative** when you file a formal idea (for example via internal Product intake, customer advisory, or account-sponsored FR). Pair it with the **reference workflow YAML** in this repository (paths below).

---

## 1. Executive summary

- **Adaptive Metrics** is a **positioning and capability slice**, not a separate SKU: it describes how Elastic Observability ties **metrics volume and cost** to **declared usage** (dashboards, SLOs, alerts, Cases, audit expectations)—then **recommends** policy changes (Streams, retention, downsampling) with **human governance**.
- **Buyer pain:** High-cardinality and custom-metric **bill risk**, plus **operational distrust** when cost cuts happen without evidence. Regulated enterprises need **audit-friendly change management**, not silent drops.
- **Elastic’s differentiation:** **One store** for metrics, logs, and traces; **ES|QL** for FinOps-grade evidence; **Streams** and **downsampling** as server-side levers; **Kibana Workflows + Cases** as the **control plane** for approvals—competing “cheap metrics tiers” rarely close this loop on one platform.
- **What exists today:** Shipping Observability features (Streams, downsampling where exposed, Workflows, Cases, AI workflow steps) plus a **repeatable lab** (Instruqt) that demonstrates the story on **live Serverless** telemetry.
- **What Product can formalize:** First-party **language, defaults, and packaged assets** (wizard, curated dashboards, opinionated workflow templates, documentation hierarchy under Observability) so customers recognize **Adaptive Metrics** as an Elastic-native practice—similar clarity to how **SLO** and **alerting** are productized.
- **Non-goals:** This proposal does **not** require a new metrics engine; it **organizes** existing Elasticsearch/Kibana capabilities into a buyer-facing narrative with **reference automation**.

---

## 2. Problem statement

### 2.1 Customer/buyer

- **FinOps / cloud economics** owners need to explain observability spend in terms **finance understands** (budget envelopes, chargeback, quarterly reviews)—not raw ingest TB alone.
- **SRE / platform** owners need to reduce noise and storage without **breaking the incidents people trust** (declared usage and golden signals).
- **Compliance / risk** stakeholders need **traceability**: who approved shorter retention, routing to a child stream, or a rollup—**Cases** and workflow runs carry that better than ad-hoc scripts.

### 2.2 Why now

- Metrics cardinality grows with **Kubernetes labels**, **multi-tenant IDs**, and **OpenTelemetry** adoption; cost surprises land **before** teams finish labeling “what matters.”
- Competitors position **low $/GB** metrics; Elastic wins when buyers evaluate **governance, correlation, and enterprise posture**—that story must be **product-shaped**, not only field-crafted.

---

## 3. Proposed solution: **Adaptive Metrics** as a productized practice

**Definition (draft for Product):**

> **Adaptive Metrics** is Elastic’s approach to **metrics economics and governance**: continuously **measure** what traffic is driving storage and query load, **compare** it to declared operational usage, **recommend** Streams/retention/downsampling actions, and **apply** changes through **workflows and Cases** so automation amplifies human judgment.

### 3.1 Pillars (map to existing capabilities)

| Pillar | Buyer outcome | Elastic building blocks (non-exhaustive) |
|--------|----------------|--------------------------------------------|
| **Discover** | Know where volume and cardinality concentrate | ES|QL on metrics indices, dashboard inventory, APM/SLO linkage |
| **Recommend** | Evidence-backed FinOps and SRE proposals | Observability AI Assistant / workflow `ai.prompt` / Agent Builder |
| **Approve** | Auditable decisions | Cases, workflow `waitForInput`, Slack/email connectors |
| **Apply** | Server-side policy, not one-off agents | Streams API, downsampling in Streams retention where available, Fleet for collection scope |

### 3.2 Packaged “Adaptive Metrics” deliverables (asks for Product)

These are **examples** of first-party packaging—not commitments from this repo:

1. **Observability navigation:** A landing pattern (tile, hub page, or guided tour) for **metrics governance & TCO**.
2. **Curated templates:** Importable **Kibana Workflows** (scheduled + manual), aligned with Serverless API stability cadence.
3. **Dashboard kits:** Executive + practitioner views that standardize **modeled savings** language with explicit **“illustrative / not a bill”** disclaimers until finance-grade metering exists.
4. **Documentation spine:** Single doc hierarchy linking Streams, downsampling, workflows, and FinOps ES|QL patterns.
5. **Success metrics:** Instrumentation for adoption (workflows enabled, Cases opened from governance runs, Streams PUTs after approval).

---

## 4. Reference implementation (this repository)

| Artifact | Path | Role |
|----------|------|------|
| **Production-oriented workflow template** | `workflows/kibana/adaptive-metrics-governance-production-template.yaml` | **Daily** Streams list + ES|QL snapshot + Case; gated AI **off** by default; intended for Product/staging review |
| **Lab/starter workflow** (fast cadence) | `workflows/kibana/metric-governance-retail-banking-starter.yaml` | **`every: 5m`** for Instruqt demos |
| **Implementation blueprint** | `instruqt/elastic-adaptive-metrics/docs/metric-streams-governance-workflow.md` | Architecture notes, API cautions, Fleet vs Streams boundaries |
| **Governance dashboard (API variants)** | `dashboards/instruqt-metric-governance-dashboard.json`, `dashboards/metric-governance-retail-banking-as-code.json` | ES|QL-forward tiles |
| **Deploy script** | `scripts/push_kibana_workflow.py` | `POST`/`PUT` `/api/workflows/workflow` with API key auth |

**Deploy the production template** (after setting credentials):

```bash
export KIBANA_URL="https://… .kb.*.elastic.cloud"
export ES_API_KEY="…"
WORKFLOW_ID=adaptive-metrics-governance-production \
WORKFLOW_YAML=workflows/kibana/adaptive-metrics-governance-production-template.yaml \
python3 scripts/push_kibana_workflow.py
```

**Version assumptions:** Workflow schema **`version: "1"`**, Kibana **9.5+** Serverless / Observability Workflows as validated in the Instruqt track. Re-validate against your target minor before GA claims.

---

## 5. Honest gaps (for Product planning)

- **Streams / workflow APIs** continue to evolve—customers need **stability commitments** and upgrade notes when Product wraps Adaptive Metrics as GA guidance.
- **“Modeled savings” math** in demos uses **assumption knobs** (for example illustrative **$/million points**); first-party Product should either supply **metering-aligned** views or keep **explicit disclaimers** to protect finance conversations.
- **Case deduplication:** The reference workflow creates a **new Case per run**. Enterprises may want **append to existing governance Case** or **rate-limited notifications**—workflow primitives or external automation may be needed.
- **Vertical ES|QL:** Retail Banking field names are **demo-realistic**; production rollout requires **customer-specific** `STATS` dimensions (services, regions, teams).

---

## 6. Success criteria (suggested for Product OKRs)

1. **Adoption:** % of Observability Serverless projects running at least one **governance or TCO** workflow template (telemetry allowed).
2. **Outcome:** Reduction in **support tickets** about “unexpected metrics/storage growth” where Streams/downsampling workflows were used (qual + quant).
3. **Message pull-through:** Field assets and analyst briefs consistently cite **Adaptive Metrics** alongside downsampling and Streams—not as a separate product name customers cannot find in docs.

---

## 7. Competitive framing (one paragraph)

Lean metrics stacks optimize **ingest efficiency**; full-stack SaaS optimizes **feature breadth**. **Adaptive Metrics** is how Elastic wins **regulated enterprises**: **governed cardinality**, **one correlated platform**, and **audit-friendly change**—with **ES|QL evidence** finance and engineering can share.

---

## 8. Phased roadmap suggestion (for discussion only)

| Phase | Scope |
|-------|--------|
| **Now** | Reference workflows + lab + executive dashboard pack (this repo) |
| **Next** | First-party template library + doc spine + naming consistency in Kibana UI copy |
| **Later** | Deeper metering alignment, optional automated dedupe into a standing Case, deeper Agent Builder integration for safe Streams merges |

---

## 9. Submission checklist (for the submitter)

- [ ] Attach this document **plus** `adaptive-metrics-governance-production-template.yaml`.
- [ ] Link the live **Instruqt** track for a **15-minute** stakeholder replay.
- [ ] Name **target segments** (e.g., retail banking path taken from the demo, or another vertical if ES|QL is retargeted).
- [ ] Call out **API version** tested and any **Org / project** constraints (Serverless vs stateful).
- [ ] List **open Product questions** (see §5) you want PM to answer explicitly.

---

## 10. Appendix — intake metadata

| Field | Value |
|-------|--------|
| **Working name** | Adaptive Metrics |
| **Primary persona** | FinOps + SRE + Observability lead |
| **Primary workflow artifact ID (suggested)** | `adaptive-metrics-governance-production` |
| **Related Elastic themes** | Observability Serverless, Streams, downsampling, ES|QL, Workflows, Cases, AI observability |

---

*This document is maintained in the `adaptive-metrics` repository for version control and field reuse.*
