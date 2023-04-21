from fastapi import FastAPI, Header, Security, Depends, HTTPException, status, APIRouter, Request, Body, Response
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from typing import Optional, List
from pymongo import MongoClient
import requests
import uuid
import base64

from pipeline import prediction , text_processing

login = 'RGFuVXNlcg=='
mdp = 'bXlwdw=='

#ATLAS_URI="mongodb+srv://DanUser:mypw@clusterdan.lpuyh34.mongodb.net/test"
ATLAS_URI="mongodb+srv://{login}:{pw}@clusterdan.lpuyh34.mongodb.net/test".format(login= base64.b64decode(login).decode("utf-8") , pw = base64.b64decode(mdp).decode("utf-8"))
DB_NAME="RAKUTEN_logs"
collection = "my_collection"

#instanciation de l'API
app = FastAPI(title = "API MongoDB", description = "API permettant d'effectuer des requetes")

#Demarage de l'API et connection au server MongoDB
@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(ATLAS_URI)
    app.database = app.mongodb_client[DB_NAME]
    
    print("Connected to the MongoDB database!")

#Fermeture de la connection au serveur lors de la fermeture de l'API
@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

#instanciation de la class user pour la récuperation des logins et mdp présent dans la BDD
class User(BaseModel):
    #id: int = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    password : str = Field(...)
    role : str = "user"

router = APIRouter()

#requete permettant d'ajouter un nouvel utilisateur ainsi que son mot de passe dans la base
@router.post("/", response_description="Creation d'un nouvel utilisateur", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(request: Request, user: User = Body(...)):
    user = jsonable_encoder(user)
    new_user = request.app.database[collection].insert_one(user)
    created_user = request.app.database[collection].find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user

#requete permettant de supprimer un utilisateur ainsi que son mot de passe dans la base
@router.delete("/{username}", response_description="Suppression d'un utilisateur")
def delete_user(username: str, request: Request, response: Response):
    delete_result = request.app.database[collection].delete_one({"name": username})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Aucun utilisateur portant ce nom")

#requete permettant de modifier un utilisateur dans la base
@router.put("/{username}", response_description="mise à jour d'un utilisateur", response_model=User)
def update_user(username: str, request: Request, user: User= Body(...)):
    user = {k: v for k, v in user.dict().items() if v is not None}
    if len(user) >= 1:
        update_result = request.app.database[collection].update_one(
            {"name": username}, {"$set": user}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with name {username} not found 1")

    if (
        existing_user := request.app.database[collection].find_one({"name": username})
    ) is not None:
        return existing_user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with name {username} not found 2")



#requete permettant d'obtenir la liste des utilisateurs ainsi que de leurs mot de passe
@router.get("/", response_description="List all user", response_model=List[User])
def list_users(request: Request):
    users = list(request.app.database[collection].find(limit=100))
    return users



app.include_router(router, tags=["users"], prefix="/user")

security = HTTPBasic()

#requete verifiant la validité du nom d'utilisateur ainsi que du mot de pass
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    logbdd =  requests.get(url='http://localhost:8000/user/').json()
    users = {key: value for key, value in zip([d["name"] for d in logbdd], [d["password"] for d in logbdd])}
    username = credentials.username
    if not(users.get(username)) or not(credentials.password == users[username]): #not(pwd_context.verify(credentials.password, users[username])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/login")
def current_user(username: str = Depends(get_current_user)):
    return "Hello {}".format(username)

@app.get("/predict")
def predict(designation : str, description : str,username: str = Depends(get_current_user)):
    pred = prediction(text_processing(designation, description))
    return pred


class Object(BaseModel):
    column1: str
    column2 : str

