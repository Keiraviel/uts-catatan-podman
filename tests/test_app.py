import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(db_path=str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_create_read(client):
    client.post("/tambah", data={"judul": "Belajar", "isi": "Podman CI/CD"})
    r = client.get("/")
    assert b"Belajar" in r.data and b"Podman CI/CD" in r.data


def test_update(client):
    client.post("/tambah", data={"judul": "Lama", "isi": "x"})
    client.post("/update/1", data={"judul": "Baru", "isi": "y"})
    r = client.get("/")
    assert b"Baru" in r.data and b"Lama" not in r.data


def test_delete(client):
    client.post("/tambah", data={"judul": "Hapus saya", "isi": "x"})
    client.post("/hapus/1")
    assert b"Hapus saya" not in client.get("/").data
