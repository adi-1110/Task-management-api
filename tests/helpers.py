def register_user(client, name, email, password):
    return client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )


def login_user(client, email, password):
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    return response.json()["access_token"]