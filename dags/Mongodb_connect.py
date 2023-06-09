from pymongo import MongoClient
import base64
import pandas as pd
import os
import csv


# Génére une variable non vide si une variable d'environnement concernant le chemin d'accès vers les répertoires est présente
if os.getenv("MY_DOCKER_PATH") is None:
    my_path = ""
else:
    my_path = os.getenv("MY_DOCKER_PATH") + "/"

def mongo_trigger():
    #recuperation des variables d'environnements
    trigger = int(os.getenv("TRAINING_TRIGGER"))
    DB_NAME= os.getenv("MONGODB_DB_NAME")
    logs = os.getenv("MONGODB_DB_COL_LOGS")


    #connection à la BDD et extraction des informations
    ATLAS_URI="mongodb+srv://{login}:{pw}@clusterdan.lpuyh34.mongodb.net/test".format(
        login= base64.b64decode(os.getenv("MONGODB_LOG")).decode("utf-8"), 
        pw = base64.b64decode(os.getenv("MONGODB_PW")).decode("utf-8")
        )

    mongodb_client = MongoClient(ATLAS_URI)
    database = mongodb_client[DB_NAME]
    mongo_df = pd.DataFrame(list(database[logs].find({})))
    mongodb_client.close()

    #Verification de la condition de trigger (nb de lignes UNIQUES validé dans la BDD multiple du nombre "trigger")
    mongo_df[mongo_df["validation"] == "yes"]
    validated_df = mongo_df[mongo_df["validation"] == "yes"]
    validated_df = validated_df.drop_duplicates(["designation","description","prediction"])
    
    nb_yes = len(validated_df)    
    if nb_yes % trigger == 0 :
        return True
    else:
        return False
   

def training_data_update():
    #recuperation des variables d'environnements
    DB_NAME= os.getenv("MONGODB_DB_NAME")
    logs = os.getenv("MONGODB_DB_COL_LOGS")

    #connection à la BDD et extraction des informations
    ATLAS_URI="mongodb+srv://{login}:{pw}@clusterdan.lpuyh34.mongodb.net/test".format(
        login= base64.b64decode(os.getenv("MONGODB_LOG")).decode("utf-8"), 
        pw = base64.b64decode(os.getenv("MONGODB_PW")).decode("utf-8")
        )

    mongodb_client = MongoClient(ATLAS_URI)
    database = mongodb_client[DB_NAME]
    mongo_df  = pd.DataFrame(list(database[logs].find({})))

    #processing des données pour mettre à jour les fichiers de features et de targets d'entrainement
    validated_df = mongo_df[mongo_df["validation"] == "yes"]
    validated_df = validated_df.drop_duplicates(["designation","description","prediction"])

    update_X = validated_df[["designation","description"]]
    update_y = validated_df["prediction"].rename("prdtypecode")

    #Code ci dessous abandonner pour des raisons de limite de mémoire de la machine virtuelle

    #X_df = pd.read_csv(my_path +"X.csv",index_col = 0)
    #updated_X_df = pd.concat([X_df,update_X]).reset_index(drop=True)
    #updated_X_df.to_csv(my_path +"X.csv")

    with open(my_path + 'X.csv', 'a', encoding="utf-8") as f:
        writer = csv.writer(f)
        for index, row in update_X.iterrows():
            writer.writerow(row)

    y_df = pd.read_csv(my_path +"Y.csv",index_col = 0)
    updated_y_df = pd.concat([y_df,update_y]).reset_index(drop=True) 	
    updated_y_df.to_csv(my_path +"Y.csv")

    #attention, des doublons peuvent etre insérer de maniere cumulative dans la BDD puisque on ne supprime pas les doublons déjà existant dans la BDD avec l'ajout des nouvelles lignes (contenant au cumulé les doublons des autres updates)
