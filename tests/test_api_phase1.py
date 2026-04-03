def get_token(client, username, password):
    response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_auth_login_and_current_user(client):
    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert login.status_code == 200
    token = login.json().get("access_token")
    assert token

    me = client.get("/users/me", headers=auth_headers(token))
    assert me.status_code == 200
    assert me.json()["username"] == "admin"


def test_auth_rejects_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_unauthorized_requests_return_401(client):
    assert client.get("/users/me").status_code == 401
    assert client.get("/transactions/").status_code == 401
    assert client.get("/summary/").status_code == 401


def test_rbac_admin_and_non_admin_for_users_endpoint(client):
    admin_token = get_token(client, "admin", "admin123")
    alice_token = get_token(client, "alice", "alice123")

    admin_users = client.get("/users/", headers=auth_headers(admin_token))
    assert admin_users.status_code == 200
    assert len(admin_users.json()) == 3

    alice_users = client.get("/users/", headers=auth_headers(alice_token))
    assert alice_users.status_code == 403


def test_transaction_crud_filter_and_admin_delete(client):
    admin_token = get_token(client, "admin", "admin123")
    alice_token = get_token(client, "alice", "alice123")

    created = client.post(
        "/transactions/",
        headers=auth_headers(alice_token),
        json={
            "amount": 99.5,
            "type": "expense",
            "category": "Testing",
            "date": "2025-02-01",
            "notes": "phase-1",
        },
    )
    assert created.status_code == 201
    created_id = created.json()["id"]

    filtered = client.get(
        "/transactions/?type=expense&category=Test&page=1&page_size=10",
        headers=auth_headers(alice_token),
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] >= 1

    fetched = client.get(f"/transactions/{created_id}", headers=auth_headers(alice_token))
    assert fetched.status_code == 200

    updated = client.patch(
        f"/transactions/{created_id}",
        headers=auth_headers(alice_token),
        json={"notes": "phase-1-updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["notes"] == "phase-1-updated"

    delete_by_owner = client.delete(
        f"/transactions/{created_id}",
        headers=auth_headers(alice_token),
    )
    assert delete_by_owner.status_code == 403

    delete_by_admin = client.delete(
        f"/transactions/{created_id}",
        headers=auth_headers(admin_token),
    )
    assert delete_by_admin.status_code == 204

    deleted_fetch = client.get(f"/transactions/{created_id}", headers=auth_headers(admin_token))
    assert deleted_fetch.status_code == 404


def test_summary_scoping_admin_vs_regular_user(client):
    admin_token = get_token(client, "admin", "admin123")
    alice_token = get_token(client, "alice", "alice123")

    admin_summary = client.get("/summary/", headers=auth_headers(admin_token))
    alice_summary = client.get("/summary/", headers=auth_headers(alice_token))

    assert admin_summary.status_code == 200
    assert alice_summary.status_code == 200

    admin_count = admin_summary.json()["transaction_count"]
    alice_count = alice_summary.json()["transaction_count"]

    assert admin_count > alice_count


def test_validation_errors_for_transactions_and_dates(client):
    admin_token = get_token(client, "admin", "admin123")

    invalid_create = client.post(
        "/transactions/",
        headers=auth_headers(admin_token),
        json={
            "amount": 0,
            "type": "expense",
            "category": "Invalid",
            "date": "2025-02-02",
        },
    )
    assert invalid_create.status_code == 422

    bad_date_range = client.get(
        "/transactions/?date_from=2025-03-01&date_to=2025-02-01",
        headers=auth_headers(admin_token),
    )
    assert bad_date_range.status_code == 400
