from tests.conftest import make_user, auth_headers

def test_login_success(client, db):
    make_user(db, email="alice@test.com", password="secret99")
    resp = client.post("/auth/login", json={"email": "alice@test.com", "password": "secret99"})
    assert resp.status_code == 200
    body = resp.json()
    assert "session_token" in body
    assert body["user"]["email"] == "alice@test.com"


def test_login_wrong_password(client, db):
    make_user(db, email="alice@test.com", password="correct")
    resp = client.post("/auth/login", json={"email": "alice@test.com", "password": "wrong"})
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


def test_login_unknown_email(client, db):
    resp = client.post("/auth/login", json={"email": "ghost@test.com", "password": "abc"})
    assert resp.status_code == 401


def test_login_inactive_user(client, db):
    user = make_user(db, email="disabled@test.com")
    user.status = "inactive"
    db.commit()
    resp = client.post("/auth/login", json={"email": "disabled@test.com", "password": "pass123"})
    assert resp.status_code == 401
    assert "deactivated" in resp.json()["detail"]


def test_logout_success(client, db):
    make_user(db, email="alice@test.com")
    token = client.post("/auth/login", json={"email": "alice@test.com", "password": "pass123"}).json()["session_token"]
    resp = client.post("/auth/logout", headers=auth_headers(token))
    assert resp.status_code == 200
    assert "Logged out" in resp.json()["message"]


def test_logout_then_token_invalid(client, db):
    make_user(db, email="alice@test.com")
    token = client.post("/auth/login", json={"email": "alice@test.com", "password": "pass123"}).json()["session_token"]
    client.post("/auth/logout", headers=auth_headers(token))
    resp = client.get("/dashboard/summary", headers=auth_headers(token))
    assert resp.status_code == 401


def test_no_auth_header_rejected(client, db):
    resp = client.get("/dashboard/summary")
    assert resp.status_code == 401
