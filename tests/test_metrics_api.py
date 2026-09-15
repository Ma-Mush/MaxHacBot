"""Tests for metrics ingestion and metadata endpoints."""
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test /api/v1/health returns healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"
    assert data["registered_reports_count"] >= 2


@pytest.mark.asyncio
async def test_ingest_single_metric(client: AsyncClient, auth_headers: dict):
    """Test ingesting a single metric with tags."""
    payload = {
        "name": "revenue",
        "value": 1250.50,
        "unit": "USD",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tags": {"region": "EU", "channel": "google_ads", "store_id": "42"},
    }
    response = await client.post("/api/v1/metrics", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "revenue"
    assert data["value"] == 1250.50
    assert data["unit"] == "USD"
    assert data["tags"] == {"region": "EU", "channel": "google_ads", "store_id": "42"}
    assert "id" in data


@pytest.mark.asyncio
async def test_ingest_unauthorized(client: AsyncClient):
    """Test request without valid API key is rejected with 401."""
    payload = {
        "name": "revenue",
        "value": 100.0,
    }
    response = await client.post("/api/v1/metrics", json=payload, headers={"X-API-Key": "wrong_key"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ingest_batch_metrics(client: AsyncClient, auth_headers: dict):
    """Test batch ingestion of multiple metric points."""
    payload = {
        "metrics": [
            {"name": "orders_count", "value": 5.0, "unit": "pcs", "tags": {"channel": "direct"}},
            {"name": "revenue", "value": 450.0, "unit": "USD", "tags": {"channel": "direct"}},
            {"name": "api_latency", "value": 42.1, "unit": "ms", "tags": {"host": "node-1"}},
        ]
    }
    response = await client.post("/api/v1/metrics/batch", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["inserted"] == 3
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_metrics_metadata(client: AsyncClient, auth_headers: dict):
    """Test retrieving distinct metric names and tag keys."""
    # Ingest diverse metrics
    batch = {
        "metrics": [
            {"name": "sales", "value": 10.0, "tags": {"city": "Berlin", "tier": "gold"}},
            {"name": "cpu_load", "value": 55.0, "tags": {"server": "prod-1", "datacenter": "fra1"}},
        ]
    }
    await client.post("/api/v1/metrics/batch", json=batch, headers=auth_headers)

    res = await client.get("/api/v1/metrics/meta", headers=auth_headers)
    assert res.status_code == 200
    meta = res.json()
    assert "sales" in meta["metric_names"]
    assert "cpu_load" in meta["metric_names"]
    assert "city" in meta["tag_keys"]
    assert "server" in meta["tag_keys"]
    assert meta["total_records"] >= 2


@pytest.mark.asyncio
async def test_list_and_filter_metrics(client: AsyncClient, auth_headers: dict):
    """Test querying metrics with name filtering."""
    batch = {
        "metrics": [
            {"name": "unique_visits", "value": 100.0},
            {"name": "unique_visits", "value": 200.0},
            {"name": "bounces", "value": 15.0},
        ]
    }
    await client.post("/api/v1/metrics/batch", json=batch, headers=auth_headers)

    res = await client.get("/api/v1/metrics?name=unique_visits", headers=auth_headers)
    assert res.status_code == 200
    records = res.json()
    assert len(records) == 2
    assert all(r["name"] == "unique_visits" for r in records)
