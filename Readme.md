# Pipe Weather

Pipe Weather is a data engineering project for collecting, transforming, and analyzing weather forecasts for Moroccan cities. The solution follows a Bronze → Silver → Gold pipeline and is designed to help identify risky meteorological conditions for operational planning.

## Project goal

The project answers a practical business question: which cities and which periods are likely to face the highest meteorological risk in the coming days?

## Current project status

This repository is currently structured around the main ETL stages: Bronze extraction, Silver cleaning, and Gold feature engineering. The codebase is organized to support weather forecasting, risk scoring, and future PostgreSQL and Airflow orchestration.

It is built around a simple data pipeline that:

- extracts weather data from Open-Meteo;
- stores raw responses in the Bronze layer;
- cleans and standardizes the data in Silver;
- creates risk features and business-ready indicators in Gold;
- orchestrates the workflow with Airflow;
- can be deployed locally with Docker Compose.

## Main features

- API-based weather extraction for multiple cities
- Bronze raw storage for unchanged source data
- Silver data cleaning and standardization
- Gold feature engineering with temperature, precipitation, wind, and risk categories
- Risk score calculation for operational decision support
- Docker setup for local orchestration and services

## Tech stack

- Python
- Pandas
- SQLAlchemy
- PostgreSQL
- Apache Airflow
- Streamlit
- Docker

## Pipeline architecture

1. Extract forecast data from Open-Meteo
2. Save the raw responses in Bronze
3. Clean and structure the raw data in Silver
4. Build analytical features and weather-risk scores in Gold
5. Prepare the data for SQL analysis and visualization

## Business value

The project helps operational teams compare weather conditions between cities, detect high-risk windows, and anticipate disruptions that may affect logistics, deliveries, and field operations.

## Weather risk score

The Gold layer calculates a score from 0 to 100 for each city and forecast date:

- maximum temperature above 35 C: 40 points; above 30 C: 20 points;
- minimum temperature below 5 C: 30 points; below 10 C: 15 points;
- precipitation above 10 mm: 30 points; above 0 mm: 15 points.

The score prioritizes conditions that can disrupt delivery operations. The resulting levels are `Faible` below 25, `Modere` from 25, `Eleve` from 50, and `Extreme` from 75.

## Local services

- Airflow: http://localhost:8080
- Streamlit: http://localhost:8501
- pgAdmin: http://localhost:5050

The Airflow DAG runs Bronze extraction, Silver cleaning, and Gold feature engineering daily. Gold forecasts are upserted using the city and forecast date, so refreshing a forecast does not create duplicate rows.
