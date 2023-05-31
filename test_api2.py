import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_200_OK
from api_rak import app  

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

#Requete testant la création d'un utilisateur dans la base
def test_create_user(client):
    form_data = {"username": "testuser", "password": "testpass", "role" : "user"}
    response = client.post("/user/creation", data=form_data)
    assert response.status_code == HTTP_200_OK
    assert "Nouvel utilisateur créée" in response.text


def test_predict(client):
    form_data = {"designation": "Test Designation", "description": "Test Description"}
    response = client.post("/predict", data=form_data)
    assert response.status_code == 200


#Requete testant la maj'un utilisateur dans la base
def test_update_user(client):
    username = "testuser"
    password = "changement"
    user_data = {"name":username, "password" : password, "role": "user"}
    response = client.put("/admin/{}".format(username), json=user_data)
    assert response.status_code == 200
    assert response.json()["name"] == username
    assert response.json()["role"] == "password"
    assert response.json()["role"] == "user"

#Requete supprimant un utilisateur de la base
def test_delete_user(client):
    username = "testuser"
    response =  client.delete("/admin/{}".format(username))
    assert response.status_code == HTTP_204_NO_CONTENT

#Requete testant la réponse si l'on tente de maj un utilisateur qui n'existe pas dans la base
def test_update_user_not_found(client):
    username = "nonexistentuser"
    password = "changement"
    user_data = {"name":username, "password" : password, "role": "user"}
    user_data = {"role": "user"}
    response = client.put("/admin/{}".format(username), json=user_data)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert "User with name" in response.text