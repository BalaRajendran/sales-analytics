"""Integration tests for URL endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.integration
async def test_create_url(client: AsyncClient):
    """Test creating a shortened URL."""
    response = await client.post(
        "/api/v1/urls/",
        json={"url": "https://example.com/very/long/url"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com/very/long/url"
    assert "short_code" in data
    assert "short_url" in data
    assert data["clicks"] == 0


@pytest.mark.integration
async def test_create_url_with_custom_code(client: AsyncClient):
    """Test creating a URL with custom short code."""
    response = await client.post(
        "/api/v1/urls/",
        json={"url": "https://example.com", "custom_code": "mycustom"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == "mycustom"


@pytest.mark.integration
async def test_create_duplicate_custom_code(client: AsyncClient):
    """Test creating a URL with duplicate custom code fails."""
    # Create first URL
    await client.post(
        "/api/v1/urls/",
        json={"url": "https://example.com", "custom_code": "duplicate"},
    )

    # Try to create second URL with same code
    response = await client.post(
        "/api/v1/urls/",
        json={"url": "https://another.com", "custom_code": "duplicate"},
    )
    assert response.status_code == 400


@pytest.mark.integration
async def test_list_urls(client: AsyncClient):
    """Test listing URLs."""
    # Create some URLs
    await client.post("/api/v1/urls/", json={"url": "https://example1.com"})
    await client.post("/api/v1/urls/", json={"url": "https://example2.com"})

    # List URLs
    response = await client.get("/api/v1/urls/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.integration
async def test_get_url_stats(client: AsyncClient):
    """Test getting URL statistics."""
    # Create a URL
    create_response = await client.post(
        "/api/v1/urls/",
        json={"url": "https://example.com"},
    )
    short_code = create_response.json()["short_code"]

    # Get stats
    response = await client.get(f"/api/v1/urls/{short_code}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == short_code
    assert data["clicks"] == 0


@pytest.mark.integration
async def test_redirect_increments_clicks(client: AsyncClient):
    """Test that redirecting increments click count."""
    # Create a URL
    create_response = await client.post(
        "/api/v1/urls/",
        json={"url": "https://example.com"},
    )
    short_code = create_response.json()["short_code"]

    # Redirect (without following)
    redirect_response = await client.get(
        f"/api/v1/urls/{short_code}", follow_redirects=False
    )
    assert redirect_response.status_code == 307

    # Check clicks increased
    stats_response = await client.get(f"/api/v1/urls/{short_code}/stats")
    data = stats_response.json()
    assert data["clicks"] == 1


@pytest.mark.integration
async def test_delete_url(client: AsyncClient):
    """Test deleting a URL."""
    # Create a URL
    create_response = await client.post(
        "/api/v1/urls/",
        json={"url": "https://example.com"},
    )
    short_code = create_response.json()["short_code"]

    # Delete it
    delete_response = await client.delete(f"/api/v1/urls/{short_code}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/urls/{short_code}")
    assert get_response.status_code == 404


@pytest.mark.integration
async def test_get_nonexistent_url(client: AsyncClient):
    """Test getting a non-existent URL returns 404."""
    response = await client.get("/api/v1/urls/nonexistent")
    assert response.status_code == 404
