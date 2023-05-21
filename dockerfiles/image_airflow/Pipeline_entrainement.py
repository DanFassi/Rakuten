import joblib
import string
import os
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Input


# Génére une variable non vide si une variable d'environnement concernant le chemin d'accès vers les répertoires est présente
if os.getenv("MY_DOCKER_PATH") is None:
    my_path = ""
else:
    my_path = os.getenv("MY_DOCKER_PATH") + "/"

# =============================================================================
# fonctions utilisés pour le processing d'un dataframe:
# =============================================================================
def column_junction(column1,column2):
    if str(column2).lower() =="nan":
        return str(column1)
    else:
        return str(column1) + " " + str(column2)

def remove_punctuation(text):
    punctuationfree="".join([i for i in text if i not in string.punctuation])
    return punctuationfree

def remove_stopwords(text,stopword):
    output= " ".join([word for word in str(text).split() if word not in stopword])
    return output

def stem_words(text,stemmer):
    return " ".join([stemmer.stem(word) for word in text.split()])


# =============================================================================
# Fonctions utilisées pour le réentrainement du model
# =============================================================================

# 1 - features Processing
def dataframe_processing(df):
    df["text"] = df.apply(lambda x : column_junction(x["designation"],x["description"]),axis=1)
    df["text"]= df["text"].str.lower()
    df["text"]= df["text"].apply(lambda x:remove_punctuation(x))
    stopword = stopwords.words('english')
    df["text"]= df["text"].apply(lambda x:remove_stopwords(x,stopword))
    stopword = stopwords.words('french')
    df["text"]= df["text"].apply(lambda x:remove_stopwords(x,stopword))
    stemmer = SnowballStemmer("french")
    df["text"] = df["text"].apply(lambda text: stem_words(text,stemmer))
    vectorizer = CountVectorizer(min_df= 50)
    vectorizer.fit_transform(df["text"])
    X = vectorizer.transform(df["text"]).todense()
    return X , vectorizer

#2 - targets processing
def target_processing(y):
    le = LabelEncoder()
    y["prdtypecode"] = le.fit_transform(y["prdtypecode"])
    return y, le

#3 - definition du model et entrainement
def MLmodel(X,y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=1000)
    input_dim = X_train.shape[1] 
    output_dim = y["prdtypecode"].nunique()

    model = Sequential()
    model.add(Input(shape = (input_dim ), name = "Input"))
    model.add(Dense(30, activation='relu'))
    model.add(Dense(output_dim, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy', 
              optimizer='adam', 
              metrics=['accuracy'])
    model.summary()

    history = model.fit(X_train, y_train,
                    epochs=10,
                    verbose=True,
                    validation_data=(X_test, y_test),
                    batch_size=10)
    return model , history

#4 Comparason de performance avec le modèle en cour (cad le dernier modèle enregistré dans le log) 
def model_selection(new_model_history):
    df = pd.read_csv(my_path + "versions/model/model_training_history.csv",index_col = 0)
    last_model_version = df["version"].iloc[-1]
    last_model_val_accuracy = max(df[df["version"] == last_model_version ]["val_accuracy"])
    new_model_val_accuracy = max(new_model_history.history['val_accuracy'])
    #si la metric d'évaluation du nouveau model est inférieur à celui actuel, on retourne la valeur False sinon True
    if last_model_val_accuracy >= new_model_val_accuracy:
        return False
    else:
        return True

#5 Enregistrement de la nouvelle version du model 
def version_saving(vectorizer, labencoder, model, new_model_history):
    
    #Sauvegarde de l'historique d'entrainement ainsi que du numero de version
    hist_df = pd.read_csv(my_path +"versions/model/model_training_history.csv",index_col = 0)

    #itération du numero de version sur la base du numero de la dernier ligne du fichier log
    new_version = hist_df["version"].iloc[-1]+1

    current_model_hist = pd.DataFrame(new_model_history.history) 
    current_model_hist["version"] = new_version
    current_model_hist=current_model_hist[["version", "loss", "accuracy", "val_loss","val_accuracy"]]

    total_hist = pd.concat([hist_df,current_model_hist]).reset_index(drop=True) 	
    with open(my_path +"versions/model/model_training_history.csv", mode='w') as f:
        total_hist.to_csv(f)

    #Sauvegarde du count_vectorizer
    CV_filename = my_path +"versions/count_vectorizer/Rakuten_CountVectorizer_v{}.sav".format(new_version)
    joblib.dump(vectorizer, CV_filename)
    #Sauvegarde du label_encoder
    LE_filename = my_path +"versions/label_encoder/Rakuten_LabelEncoder_v{}.sav".format(new_version)
    joblib.dump(labencoder, LE_filename)
    #sauvegarde du model
    model_directoryname = my_path +"versions/model/Rakuten_model_v{}".format(new_version)
    model.save(model_directoryname)
    return new_version