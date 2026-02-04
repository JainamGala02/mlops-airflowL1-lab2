from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.lab import load_data, data_preprocessing, build_save_model, load_model_evaluate

default_args = {
    'owner': 'jainam',
    'start_date': datetime(2026, 2, 4),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='Wine_Clustering',
    default_args=default_args,
    description='Clustering on Wine dataset',
    schedule=None,
    catchup=False,
) as dag:

    load_data_task = PythonOperator(
        task_id='load_data_task',
        python_callable=load_data,
    )

    data_preprocessing_task = PythonOperator(
        task_id='data_preprocessing_task',
        python_callable=data_preprocessing,
        op_args=[load_data_task.output],
    )

    build_save_model_task = PythonOperator(
        task_id='build_save_model_task',
        python_callable=build_save_model,
        op_args=[data_preprocessing_task.output],
    )

    load_model_evaluate_task = PythonOperator(
        task_id='load_model_evaluate_task',
        python_callable=load_model_evaluate,
        op_args=['kmeans_model.pkl', build_save_model_task.output],
    )

    load_data_task >> data_preprocessing_task >> build_save_model_task >> load_model_evaluate_task