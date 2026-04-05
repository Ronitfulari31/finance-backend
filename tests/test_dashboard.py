from tests.conftest import make_user, login_as, auth_headers

def _seed_records(client, token):
    """Helper to create a few records so dashboard queries have data."""
    client.post("/records", headers=auth_headers(token), json={"amount": 3000, "type": "income",  "category": "Salary",    "date": "2024-03-01"})
    client.post("/records", headers=auth_headers(token), json={"amount": 500,  "type": "expense", "category": "Rent",      "date": "2024-03-05"})
    client.post("/records", headers=auth_headers(token), json={"amount": 200,  "type": "expense", "category": "Food",      "date": "2024-03-10"})
    client.post("/records", headers=auth_headers(token), json={"amount": 1000, "type": "income",  "category": "Freelance", "date": "2024-02-15"})


def test_viewer_can_access_summary(client, db):
    make_user(db, email="admin@test.com", role="admin")
    make_user(db, email="viewer@test.com", role="viewer")
    admin_token = login_as(client, "admin@test.com")
    _seed_records(client, admin_token)
    viewer_token = login_as(client, "viewer@test.com")
    resp = client.get("/dashboard/summary", headers=auth_headers(viewer_token))
    assert resp.status_code == 200


def test_summary_values_are_correct(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    _seed_records(client, token)
    resp = client.get("/dashboard/summary", headers=auth_headers(token))
    body = resp.json()
    assert float(body["total_income"]) == 4000.0
    assert float(body["total_expenses"]) == 700.0
    assert float(body["net_balance"]) == 3300.0
    assert body["total_records"] == 4


def test_by_category_returns_income_and_expenses(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    _seed_records(client, token)
    resp = client.get("/dashboard/by-category", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "income" in body
    assert "expenses" in body
    income_categories = [i["category"] for i in body["income"]]
    assert "Salary" in income_categories


def test_trends_endpoint(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    _seed_records(client, token)
    resp = client.get("/dashboard/trends", headers=auth_headers(token))
    assert resp.status_code == 200
    assert "trends" in resp.json()


def test_recent_activity(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    _seed_records(client, token)
    resp = client.get("/dashboard/recent", headers=auth_headers(token))
    assert resp.status_code == 200
    records = resp.json()["records"]
    assert len(records) == 4
    assert records[0]["date"] >= records[-1]["date"]


def test_unauthenticated_dashboard_rejected(client, db):
    resp = client.get("/dashboard/summary")
    assert resp.status_code == 401


def test_deleted_records_excluded_from_summary(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    _seed_records(client, token)

    records_resp = client.get("/records", headers=auth_headers(token))
    first_income = next(r for r in records_resp.json()["records"] if r["type"] == "income")
    client.delete(f"/records/{first_income['id']}", headers=auth_headers(token))

    summary = client.get("/dashboard/summary", headers=auth_headers(token)).json()
    assert float(summary["total_income"]) < 4000.0
