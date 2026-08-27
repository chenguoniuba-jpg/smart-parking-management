import os
from datetime import datetime, timedelta

os.environ.setdefault(
    "SECRET_KEY",
    "test-only-secret-key-with-more-than-thirty-two-characters",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.database
import backend.main
from backend.database import Admin, Base, ParkingStatus


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TEST_ENGINE,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(monkeypatch):
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestingSessionLocal()
    admin = Admin(
        username="testadmin",
        email="testadmin@example.invalid",
        is_superuser=True,
    )
    admin.set_password("correct-horse-battery-staple")
    db.add(admin)
    db.commit()
    db.close()

    backend.main.app.dependency_overrides[backend.database.get_db] = override_get_db
    monkeypatch.setattr(backend.main, "init_db", lambda: None)
    with TestClient(backend.main.app) as test_client:
        yield test_client
    backend.main.app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/auth/login/json",
        json={
            "username": "testadmin",
            "password": "correct-horse-battery-staple",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_is_public(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_management_routes_require_authentication(client):
    assert client.get("/api/users/").status_code == 401
    assert client.get("/api/parking-spots/stats/summary").status_code == 401
    assert client.get("/api/ai/configs").status_code == 401


def test_password_is_salted_bcrypt_hash(client):
    db = TestingSessionLocal()
    admin = db.query(Admin).filter(Admin.username == "testadmin").one()
    assert admin.hashed_password != "correct-horse-battery-staple"
    assert admin.hashed_password.startswith(("$2a$", "$2b$", "$2y$"))
    assert admin.verify_password("correct-horse-battery-staple")
    assert not admin.verify_password("wrong-password")
    db.close()


def test_superuser_can_create_admin(client, auth_headers):
    unauthorized = client.post(
        "/api/auth/register",
        json={
            "username": "secondadmin",
            "email": "second@example.com",
            "password": "another-strong-password",
            "is_superuser": False,
        },
    )
    assert unauthorized.status_code == 401

    authorized = client.post(
        "/api/auth/register",
        headers=auth_headers,
        json={
            "username": "secondadmin",
            "email": "second@example.com",
            "password": "another-strong-password",
            "is_superuser": False,
        },
    )
    assert authorized.status_code == 201
    assert authorized.json()["is_superuser"] is False


def test_authenticated_parking_flow_and_static_routes(client, auth_headers):
    user_response = client.post(
        "/api/users/",
        headers=auth_headers,
        json={
            "username": "自动测试用户",
            "phone": "13000000999",
            "license_plate": "TEST-999",
            "vehicle_size": "MEDIUM",
            "is_special_needs": False,
        },
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    spot_response = client.post(
        "/api/parking-spots/",
        headers=auth_headers,
        json={
            "spot_number": "T-001",
            "floor": 1,
            "zone": "T",
            "size": "MEDIUM",
            "is_special_needs": False,
        },
    )
    assert spot_response.status_code == 201

    stats = client.get("/api/parking-spots/stats/summary", headers=auth_headers)
    assert stats.status_code == 200
    assert stats.json()["total_spots"] == 1

    assignment = client.post(
        f"/api/parking-spots/smart-assign/{user_id}",
        headers=auth_headers,
    )
    assert assignment.status_code == 200

    db = TestingSessionLocal()
    assigned = db.get(backend.database.ParkingSpot, assignment.json()["spot_id"])
    assert assigned.status == ParkingStatus.OCCUPIED
    db.close()


def test_historical_baseline_is_deterministic_without_data(client, auth_headers):
    first = client.post(
        "/api/ai/traffic-predictions/generate?days_ahead=2",
        headers=auth_headers,
    )
    second = client.post(
        "/api/ai/traffic-predictions/generate?days_ahead=2",
        headers=auth_headers,
    )
    assert first.status_code == 200
    assert second.status_code == 200

    predictions = client.get(
        "/api/ai/traffic-predictions?days_ahead=2",
        headers=auth_headers,
    )
    assert predictions.status_code == 200
    assert all(item["predicted_volume"] == 0 for item in predictions.json())
    assert all(item["confidence"] == 0.0 for item in predictions.json())


def _create_user_and_spot(client, auth_headers, suffix):
    user_response = client.post(
        "/api/users/",
        headers=auth_headers,
        json={
            "username": f"流程测试用户{suffix}",
            "phone": f"1300000{int(suffix):04d}",
            "license_plate": f"FLOW-{suffix}",
            "vehicle_size": "MEDIUM",
            "is_special_needs": False,
        },
    )
    assert user_response.status_code == 201

    spot_response = client.post(
        "/api/parking-spots/",
        headers=auth_headers,
        json={
            "spot_number": f"FLOW-{suffix}",
            "floor": 1,
            "zone": "F",
            "size": "MEDIUM",
            "is_special_needs": False,
        },
    )
    assert spot_response.status_code == 201
    return user_response.json()["id"], spot_response.json()["id"]


def test_parking_record_entry_and_exit_release_the_space(client, auth_headers):
    user_id, spot_id = _create_user_and_spot(client, auth_headers, "1001")

    entry = client.post(
        "/api/parking-records/",
        headers=auth_headers,
        json={"user_id": user_id, "parking_spot_id": spot_id},
    )
    assert entry.status_code == 201
    record_id = entry.json()["id"]

    db = TestingSessionLocal()
    assert db.get(backend.database.ParkingSpot, spot_id).status == ParkingStatus.OCCUPIED
    db.close()

    active = client.get("/api/parking-records/active", headers=auth_headers)
    assert active.status_code == 200
    assert [item["id"] for item in active.json()] == [record_id]

    departure = client.post(
        f"/api/parking-records/{record_id}/exit",
        headers=auth_headers,
    )
    assert departure.status_code == 200

    db = TestingSessionLocal()
    assert db.get(backend.database.ParkingSpot, spot_id).status == ParkingStatus.AVAILABLE
    user = db.get(backend.database.User, user_id)
    assert user.credit_score == 100
    assert user.points == 5
    assert db.query(backend.database.CreditRecord).filter_by(user_id=user_id).count() == 1
    assert db.query(backend.database.PointRecord).filter_by(user_id=user_id).count() == 1
    db.close()


def test_reservation_lifecycle_reserves_and_releases_the_space(client, auth_headers):
    user_id, spot_id = _create_user_and_spot(client, auth_headers, "1002")
    start = datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(hours=2)

    invalid = client.post(
        "/api/reservations/",
        headers=auth_headers,
        json={
            "user_id": user_id,
            "parking_spot_id": spot_id,
            "start_time": end.isoformat(),
            "end_time": start.isoformat(),
        },
    )
    assert invalid.status_code == 400

    created = client.post(
        "/api/reservations/",
        headers=auth_headers,
        json={
            "user_id": user_id,
            "parking_spot_id": spot_id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
    )
    assert created.status_code == 201
    reservation_id = created.json()["id"]

    db = TestingSessionLocal()
    assert db.get(backend.database.ParkingSpot, spot_id).status == ParkingStatus.RESERVED
    db.close()

    cancelled = client.delete(
        f"/api/reservations/{reservation_id}",
        headers=auth_headers,
    )
    assert cancelled.status_code == 204

    db = TestingSessionLocal()
    assert db.get(backend.database.ParkingSpot, spot_id).status == ParkingStatus.AVAILABLE
    db.close()


def test_system_config_crud_and_duplicate_guard(client, auth_headers):
    created = client.post(
        "/api/ai/configs",
        headers=auth_headers,
        json={
            "config_key": "test_threshold",
            "config_value": "10",
            "description": "automated test",
        },
    )
    assert created.status_code == 201

    duplicate = client.post(
        "/api/ai/configs",
        headers=auth_headers,
        json={
            "config_key": "test_threshold",
            "config_value": "20",
        },
    )
    assert duplicate.status_code == 400

    updated = client.put(
        "/api/ai/configs/test_threshold?config_value=15",
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["config_value"] == "15"

    deleted = client.delete(
        "/api/ai/configs/test_threshold",
        headers=auth_headers,
    )
    assert deleted.status_code == 204
    assert (
        client.get("/api/ai/configs/test_threshold", headers=auth_headers).status_code
        == 404
    )
