from app import dev_server_options


def test_dev_server_defaults_to_no_debug_on_localhost(monkeypatch):
    for name in ("FLASK_DEBUG", "FLASK_HOST", "FLASK_PORT"):
        monkeypatch.delenv(name, raising=False)
    assert dev_server_options() == {"host": "127.0.0.1", "port": 5000, "debug": False}


def test_dev_server_debug_only_when_explicitly_enabled(monkeypatch):
    monkeypatch.setenv("FLASK_DEBUG", "1")
    assert dev_server_options()["debug"] is True
    monkeypatch.setenv("FLASK_DEBUG", "true")
    assert dev_server_options()["debug"] is False
