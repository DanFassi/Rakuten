from Pipeline_prediction import prediction , text_processing
import numpy as np
import joblib
import pandas as pd
import datetime

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

output = '''\n
****************************************************************************
****************** Tests unitaires du {} ******************
****************************************************************************
Tests unitaires du pipeline de prédiction\n
'''.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

#ATTENTION CHANGER CHEMIN FICHIER POUR LINUX / DOCKER
with open('logs/units_test.txt', 'a') as file:
    file.write(output)
    for i in checklist_dict.items():
        file.write((str(i[0]) + " : " + str(i[1]) + "\n"))
    #si l'ensemble des 4 tests précédents sont ok alors on considere la partie prédiction comme fonctionnelle
    file.write("-----------------------------")
    if sum(checklist_dict.values()) == 4:
        file.write("\nPipeline prédiction : OK")
    else:
        file.write("\nPipeline prédiction : NOT OK") 
