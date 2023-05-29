from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator, BranchPythonOperator
from Mongodb_connect import mongo_trigger, training_data_update
from Pipeline_entrainement import dataframe_processing, target_processing, MLmodel, model_selection,  version_saving
import pandas as pd

def modelisation():
    X_df = pd.read_csv("X.csv",index_col = 0)
    y_df = pd.read_csv("y.csv",index_col = 0)
    X, vectorizer = dataframe_processing(X_df)
    y, le = target_processing(y_df)
    model , history = MLmodel(X,y)
    if model_selection(history):
        version_saving(vectorizer, le, model, history)

    
#dag se déclanchant chaque jour
rakuten_dag = DAG(
    dag_id = "model_retraining",
    description = "Dag permettant le ré-entrainement du model",
    tags = ["rakuten", 'project', 'datascientest'],
    schedule_interval = '0 0 * * *',
    default_args={ 'owner': 'airflow', 'start_date': days_ago(0)},
    catchup=False
)

task1 = BranchPythonOperator(
    task_id= "BDD_trigger_condition_check",
    provide_context = True,
    python_callable = mongo_trigger,
    dag  = rakuten_dag
)

task2 = PythonOperator(
    task_id= "Dataframe_update",
    python_callable= training_data_update,
    dag  = rakuten_dag
)

task3 = PythonOperator(
    task_id= "training_and_update",
    python_callable =  modelisation,
    dag  = rakuten_dag
)
