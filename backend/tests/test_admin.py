from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.cli.platform_admin import set_platform_admin
from app.modules.users.repository import UserRepository
from tests.conftest import register_and_login


def make_platform_admin(db: Session, email: str = "admin@example.com") -> None:
    user = UserRepository(db).get_by_email(email)
    assert user is not None
    user.is_platform_admin = True
    db.commit()


def test_regular_user_cannot_access_admin_api(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.get("/api/v1/admin/users", headers=headers)

    assert response.status_code == 403


def test_admin_can_list_users_and_businesses(client: TestClient, db: Session) -> None:
    admin_headers = register_and_login(client, "admin@example.com")
    register_and_login(client, "member@example.com")
    make_platform_admin(db)
    client.post(
        "/api/v1/businesses",
        json={"name": "Cửa hàng thử nghiệm"},
        headers=admin_headers,
    )

    users_response = client.get("/api/v1/admin/users", headers=admin_headers)
    businesses_response = client.get("/api/v1/admin/businesses", headers=admin_headers)

    assert users_response.status_code == 200
    assert {user["email"] for user in users_response.json()} == {
        "admin@example.com",
        "member@example.com",
    }
    assert businesses_response.status_code == 200
    assert businesses_response.json()[0]["name"] == "Cửa hàng thử nghiệm"


def test_admin_can_disable_user_and_action_is_audited(client: TestClient, db: Session) -> None:
    admin_headers = register_and_login(client, "admin@example.com")
    member_headers = register_and_login(client, "member@example.com")
    make_platform_admin(db)
    member = UserRepository(db).get_by_email("member@example.com")
    assert member is not None

    response = client.patch(
        f"/api/v1/admin/users/{member.id}/status",
        json={"is_active": False},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert client.get("/api/v1/auth/me", headers=member_headers).status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "member@example.com", "password": "StrongPass123!"},
        ).status_code
        == 401
    )

    logs = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert logs.status_code == 200
    assert logs.json()[0]["action"] == "USER_STATUS_CHANGED"
    assert logs.json()[0]["target_id"] == str(member.id)
    assert logs.json()[0]["details"] == {
        "previous_is_active": True,
        "is_active": False,
    }


def test_admin_cannot_disable_own_account(client: TestClient, db: Session) -> None:
    headers = register_and_login(client, "admin@example.com")
    make_platform_admin(db)
    admin = UserRepository(db).get_by_email("admin@example.com")
    assert admin is not None

    response = client.patch(
        f"/api/v1/admin/users/{admin.id}/status",
        json={"is_active": False},
        headers=headers,
    )

    assert response.status_code == 409
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200


def test_platform_admin_cli_helper_grants_and_revokes(client: TestClient, db: Session) -> None:
    register_and_login(client, "operator@example.com")

    assert set_platform_admin(db, email=" OPERATOR@example.com ", enabled=True)
    user = UserRepository(db).get_by_email("operator@example.com")
    assert user is not None
    assert user.is_platform_admin is True

    assert set_platform_admin(db, email="operator@example.com", enabled=False)
    assert user.is_platform_admin is False
    assert set_platform_admin(db, email="missing@example.com", enabled=True) is False
