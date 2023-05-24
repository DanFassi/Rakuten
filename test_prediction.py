from Pipeline_prediction import prediction , text_processing
import numpy as np
import joblib

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
def test_size():
    assert len(vectorizer.vocabulary_) == X.shape[1]

#Verification de la nature de l'object obtenu en sortie de la fonction de transformation
#attendu : objet de type Numpy Matrix
def test_matrix_type():
    assert type(X) == type(np.matrix([0,0]))

#verification de la coherence des valeurs présente dans la matrice :
#attendu : le nombre maximum d'itération d'un mot enregistré dans le CountVectorizer ne doit pas être supérieur au nombre de mot de la phrase 

def test_vector_size():
    assert (np.max(X) < len((title +" "+ desc).split(" "))) == True


#Verification de la prédiction pour un object de type "livre":
#attendu : code 2403
def test_predict():
    result = prediction(X)
    assert result["PrductCODE"] == str(2403)
