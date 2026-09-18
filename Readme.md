# Pipe Weather

This project is a weather data pipeline designed to collect, clean, and transform meteorological data for multiple cities. It follows a classic ETL architecture composed of three layers:

- Bronze: raw weather data extracted from an external API
- Silver: cleaned and structured data prepared for analysis
- Gold: enriched dataset with computed features and risk indicators

The pipeline retrieves daily weather forecasts from the Open-Meteo API, stores the raw responses, transforms them into a tabular format, and builds analytics such as temperature categories, precipitation levels, and weather risk scoring.

## Project Overview

The main goal of this project is to demonstrate how to build an end-to-end data pipeline that turns external weather data into useful analytical outputs. It combines Python, Pandas, Airflow, and Docker to automate the full data flow from collection to processing.

## Features

- Extract weather data for multiple cities
- Save raw API responses in a Bronze layer
- Clean and normalize the data in the Silver layer
- Generate analytical features and risk metrics in the Gold layer
- Orchestrate the workflow using Apache Airflow
- Deploy the stack locally with Docker Compose

## Tech Stack

- Python
- Pandas
- PostgreSQL
- Apache Airflow
- Streamlit
- Docker

## Architecture

The project follows a simple data pipeline structure:

1. Extract weather data from Open-Meteo
2. Store raw JSON files in the Bronze layer
3. Transform and clean the data into a structured dataset
4. Compute derived features and risk scores
5. Export the final results for analysis or visualization

## Purpose

This project is useful for learning and practicing data engineering concepts such as ETL pipelines, data orchestration, and layered data processing in a real-world scenario.
