import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from api_rak import app  
import os

@pytest.fixture
def client():
    """
    Create a test client using the FastAPI app
    """
    with AsyncClient(app=app, base_url="http://localhost:8000", headers={"Authorization": [os.environ["MONGODB_LOG"],
                                                                                           os.environ["MONGODB_PW"],
                                                                                           os.environ["MONGODB_DB_NAME"],
                                                                                           os.environ["MONGODB_DB_COL_USERS"],
                                                                                           os.environ["MONGODB_DB_COL_LOGS"] 
                                                                                           ]
                                                                        }
                    ) as client:
        yield client

@pytest.mark.asyncio
async def test_create_user(client):
    # Prepare test data
    form_data = {"username": "testuser", "password": "testpass"}

    # Send a POST request to create a new user
    response = await client.post("/creation", data=form_data)

    # Verify the response
    assert response.status_code == HTTP_201_CREATED
    assert "Nouvel utilisateur créée" in response.text

@pytest.mark.asyncio
async def test_predict(client):
    # Prepare test data
    form_data = {"designation": "Test Designation", "description": "Test Description"}

    # Send a POST request to make a prediction
    response = await client.post("/predict", data=form_data)

    # Verify the response
    assert response.status_code == 200
    assert "result" in response.text

@pytest.mark.asyncio
async def test_delete_user(client):
    # Prepare test data
    username = "testuser"

    # Send a DELETE request to delete a user
    response = await client.delete(f"/{username}")

    # Verify the response
    assert response.status_code == HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_update_user(client):
    # Prepare test data
    username = "testuser"
    user_data = {"role": "admin"}

    # Send a PUT request to update a user
    response = await client.put(f"/{username}", json=user_data)

    # Verify the response
    assert response.status_code == 200
    assert response.json()["name"] == username
    assert response.json()["role"] == "admin"

@pytest.mark.asyncio
async def test_update_user_not_found(client):
    # Prepare test data
    username = "nonexistentuser"
    user_data = {"role": "admin"}

    # Send a PUT request to update a non-existent user
    response = await client.put(f"/{username}", json=user_data)

    # Verify the response
    assert response.status_code == HTTP_404_NOT_FOUND
    assert "User with name" in response.text