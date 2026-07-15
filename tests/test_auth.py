

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Aditya",
            "email": "aditya@test.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Aditya"
    assert data["email"] == "aditya@test.com"
    assert "id" in data

def test_register_duplicate_email(client):
    user = {
        "name": "Aditya",
        "email": "duplicate@test.com",
        "password": "Password123"
    }

    # First registration should succeed
    response = client.post("/auth/register", json=user)
    assert response.status_code == 201

    # Second registration with the same email
    response = client.post("/auth/register", json=user)

    print(response.status_code)
    print(response.json())

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "status_code": 400,
        "message": "Email already registered"
    }

def test_login_success(client):
    user = {
        "name": "Login User",
        "email": "login@test.com",
        "password": "Password123"
    }

    # Register user
    response = client.post("/auth/register", json=user)
    assert response.status_code == 201

    # Login
    response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    user = {
        "name": "Wrong Password",
        "email": "wrong@test.com",
        "password": "Password123"
    }

    client.post("/auth/register", json=user)

    response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401
    assert data["message"] == "Invalid email or password"

def test_login_unknown_user(client):
    response = client.post(
            "/auth/login",
        data={
            "username": "nouser@test.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401
    assert data["message"] == "Invalid email or password"

def test_protected_route_without_token(client):
    response = client.get("/projects")

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401

def test_protected_route_with_token(client):
    user = {
        "name": "Protected User",
        "email": "protected@test.com",
        "password": "Password123"
    }

    # Register
    client.post("/auth/register", json=user)

    # Login
    login = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"]
        }
    )

    token = login.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/projects",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0
