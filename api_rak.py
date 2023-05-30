from fastapi import FastAPI, Header, Security, Depends, HTTPException, status, APIRouter, Request, Body, Response,BackgroundTasks
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from pymongo import MongoClient
import json
import requests
import base64
import datetime
import os

from Pipeline_prediction import prediction , text_processing

#ATLAS_URI="mongodb+srv://DanUser:mypw@clusterdan.lpuyh34.mongodb.net/test"
ATLAS_URI="mongodb+srv://{login}:{pw}@clusterdan.lpuyh34.mongodb.net/test".format(login= base64.b64decode(os.getenv("MONGODB_LOG")).decode("utf-8") , pw = base64.b64decode(os.getenv("MONGODB_PW")).decode("utf-8"))
DB_NAME= os.getenv("MONGODB_DB_NAME")
collection = os.getenv("MONGODB_DB_COL_USERS")
logs = os.getenv("MONGODB_DB_COL_LOGS")

#instanciation de l'API
app = FastAPI(title = "API MongoDB", description = "API gérant à la fois les utilisateurs (création, connection, changement et suppression), ainsi que les prédictions du modèle mis en place")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

  
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
router2 = APIRouter()
router3 = APIRouter()


# =============================================================================
# Fonctions API liées à l'inscription et à l'identification
# =============================================================================
current_username = None
current_role = "user"

#requete permettant d'ajouter un nouvel utilisateur ainsi que son mot de passe dans la base
@router.post("/creation", response_description="Creation d'un nouvel utilisateur", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request):
    form_data = await request.form()
    username = form_data["username"]
    password = form_data["password"]   
    user =  {"name" : username,
            "password" : password,
            "role" : "user"
            }  
    new_user = request.app.database[collection].insert_one(user)
    created_user = request.app.database[collection].find_one(
        {"_id": new_user.inserted_id}
    )
    popup_message = "Nouvel utilisateur créé. Vous allez être redirigé vers la page d'accueil dans 2 secondes"

    # Render the pop-up message template
    return templates.TemplateResponse(
        "popup.html",
        {"request": request, "popup_message": popup_message, "redirect_url": "/"},
    )


security = HTTPBasic()
#requete permettant d'obtenir la liste des utilisateurs ainsi que de leurs mot de passe
@router.get("/", response_description="List all user", response_model=List[User])
def list_users(request: Request):
    users = list(request.app.database[collection].find(limit=100))
    return users

#requete verifiant la validité du nom d'utilisateur ainsi que du mot de passe
@router3.post("/login")
def get_current_user(request: Request, background_tasks: BackgroundTasks, credentials: HTTPBasicCredentials = Depends(security), user_agent:str = Header(None)): 
    logbdd =  requests.get(url='http://localhost:8000/user/').json()
    users = {key: value for key, value in zip([d["name"] for d in logbdd], [d["password"] for d in logbdd])}
    username = credentials.username
    if not(users.get(username)) or not(credentials.password == users[username]): #not(pwd_context.verify(credentials.password, users[username])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        global current_username
        current_username = username
        roles = {key: value for key, value in zip([d["name"] for d in logbdd], [d["role"] for d in logbdd])}
        global current_role
        current_role = roles[username] 
        if roles[username] != "admin":
            #global current_role
            #current_role = "user"
            return  templates.TemplateResponse("input.html", {"request": request})
        else:
            #global current_role
            #current_role = "admin"
            return  templates.TemplateResponse("admin.html", {"request": request})


# =============================================================================
# Fonctions API liées à l'interface
# =============================================================================

#requete permettant de naviguer vers la d'accueil
@router3.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    

#requete retournant une prediction en fonction des informations fournit par l'utilisateur, et stock les résultats dans la base logs
@router3.post("/predict", response_class=HTMLResponse)
#def predict(designation : str, description : str,request: Request, username: str = Depends(get_current_user)):
async def predict(request: Request):
    #global current_username
    username = current_username
    form_data = await request.form()
    designation = form_data["designation"]
    description = form_data["description"]   
    pred = prediction(text_processing(designation, description))
    log =  {"date": datetime.datetime.now(),
            "user" : username,
            "designation" : designation,
            "description" : description,
            "prediction" : pred["PrductCODE"],
            "validation" : "no"
            }  
    new_log = request.app.database[logs].insert_one(log)
    created_log = request.app.database[logs].find_one(
        {"_id": new_log.inserted_id}
    )
    app.state.log_id = created_log["_id"]
    result = str(pred["PrductCODE"])
    if current_username is None:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return templates.TemplateResponse("result.html", {"request": request, "result": result})

#requete modifiant la valeur "validation" pour la prédiction venant d'etre effectué, si la requete est appelé
@router3.put("/", response_description="mise à jour du dernier log entré")
def update_user(request: Request):
    log_id = app.state.log_id
    if log_id is not None:
        update_result = request.app.database[logs].update_one(
            {"_id": log_id}, {"$set": {"validation" : "yes"}}
        )
        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"log with log_id {log_id} not found 1")
    if (
        existing_log := request.app.database[logs].find_one({"_id": log_id}, {'_id': 0})
    ) is not None:
        return existing_log
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"log with log_id {log_id} not found 2")

#requete permettant de naviguer vers la page input
@router3.get('/input')
def input(request: Request):
    if current_username is None:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        if current_role != "admin":
            return templates.TemplateResponse("input.html", {"request": request})
        else:
            return  templates.TemplateResponse("admin.html", {"request": request})


#requete permettant de naviguer vers la page inscription
@router3.get('/inscription')
def input(request: Request):
    return templates.TemplateResponse("inscription.html", {"request": request})


# =============================================================================
# Fonctions Amdmin only
# =============================================================================

#requete permettant de supprimer un utilisateur ainsi que son mot de passe dans la base
@router2.delete("/{username}", response_description="Suppression d'un utilisateur")
def delete_user(username: str, request: Request, response: Response):
    delete_result = request.app.database[collection].delete_one({"name": username})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Aucun utilisateur portant ce nom")


#requete permettant de modifier un utilisateur dans la base
@router2.put("/{username}", response_description="mise à jour d'un utilisateur", response_model=User)
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




app.include_router(router, tags=["users"], prefix="/user")
app.include_router(router2, tags=["admin"], prefix="/admin")
app.include_router(router3, tags=["Interface"])
