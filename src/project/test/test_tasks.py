import pytest
from starlette import status


def test_get_tasks(client, auth_header, service):
    response = client.get("/tasks/", headers=auth_header)
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert len(tasks) == 1


def test_get_as_non_authorized(client):
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_task(client, auth_header):
    payload = {
        "title": "Test Task",
        "status": "Pending",
        "description": "Test Task Description",
        "priority": 1,
    }
    response = client.post("/tasks/", json=payload, headers=auth_header)
    assert response.status_code == status.HTTP_201_CREATED


def test_create_task_as_non_authorized(client):
    response = client.post("/tasks/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
