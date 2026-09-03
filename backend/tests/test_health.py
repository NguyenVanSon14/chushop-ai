from fastapi.testclient import TestClient


def test_health_and_database_readiness(client: TestClient) -> None:
    health = client.get("/health")
    readiness = client.get("/ready")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert readiness.status_code == 200
    assert readiness.json() == {"status": "ready", "database": "ok"}
