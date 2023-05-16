from Pipeline_entrainement import dataframe_processing , MLmodel , target_processing, version_saving, model_selection
import numpy as np
import joblib
import pandas as pd
import os
import shutil

##############################################################################################################################
#################################### Unit Test pour la partie de ré-entrainement #############################################
##############################################################################################################################

#importation d'une partie du dataframe pour effectier un test rapide
df = pd.read_csv("X.csv", index_col = 0, skipfooter= 84000)
y = pd.read_csv("Y.csv", index_col = 0, skipfooter= 84000)

#processing des features et des targets
X2, vectorizer =  dataframe_processing(df)
y, le = target_processing(y)

#entrainement du model et prédiction de la premiere ligne du donneé)
model, history = MLmodel(X2,y)
pred_class = np.argmax(model.predict(X2[0]), axis=-1)

checklist_training = {}

#Verification de la bonne dimension du text transformé
#attendu : valeur 1 égale à la taille du dataframe de test , valeur 2 égale à la taille du dictionnaire de l'object countvectorizer utiliser lors de l'entrainement 
try:
    if len(vectorizer.vocabulary_) == X2.shape[1] and len(df) == X2.shape[0]:
        checklist_training["countvectorizer_size"] = 1
    else:
        checklist_training["countvectorizer_size"] = 0
except:
    checklist_training["countvectorizer_size"] = 0

#Verification de la nature de l'object obtenu en sortie de la fonction de transformation
#attendu : objet de type Numpy Matrix
try:
    if type(X2) == type(np.matrix([0,0])):
        checklist_training["object_type"] = 1
    else:
        checklist_training["object_type"] = 0
except:
    checklist_training["object_type"] = 0

#Verification que la prédiction fait bien partie des valeurs attendues
#attendu : valeur prédite présente dans la liste des valeurs de targets
try:
    if le.inverse_transform(pred_class)[0] in le.inverse_transform(y["prdtypecode"]):
        checklist_training["format_pred"] = 1
    else:
        checklist_training["format_pred"] = 0
except:
    checklist_training["format_pred"] = 0


#Verification que la selection du model le plus performant à bien été.
#attendu : présence d'une valeur booléenne à la sortie de lafonction model_selection
try: 
    if isinstance(model_selection(history),bool):
        checklist_training["model_selection"] = 1
    else:
        checklist_training["model_selection"] = 0
except:
    checklist_training["model_selection"] = 0


#execute la fonction permettant de sauvegarder les données. Si une erreur survient, des logs de non execution sont enregistrés 
try:
    new_version = version_saving(vectorizer, le, model, history)
except:
    checklist_training["log_record"] = 0
    checklist_training["CV_save"] = 0
    checklist_training["LE_save"] = 0
    checklist_training["model_save"] = 0

#Les tests suivants vérifie la présence des logs ainsi que des nouveau fichier créer, et supprime ceux issues du test.
#--------------------------------------------------------------------------------------------------------------------
df = pd.read_csv("versions\\model\\model_training_history.csv",index_col = 0)
if new_version == df["version"].iloc[-1]:
    checklist_training["log_record"] = 1
    df1=df.drop(df.index[-10:])
    df1.to_csv("versions\\model\\model_training_history.csv")       
else:
    checklist_training["log_record"] = 0

if os.path.exists("versions\\count_vectorizer\\Rakuten_CountVectorizer_v{}.sav".format(new_version)):
    checklist_training["CV_save"] = 1
    os.remove("versions\\count_vectorizer\\Rakuten_CountVectorizer_v{}.sav".format(new_version))
else:
    checklist_training["CV_save"] = 0    

if os.path.exists("versions\\label_encoder\\Rakuten_LabelEncoder_v{}.sav".format(new_version)):
    checklist_training["LE_save"] = 1
    os.remove("versions\\label_encoder\\Rakuten_LabelEncoder_v{}.sav".format(new_version))
else:
    checklist_training["LE_save"] = 0

if os.path.exists("versions\\model\\Rakuten_model_v{}".format(new_version)):
    checklist_training["model_save"] = 1
    shutil.rmtree("versions\\model\\Rakuten_model_v{}".format(new_version))
else:
    checklist_training["model_save"] = 0

#--------------------------------------------------------------------------------------------------------------------

#Enregistrement des données dans un fichier logs
output = '''\n
***********************************************
Tests unitaires du pipeline d'entrainement\n
'''

with open('logs/units_test.txt', 'a') as file:
    
    file.write(output)
    for i in checklist_training.items():
        file.write((str(i[0]) + " : " + str(i[1]) + "\n"))
    #si l'ensemble des 3 tests précédents sont ok alors on considere la partie entrainement comme fonctionnelle
    file.write("-----------------------------")
    if sum(checklist_training.values()) == 8:
        file.write("\nPipeline entrainement : OK")
    else:
        file.write("\nPipeline entrainement : NOT OK") 
