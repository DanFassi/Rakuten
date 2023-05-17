from pymongo import MongoClient
import base64
import pandas as pd

#****************************
#Rajouter variable d'environnement pour :
#login (secret)
#mdp (secret)
#collection (secret)
#logs (secret)
#trigger (configmap)


def mongo_trigger():
    #recuperation des variables d'environnements
    trigger = 200
    login = 'RGFuVXNlcg=='
    mdp = 'bXlwdw=='

    #connection à la BDD et extraction des informations
    ATLAS_URI="mongodb+srv://{login}:{pw}@clusterdan.lpuyh34.mongodb.net/test".format(
        login= base64.b64decode(login).decode("utf-8"), 
        pw = base64.b64decode(mdp).decode("utf-8")
        )
    DB_NAME="RAKUTEN_logs"
    logs = "logs"
    mongodb_client = MongoClient(ATLAS_URI)
    database = mongodb_client[DB_NAME]
    mongo_df = pd.DataFrame(list(database[logs].find({})))
    mongodb_client.close()

    #Verification de la condition de trigger (nb de lignes UNIQUES validé dans la BDD multiple du nombre "trigger")
    mongo_df[mongo_df["validation"] == "yes"]
    validated_df = mongo_df[mongo_df["validation"] == "yes"]
    validated_df = validated_df.drop_duplicates(["designation","description","prediction"])
    
    nb_yes = len(validated_df)    
    if nb_yes % trigger ==0 :
        return True
    else:
        return False
   

def training_data_update():
    #recuperation des variables d'environnements
    login = 'RGFuVXNlcg=='
    mdp = 'bXlwdw=='

    #connection à la BDD et extraction des informations
    ATLAS_URI="mongodb+srv://{login}:{pw}@clusterdan.lpuyh34.mongodb.net/test".format(
        login= base64.b64decode(login).decode("utf-8"), 
        pw = base64.b64decode(mdp).decode("utf-8")
        )
    DB_NAME="RAKUTEN_logs"
    logs = "logs"
    mongodb_client = MongoClient(ATLAS_URI)
    database = mongodb_client[DB_NAME]
    mongo_df  = pd.DataFrame(list(database[logs].find({})))

    #processing des données pour mettre à jour les fichiers de features et de targets d'entrainement
    validated_df = mongo_df[mongo_df["validation"] == "yes"]
    validated_df = validated_df.drop_duplicates(["designation","description","prediction"])

    update_X = validated_df[["designation","description"]]
    update_y = validated_df["prediction"].rename("prdtypecode")

    X_df = pd.read_csv("X.csv",index_col = 0)
    updated_X_df = pd.concat([X_df,update_X]).reset_index(drop=True)
    updated_X_df.to_csv("X.csv")

    y_df = pd.read_csv("Y.csv",index_col = 0)
    updated_y_df = pd.concat([y_df,update_y]).reset_index(drop=True) 	
    updated_y_df.to_csv("Y.csv")

    #suppression des données présent dans mango pour eviter de futurs doublons:


training_data_update()