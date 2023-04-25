import joblib
import string
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Input

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

# 1 - Data Processing
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
    return X

#2 - definition du model et entrainement
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

    model.fit(X_train, y_train,
                    epochs=10,
                    verbose=True,
                    validation_data=(X_test, y_test),
                    batch_size=10)
    return model



# =============================================================================
# Fonctions utilisées pour la prédiction de valeurs
# =============================================================================

def text_processing(title,desc):
    text = str(title) + " " + str(desc)
    text = text.lower()
    text = "".join([i for i in text if i not in string.punctuation])
    stopword = stopwords.words('english')
    text = " ".join([word for word in str(text).split() if word not in stopword])
    stopword = stopwords.words('french')
    text = " ".join([word for word in str(text).split() if word not in stopword])
    stemmer = SnowballStemmer("french")
    text = " ".join([stemmer.stem(word) for word in text.split()])
    vectorizer = joblib.load("Rakuten_CountVectorizer.sav")
    X = vectorizer.transform([text]).todense()
    return X


def prediction(X):
    model = load_model('Rakuten_model')
    prob = np.max(model.predict(X)) 
    pred_class = np.argmax(model.predict(X), axis=-1)
    le = joblib.load("Rakuten_LabelEncoder.sav")
    classe = str(le.inverse_transform(pred_class)[0])
    return {"PrductCODE" : classe, "predict_proba": prob}

#title = "Super jouet de folie"
#desc = "une figurine qui fera rever les enfants"

#X = prediction(text_processing(title,desc))
#print(X[0])
#print(round(X[1]*100), "%")
