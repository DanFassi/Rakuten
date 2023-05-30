import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from api_rak import app  

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_create_user(client):
    # Prepare test data
    form_data = {"username": "testuser", "password": "testpass", "role" : "user"}

    # Send a POST request to create a new user
    response = client.post("/user/creation", data=form_data)

    # Verify the response
    assert response.status_code == HTTP_201_CREATED
    assert "Nouvel utilisateur créée" in response.text

def test_predict(client):
    # Prepare test data
    form_data = {"designation": "Test Designation", "description": "Test Description"}

    # Send a POST request to make a prediction
    response = client.post("/predict", data=form_data)

    # Verify the response
    assert response.status_code == 200

def test_delete_user(client):
    # Prepare test data
    username = "testuser"

    # Send a DELETE request to delete a user
    response =  client.delete("/admin/{}".format(username))

    # Verify the response
    assert response.status_code == HTTP_204_NO_CONTENT

def test_update_user(client):
    # Prepare test data
    username = "testuser"
    user_data = {"role": "user"}

    # Send a PUT request to update a user
    response = client.put("/admin/{}".format(username), json=user_data)

    # Verify the response
    assert response.status_code == 200
    assert response.json()["name"] == username
    assert response.json()["role"] == "user"


def test_update_user_not_found(client):
    # Prepare test data
    username = "nonexistentuser"
    user_data = {"role": "user"}

    # Send a PUT request to update a non-existent user
    response = client.put("/admin/{}".format(username), json=user_data)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert "User with name" in response.text