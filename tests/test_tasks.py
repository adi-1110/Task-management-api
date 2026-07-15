from tests.helpers import register_user, login_user


def create_project(client):
    register_user(
        client,
        "Admin",
        "taskadmin@test.com",
        "Password123"
    )

    token = login_user(
        client,
        "taskadmin@test.com",
        "Password123"
    )

    response = client.post(
        "/projects",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Task Project",
            "description": "Testing Tasks"
        }
    )

    return token, response.json()["id"]

def test_create_task(client):
    token, project_id = create_project(client)

    response = client.post(
        f"/projects/{project_id}/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Write Tests",
            "description": "Implement pytest",
            "priority": "high"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Write Tests"
    assert data["priority"] == "high"

def test_filter_tasks_by_status(client):
    token, project_id = create_project(client)

    client.post(
        f"/projects/{project_id}/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Task 1",
            "status": "todo"
        }
    )

    client.post(
        f"/projects/{project_id}/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Task 2",
            "status": "done"
        }
    )

    response = client.get(
        f"/projects/{project_id}/tasks?status=todo",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "todo"

def test_update_task(client):
    token, project_id = create_project(client)

    response = client.post(
        f"/projects/{project_id}/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Old",
            "priority": "low"
        }
    )

    task_id = response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Updated",
            "priority": "high"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated"
    assert data["priority"] == "high"
def test_change_task_status(client):
    token, project_id = create_project(client)

    response = client.post(
        f"/projects/{project_id}/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Status Test"
        }
    )

    task_id = response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "done"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"

def test_delete_task(client):
    token, project_id = create_project(client)

    response = client.post(
        f"/projects/{project_id}/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Delete Me"
        }
    )

    task_id = response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"