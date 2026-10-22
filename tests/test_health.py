from sqlalchemy.exc import OperationalError

from models import db


def test_health_reports_ok_when_database_answers(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


def test_health_reports_503_without_leaking_error(client, monkeypatch):
    def broken_execute(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("secret-host:3306 refused"))

    monkeypatch.setattr(db.session, "execute", broken_execute)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.get_json() == {"status": "error", "database": "unavailable"}
    assert b"secret-host" not in response.data
