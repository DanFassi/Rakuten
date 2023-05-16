from pipeline import prediction , text_processing , dataframe_processing , MLmodel
import numpy as np
import joblib
import pandas as pd

##############################################################################################################################
#################################### Unit Test pour la partie prediction #####################################################
##############################################################################################################################
title = "un livre"
desc = "un livre contenant une histoire avec un resumé des personnages un début une fin et une intrigue"

vectorizer = joblib.load("Rakuten_CountVectorizer.sav")
X = text_processing(title,desc)

checklist_dict = {}

#Verification de la bonne dimension du text transformé
#attendu : valeur égale à la taille du dictionnaire de l'object countvectorizer utiliser lors de l'entrainement
if len(vectorizer.vocabulary_) == X.shape[1]:
    checklist_dict["countvectorizer_size"] = 1
else:
    checklist_dict["countvectorizer_size"] = 0

#Verification de la nature de l'object obtenu en sortie de la fonction de transformation
#attendu : objet de type Numpy Matrix
if type(X) == type(np.matrix([0,0])):
    checklist_dict["object_type"] = 1
else:
    checklist_dict["object_type"] = 0

#verification de la coherence des valeurs présente dans la matrice :
#attendu : le nombre maximum d'itération d'un mot enregistré dans le CountVectorizer ne doit pas être supérieur au nombre de mot de la phrase 

if (np.max(X)) < len((title +" "+ desc).split(" ")):
    checklist_dict["matrix_values"] = 1
else:
    checklist_dict["matrix_values"] = 0

print([i for i in np.unique(X, axis =1 )[0]])
print(np.unique(X, axis =1 ))
result = prediction(X)

#Verification de la prédiction pour un object de type "livre":
#attendu : code 2403

if result["PrductCODE"] == str(2403):
    checklist_dict["prediction"] = 1
else:
    checklist_dict["prediction"] = 0


#si l'ensemble des 4 tests précédents sont ok alors on considere la partie prédiction comme fonctionnelle
if sum(checklist_dict.values()) == 4:
    print("Pipeline prédiction OK")



##############################################################################################################################
#################################### Unit Test pour la partie de ré-entrainement #############################################
##############################################################################################################################

#df = pd.DataFrame({"designation": ["un livre", "un jouet"], "description" : ["un livre contenant une histoire avec un resumé des personnages un début une fin et une intrigue","un jouet qui amuse les enfants avec des jeux"]})
#y = pd.DataFrame({"prdtypecode": [2403, 1360]})

df = pd.read_csv("X.csv", index_col = 0, skipfooter= 84000)
y = pd.read_csv("Y.csv", index_col = 0, skipfooter= 84000)

le = joblib.load("Rakuten_LabelEncoder.sav")
y["prdtypecode"] = le.transform(y["prdtypecode"])

X2, vectorizer =  dataframe_processing(df)

checklist_training = {}

#Verification de la bonne dimension du text transformé
#attendu : valeur 1 égale à la taille du dataframe de test , valeur 2 égale à la taille du dictionnaire de l'object countvectorizer utiliser lors de l'entrainement 
if len(vectorizer.vocabulary_) == X2.shape[1] and len(df) == X2.shape[0]:
    checklist_training["countvectorizer_size"] = 1
else:
    checklist_training["countvectorizer_size"] = 0

#Verification de la nature de l'object obtenu en sortie de la fonction de transformation
#attendu : objet de type Numpy Matrix
if type(X2) == type(np.matrix([0,0])):
    checklist_training["object_type"] = 1
else:
    checklist_training["object_type"] = 0

model = MLmodel(X2,y)
pred_class = np.argmax(model.predict(X2[0]), axis=-1)
print(pred_class)