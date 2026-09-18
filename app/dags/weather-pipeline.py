from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.bronze.main import extract as extract_weather
from app.Silver.silver import transform
from app.Gold.gold import load


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

airflow_dag = DAG(
    'weather_pipeline',
    default_args=default_args,
    description='A simple weather data pipeline',
    schedule_interval=timedelta(days=1),
)


def run_bronze():
    return extract_weather(
        output_dir=os.getenv('BRONZE_DIR', str(PROJECT_ROOT / 'app' / 'bronze')),
        cities_file=os.getenv('CITIES_FILE', str(PROJECT_ROOT / 'app' / 'bronze' / 'cities.csv')),
        weather_url=os.getenv('OPEN_METEO_URL', 'https://api.open-meteo.com/v1/forecast'),
        forecast_days=int(os.getenv('FORECAST_DAYS', '7')),
        timeout=int(os.getenv('REQUEST_TIMEOUT_SECONDS', '30')),
        retries=int(os.getenv('REQUEST_RETRIES', '3')),
    )


def run_transform():
    return transform(
        bronze_dir=os.getenv('BRONZE_DIR', str(PROJECT_ROOT / 'app' / 'bronze')),
        output_file=os.getenv('SILVER_FILE', str(PROJECT_ROOT / 'app' / 'Silver' / 'meteo_maroc.csv')),
    )


def run_load():
    return load(
        input_file=os.getenv('SILVER_FILE', str(PROJECT_ROOT / 'app' / 'Silver' / 'meteo_maroc.csv')),
        output_file=os.getenv('GOLD_FILE', str(PROJECT_ROOT / 'app' / 'Gold' / 'meteo_maroc_features.csv')),
    )


extract_task = PythonOperator(
    task_id='extract',
    python_callable=run_bronze,
    dag=airflow_dag,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=run_transform,
    dag=airflow_dag,
)

load_task = PythonOperator(
    task_id='load',
    python_callable=run_load,
    dag=airflow_dag,
)

extract_task >> transform_task >> load_task






