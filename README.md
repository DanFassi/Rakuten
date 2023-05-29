# Rakuten
Rakuten Challenge

## Contenue du repo
Ce repo contient l'ensemble des fichiers et dossier nécessaire pour:
- L'execution d'une API
- L'execution d'airflow et du processe de ré-entrainement du modèle. (les dossiers dags et logs sont associés à airflow)

### Les dossiers
Les dossiers template et statics sont necessaires au fonctionnement de l'interface web associée à l'API.

Le dossier versions stock les anciennes versions:
 - Du modèle
 - Du Count Vectorizer
 - Du Label Encoder

Le dossier Rakuten_model contient le modèle actuel.

### Les fichiers

le fichier api_rak.py contient l'API utilisé par la programme.
le fichier Pipelines_prediction.py contient les fonctions appellées par l'API pour prédire une catégorie de produit.
les fichiers Rakuten_CountVectorizer.sav et Rakuten_LabelEncoder.sav sont les versions actuelle utilisé dans le retraitement des données textuelles entrées par l'utilisateur.

Les fichiers X.csv et Y.csv correspondant aux features et target d'entrainement. ces deux fichiers sont mis à jour dans le cas du process de ré-entrainement.

Le fichier docker-compose permet de lancer l'application, c'est à dire qu'il effectue le lancement de l'API et de AIRFLOW.

## Comment lancer l'application

1. Sur linux, clonez ce repo dans le repertoire home. Vous obtiendrez un dossier **Rakuten** (avec une majuscule)
2. Elevez les droits de ce nouveau dossier avec la commande : **sudo chmod -R 777 Rakuten**
3. Dans le repertoire Rakuten, initialiser airflow init en executant la commande :  **docker-compose up airflow-init**
4. Une fois l'étape précédente correctement executé, executez la commande : **docker-compose up -d**
5. Connectez vous à l'interface de l'api à l'adresse: **localhost:8000** ou à l'interface airflow à l'adresse **ip_de_votre_machine:8080**
