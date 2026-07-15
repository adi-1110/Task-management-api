from tests.helpers import register_user, login_user


def test_create_project(client):
    register_user(
        client,
        "Admin",
        "admin@test.com",
        "Password123"
    )

    token = login_user(
        client,
        "admin@test.com",
        "Password123"
    )

    response = client.post(
        "/projects",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Backend API",
            "description": "Task management project"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Backend API"
    assert data["description"] == "Task management project"




def test_member_cannot_update_project(client):
    # Register admin
    register_user(
        client,
        "Admin",
        "admin@test.com",
        "Password123"
    )

    admin_token = login_user(
        client,
        "admin@test.com",
        "Password123"
    )

    # Register member
    register_user(
        client,
        "Member",
        "member@test.com",
        "Password123"
    )

    # Admin creates project
    response = client.post(
        "/projects",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "name": "RBAC Project",
            "description": "Testing RBAC"
        }
    )

    assert response.status_code == 200

    project_id = response.json()["id"]

    # Admin adds member
    response = client.post(
        f"/projects/{project_id}/members",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "email": "member@test.com",
            "role": "member"
        }
    )

    assert response.status_code == 200

    # Member logs in
    member_token = login_user(
        client,
        "member@test.com",
        "Password123"
    )

    # Member tries to update project
    response = client.put(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {member_token}"
        },
        json={
            "name": "Hacked Project",
            "description": "Should not work"
        }
    )

    assert response.status_code == 403

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 403
    assert data["message"] == "Admin access required"

def test_admin_can_update_project(client):
    register_user(client, "Admin", "admin_update@test.com", "Password123")

    token = login_user(client, "admin_update@test.com", "Password123")

    response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Old Name",
            "description": "Old Description"
        }
    )

    project_id = response.json()["id"]

    response = client.put(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Name",
            "description": "New Description"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "New Name"
    assert data["description"] == "New Description"

def test_member_cannot_delete_project(client):
    register_user(client, "Admin", "admin_delete@test.com", "Password123")
    admin_token = login_user(client, "admin_delete@test.com", "Password123")

    register_user(client, "Member", "member_delete@test.com", "Password123")

    response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Delete Test",
            "description": "RBAC"
        }
    )

    project_id = response.json()["id"]

    client.post(
        f"/projects/{project_id}/members",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "member_delete@test.com",
            "role": "member"
        }
    )

    member_token = login_user(client, "member_delete@test.com", "Password123")

    response = client.delete(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {member_token}"}
    )

    assert response.status_code == 403

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 403
    assert data["message"] == "Admin access required"

def test_admin_can_delete_project(client):
    register_user(client, "Admin", "admin_final@test.com", "Password123")

    token = login_user(client, "admin_final@test.com", "Password123")

    response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Delete Me",
            "description": "Temporary"
        }
    )

    project_id = response.json()["id"]

    response = client.delete(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204