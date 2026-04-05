from tests.conftest import make_user, login_as, auth_headers

def test_admin_can_list_users(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = client.get("/users", headers=auth_headers(token))
    assert resp.status_code == 200
    assert "users" in resp.json()


def test_viewer_cannot_list_users(client, db):
    make_user(db, email="viewer@test.com", role="viewer")
    token = login_as(client, "viewer@test.com")
    resp = client.get("/users", headers=auth_headers(token))
    assert resp.status_code == 403


def test_analyst_cannot_list_users(client, db):
    make_user(db, email="analyst@test.com", role="analyst")
    token = login_as(client, "analyst@test.com")
    resp = client.get("/users", headers=auth_headers(token))
    assert resp.status_code == 403


def test_admin_can_create_user(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = client.post("/users", headers=auth_headers(token), json={
        "name": "New Person",
        "email": "new@test.com",
        "password": "newpass1",
        "role": "viewer"
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "new@test.com"


def test_duplicate_email_rejected(client, db):
    make_user(db, email="admin@test.com", role="admin")
    make_user(db, email="existing@test.com", role="viewer")
    token = login_as(client, "admin@test.com")
    resp = client.post("/users", headers=auth_headers(token), json={
        "name": "Dupe",
        "email": "existing@test.com",
        "password": "password1",
        "role": "viewer"
    })
    assert resp.status_code == 409


def test_admin_can_update_user_role(client, db):
    admin = make_user(db, email="admin@test.com", role="admin")
    target = make_user(db, email="target@test.com", role="viewer")
    token = login_as(client, "admin@test.com")
    resp = client.patch(f"/users/{target.id}", headers=auth_headers(token), json={"role": "analyst"})
    assert resp.status_code == 200
    assert resp.json()["role"] == "analyst"


def test_admin_can_deactivate_user(client, db):
    make_user(db, email="admin@test.com", role="admin")
    target = make_user(db, email="target@test.com", role="viewer")
    token = login_as(client, "admin@test.com")
    resp = client.patch(f"/users/{target.id}", headers=auth_headers(token), json={"status": "inactive"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "inactive"


def test_get_nonexistent_user_returns_404(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = client.get("/users/99999", headers=auth_headers(token))
    assert resp.status_code == 404


def test_admin_can_delete_user(client, db):
    make_user(db, email="admin@test.com", role="admin")
    target = make_user(db, email="bye@test.com", role="viewer")
    token = login_as(client, "admin@test.com")
    resp = client.delete(f"/users/{target.id}", headers=auth_headers(token))
    assert resp.status_code == 200
    get_resp = client.get(f"/users/{target.id}", headers=auth_headers(token))
    assert get_resp.status_code == 404


def test_short_password_rejected(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = client.post("/users", headers=auth_headers(token), json={
        "name": "Bad Pass",
        "email": "badpass@test.com",
        "password": "abc",  
        "role": "viewer"
    })
    assert resp.status_code == 422


def test_pagination_params(client, db):
    make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = client.get("/users?page=1&limit=5", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["limit"] == 5


def test_admin_cannot_delete_self(client, db):
    admin = make_user(db, email="admin@test.com", role="admin")
    token = login_as(client, "admin@test.com")
    resp = client.delete(f"/users/{admin.id}", headers=auth_headers(token))
    assert resp.status_code == 409
    assert "cannot delete your own account" in resp.json()["detail"]
