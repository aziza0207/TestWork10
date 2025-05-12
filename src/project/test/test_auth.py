import pytest
from starlette import status
from sqlalchemy import select
from ..models import User


def test_register(db_session, client):
    payload = {"name": "Test Name", "email": "test@example.com", "password": "test123"}

    response = client.post("/auth/register/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    session = db_session
    try:
        db_user = session.scalar(select(User).where(User.email == payload["email"]))
        assert db_user is not None
        assert db_user.name == payload["name"]
        assert db_user.email == payload["email"]
    finally:
        if db_user:
            session.delete(db_user)
            session.commit()
        session.close()


def test_user_already_exists(db_session, client, user):
    payload = {
        "name": user.name,
        "email": user.email,
        "password": "TestPassword",
    }
    response = client.post("/auth/register/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login(user, client):
    payload = {
        "username": user.email,
        "password": "TestPassword",
    }

    response = client.post("/auth/token/", data=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


def get_auth_token(client, email, password):
    response = client.post(
        "/auth/token/",
        data={"username": email, "password": password},
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]
