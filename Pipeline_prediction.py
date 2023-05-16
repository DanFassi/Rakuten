import joblib
import string
import numpy as np

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

from tensorflow.keras.models import load_model


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
