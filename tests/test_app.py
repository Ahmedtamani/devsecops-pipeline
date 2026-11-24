import pytest

from app.main import app, init_db


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["DATABASE"] = str(tmp_path / "test.db")
    init_db()
    with app.test_client() as client:
        yield client


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_all_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.get_json()) == 3


def test_filter_users_by_name(client):
    response = client.get("/users?name=alice")
    assert response.get_json() == [{"id": 1, "name": "alice", "role": "admin"}]


def test_get_user_by_id(client):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "alice"


def test_unknown_user_returns_404(client):
    response = client.get("/users/99")
    assert response.status_code == 404
    assert response.get_json() == {"error": "not found"}


def test_sql_injection_payload_is_treated_as_data(client):
    response = client.get("/users", query_string={"name": "' OR '1'='1"})
    assert response.status_code == 200
    assert response.get_json() == []