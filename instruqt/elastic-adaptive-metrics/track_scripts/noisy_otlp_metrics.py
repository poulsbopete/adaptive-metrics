#!/usr/bin/env python3
"""
Ship high-cardinality OTLP counters to Elastic mOTLP for Streams / retention labs.

Requires Elastic Cloud Managed OTLP (mOTLP), not raw Elasticsearch URL:
  OTEL_EXPORTER_OTLP_ENDPOINT  or  MOTLP_ENDPOINT
  OTEL_EXPORTER_OTLP_HEADERS   e.g.  Authorization=ApiKey <base64 key>

Optional:
  NOISY_METRICS_INTERVAL_SEC   export interval (default 20)
  NOISY_METRICS_CARDINALITY    distinct attribute combinations per cycle (default 120)
  NOISY_METRICS_DATASET        resource attribute data_stream.dataset (default governance.noisy)
"""
from __future__ import annotations

import hashlib
import logging
import os
import random
import time
from typing import Iterable

from opentelemetry import metrics as metrics_api
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

_LOG = logging.getLogger("noisy_otlp_metrics")


def _endpoint() -> str:
    return (
        os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        or os.environ.get("MOTLP_ENDPOINT")
        or ""
    ).strip().rstrip("/")


def _resource() -> Resource:
    dataset = os.environ.get("NOISY_METRICS_DATASET", "governance.noisy").strip()
    return Resource.create(
        {
            "service.name": "noisy-governance-shipper",
            "service.namespace": "adaptive-metrics-lab",
            "deployment.environment": os.environ.get("NOISY_METRICS_ENV", "instruqt"),
            "data_stream.dataset": dataset,
        }
    )


def _cardinality_labels(n: int, cycle: int) -> Iterable[dict[str, str]]:
    """Deterministic high-cardinality attribute sets (stable series for aggregation demos)."""
    for i in range(n):
        h = hashlib.sha256(f"{cycle}:{i}".encode()).hexdigest()[:12]
        yield {
            "governance.tenant_id": f"tenant-{i % 37}",
            "governance.sku": f"SKU-{h}",
            "governance.replica": f"pod-{i % 23}",
            "governance.shard": f"shard-{i % 5}",
        }


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("NOISY_METRICS_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    endpoint = _endpoint()
    if not endpoint:
        _LOG.error(
            "Missing OTEL_EXPORTER_OTLP_ENDPOINT (or MOTLP_ENDPOINT). "
            "Copy the Ingest / Managed OTLP URL from the project (not the Elasticsearch URL)."
        )
        raise SystemExit(2)

    interval = max(5, int(os.environ.get("NOISY_METRICS_INTERVAL_SEC", "20")))
    cardinality = max(20, int(os.environ.get("NOISY_METRICS_CARDINALITY", "120")))

    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(),
        export_interval_millis=interval * 1000,
    )
    provider = MeterProvider(resource=_resource(), metric_readers=[reader])
    metrics_api.set_meter_provider(provider)

    meter = metrics_api.get_meter(__name__)
    counter_requests = meter.create_counter(
        "governance.noisy.http_requests_total",
        description="Synthetic high-cardinality request counter for Streams governance labs",
    )
    counter_noise = meter.create_counter(
        "governance.noisy.background_events_total",
        description="Background noise counter (cardinality via attributes)",
    )
    counter_rollups = meter.create_counter(
        "governance.noisy.rollup_candidates_total",
        description="Points eligible for coarser rollups / child streams in demos",
    )

    _LOG.info(
        "Shipping to %s every %ss with cardinality=%s",
        endpoint,
        interval,
        cardinality,
    )
    cycle = 0
    while True:
        t0 = time.time()
        for attrs in _cardinality_labels(cardinality, cycle):
            counter_requests.add(random.randint(1, 8), attributes=attrs)
            counter_noise.add(random.randint(0, 3), attributes=attrs)
            counter_rollups.add(random.randint(0, 2), attributes=attrs)
        cycle += 1
        elapsed = time.time() - t0
        sleep_for = max(1.0, interval - elapsed)
        time.sleep(sleep_for)


if __name__ == "__main__":
    main()
