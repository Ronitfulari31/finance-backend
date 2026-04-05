from datetime import date
from tests.conftest import make_user, login_as, auth_headers

def _create_record(client, token):
    return client.post("/records", headers=auth_headers(token), json={
        "amount": 1500.00,
        "type": "income",
        "category": "Salary",
        "date": "2024-03-01",
        "notes": "March salary"
    })


def test_admin_can_create_record(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = _create_record(client, token)
    assert resp.status_code == 201
    assert resp.json()["category"] == "Salary"
    assert float(resp.json()["amount"]) == 1500.00


def test_viewer_cannot_create_record(client, db):
    make_user(db, email="viewer@test.com", role="viewer")
    token = login_as(client, "viewer@test.com")
    resp = _create_record(client, token)
    assert resp.status_code == 403


def test_analyst_cannot_create_record(client, db):
    make_user(db, email="analyst@test.com", role="analyst")
    token = login_as(client, "analyst@test.com")
    resp = _create_record(client, token)
    assert resp.status_code == 403


def test_analyst_can_read_records(client, db):
    admin = make_user(db, email="admin@test.com", role="admin")
    make_user(db, email="analyst@test.com", role="analyst")
    admin_token = login_as(client, "admin@test.com")
    _create_record(client, admin_token)
    analyst_token = login_as(client, "analyst@test.com")
    resp = client.get("/records", headers=auth_headers(analyst_token))
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_viewer_cannot_read_records(client, db):
    make_user(db, email="viewer@test.com", role="viewer")
    token = login_as(client, "viewer@test.com")
    resp = client.get("/records", headers=auth_headers(token))
    assert resp.status_code == 403


def test_admin_can_update_record(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    record_id = _create_record(client, token).json()["id"]
    resp = client.patch(f"/records/{record_id}", headers=auth_headers(token), json={"amount": 2000.00})
    assert resp.status_code == 200
    assert float(resp.json()["amount"]) == 2000.00


def test_soft_delete_hides_record(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    record_id = _create_record(client, token).json()["id"]

    del_resp = client.delete(f"/records/{record_id}", headers=auth_headers(token))
    assert del_resp.status_code == 200

    list_resp = client.get("/records", headers=auth_headers(token))
    ids = [r["id"] for r in list_resp.json()["records"]]
    assert record_id not in ids

    get_resp = client.get(f"/records/{record_id}", headers=auth_headers(token))
    assert get_resp.status_code == 404


def test_negative_amount_rejected(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = client.post("/records", headers=auth_headers(token), json={
        "amount": -500,
        "type": "expense",
        "category": "Food",
        "date": "2024-01-01"
    })
    assert resp.status_code == 422


def test_invalid_type_rejected(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = client.post("/records", headers=auth_headers(token), json={
        "amount": 100,
        "type": "profit", 
        "category": "Other",
        "date": "2024-01-01"
    })
    assert resp.status_code == 422


def test_filter_by_type(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    client.post("/records", headers=auth_headers(token), json={"amount": 100, "type": "income", "category": "A", "date": "2024-01-01"})
    client.post("/records", headers=auth_headers(token), json={"amount": 50, "type": "expense", "category": "B", "date": "2024-01-01"})

    resp = client.get("/records?type=income", headers=auth_headers(token))
    assert resp.status_code == 200
    assert all(r["type"] == "income" for r in resp.json()["records"])


def test_pagination(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    for i in range(5):
        client.post("/records", headers=auth_headers(token), json={
            "amount": 100 + i,
            "type": "expense",
            "category": "Food",
            "date": "2024-01-01"
        })
    resp = client.get("/records?page=1&limit=3", headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()["records"]) == 3
    assert resp.json()["total"] == 5
