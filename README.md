# RAKUTEN CHALLENGE

## Présentation du projet
Dans le cadre de ma formation MLops, j'ai du réaliser un projet ayant pour thème la classification de produits de e-commerce, basé sur le challenge **Rakuten France Multimodal Product Data Classification**.
Plus d'informations sur la nature de ce challenge [ici](https://challengedata.ens.fr/challenges/35)

Les objectifs de ce projet étaient les suivants:
- Créer un modèle permettant la prédiction d'une catégorie de produit basé sur leur designation et leur description. (données textuelles)
- Créer une base de données utilisateur et une base de donnée logs (technologie choisie : MONGODB)
- Mettre en place une API sécurisée avec identification de l'utilisateur, permettant de requeter le modèle en place.
- Mettre en place un pipeline CI/CD avec réentrainement du modèle via AIRFLOW
- Containeriser L'API et AIRFLOW via DOCKER
- Créer une interface web permettant un accès simple et intuitif au modèle.

## Contenu du repo
Ce repo contient l'ensemble des fichiers et dossiers nécessaires pour:
- L'execution d'une API ainsi que d'une interface web.
- L'execution d'airflow et du processe de ré-entrainement du modèle. (les dossiers dags et logs sont associés à airflow)

### Les dossiers
Les dossiers template et statics sont necessaires au fonctionnement de l'interface web associée à l'API.

Le dossier versions stock les anciennes versions:
 - Du modèle
 - Du Count Vectorizer
 - Du Label Encoder

Le dossier Rakuten_model contient le modèle actuel.

### Les fichiers

Le fichier api_rak.py contient l'API utilisé par la programme.

Le fichier Pipelines_prediction.py contient les fonctions appellées par l'API pour prédire une catégorie de produit.

Les fichiers Rakuten_CountVectorizer.sav et Rakuten_LabelEncoder.sav sont les versions actuelle utilisées dans le retraitement des données textuelles entrées par l'utilisateur.

Les fichiers X.csv et Y.csv correspondent aux features et targets d'entrainement. Ces deux fichiers sont mis à jour dans le cas du process de ré-entrainement.

Le fichier docker-compose permet de lancer l'application, c'est à dire qu'il effectue le lancement de l'API et de AIRFLOW.

Enfin les fichiers test_xxx sont necessaires pour les tests unitaires effectués par une action github à chaque nouveau push sur ce repo.

## Comment lancer l'application

1. Sur linux, clonez ce repo dans le repertoire home. Vous obtiendrez un dossier **Rakuten** (avec une majuscule)
2. Elevez les droits de ce nouveau dossier avec la commande : **sudo chmod -R 777 Rakuten**
3. Dans le repertoire Rakuten, initialiser airflow init en executant la commande :  **docker-compose up airflow-init**
4. Une fois l'étape précédente correctement executé, executez la commande : **docker-compose up -d**
5. Connectez vous à l'interface de l'api à l'adresse: **localhost:8000** ou à l'interface airflow à l'adresse **ip_de_votre_machine:8080**
