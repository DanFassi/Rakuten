from dags.Pipeline_entrainement import dataframe_processing , MLmodel , target_processing, version_saving, model_selection
import numpy as np
import joblib
import pandas as pd
import os
import shutil

##############################################################################################################################
#################################### Unit Test pour la partie de ré-entrainement #############################################
##############################################################################################################################
if os.getenv("MY_DOCKER_PATH") is None:
    my_path = ""
else:
    my_path = os.getenv("MY_DOCKER_PATH") + "/"


#importation d'une partie du dataframe pour effectier un test rapide
df = pd.read_csv("X.csv", skipfooter= 84000, engine = 'python')
y = pd.read_csv("Y.csv", index_col = 0, skipfooter= 84000, engine = 'python')

#processing des features et des targets
X2, vectorizer =  dataframe_processing(df)
y, le = target_processing(y)

#entrainement du model et prédiction de la premiere ligne du donneé)
model, history = MLmodel(X2,y)
pred_class = np.argmax(model.predict(X2[0]), axis=-1)

checklist_training = {}

#Verification de la bonne dimension du text transformé
#attendu : valeur 1 égale à la taille du dataframe de test , valeur 2 égale à la taille du dictionnaire de l'object countvectorizer utiliser lors de l'entrainement 
def test_vectorizer_size():
    assert len(vectorizer.vocabulary_) == X2.shape[1] and len(df) == X2.shape[0]

#Verification de la nature de l'object obtenu en sortie de la fonction de transformation
#attendu : objet de type Numpy Matrix
def test_vectorizer_type():
    assert type(X2) == type(np.matrix([0,0]))

#Verification que la prédiction fait bien partie des valeurs attendues
#attendu : valeur prédite présente dans la liste des valeurs de targets
def test_labelencoder_values():
    assert (le.inverse_transform(pred_class)[0] in le.inverse_transform(y["prdtypecode"])) == True


#Verification que la selection du model le plus performant à bien été.
#attendu : présence d'une valeur booléenne à la sortie de lafonction model_selection
def test_check_past_performance():
    assert isinstance(model_selection(history),bool) == True


#execute la fonction permettant de sauvegarder les données. Si une erreur survient, des logs de non execution sont enregistrés 
#new_version = version_saving(vectorizer, le, model, history)

new_version = version_saving(vectorizer, le, model, history)

    #Les tests suivants vérifie la présence des logs ainsi que des nouveau fichier créer, et supprime ceux issues du test.
    #--------------------------------------------------------------------------------------------------------------------
def test_ecriture_logs():
    df = pd.read_csv(my_path + "versions/model/model_training_history.csv",index_col = 0)
    assert new_version == df["version"].iloc[-1]
    if new_version == df["version"].iloc[-1]:
        df1=df.drop(df.index[-10:])
        df1.to_csv(my_path + "versions/model/model_training_history.csv")       

def test_save_CV():
    assert os.path.exists(my_path + "versions/count_vectorizer/Rakuten_CountVectorizer_v{}.sav".format(new_version)) ==True
    if os.path.exists(my_path + "versions/count_vectorizer/Rakuten_CountVectorizer_v{}.sav".format(new_version)):
        os.remove(my_path + "versions/count_vectorizer/Rakuten_CountVectorizer_v{}.sav".format(new_version))  

def test_save_LE():
    assert os.path.exists(my_path + "versions/label_encoder/Rakuten_LabelEncoder_v{}.sav".format(new_version)) == True
    if os.path.exists(my_path + "versions/label_encoder/Rakuten_LabelEncoder_v{}.sav".format(new_version)):
        os.remove(my_path + "versions/label_encoder/Rakuten_LabelEncoder_v{}.sav".format(new_version))

def test_save_model():
    assert os.path.exists(my_path + "versions/model/Rakuten_model_v{}".format(new_version))
    if os.path.exists(my_path + "versions/model/Rakuten_model_v{}".format(new_version)):
        shutil.rmtree(my_path + "versions/model/Rakuten_model_v{}".format(new_version))

#--------------------------------------------------------------------------------------------------------------------
