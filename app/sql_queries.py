"""Business queries for the weather risk project."""

import pandas as pd
from sqlalchemy import text

from app.db.db import database


def _run_query(query: str) -> pd.DataFrame:
    """Execute one query and return its rows as a DataFrame."""
    return pd.read_sql_query(text(query), database.engine)


def highest_temperatures() -> pd.DataFrame:
    query = """
        SELECT c.name, MAX(wf.temp_max) AS temp_max
        FROM weather_forecasts wf
        JOIN cities c ON c.id = wf.city_id
        GROUP BY c.name
        ORDER BY temp_max DESC
        LIMIT 10;
    """
    return _run_query(query)


def highest_precipitations() -> pd.DataFrame:
    query = """
        SELECT c.name, MAX(wf.precipitation) AS precipitation_max
        FROM weather_forecasts wf
        JOIN cities c ON c.id = wf.city_id
        GROUP BY c.name
        ORDER BY precipitation_max DESC
        LIMIT 10;
    """
    return _run_query(query)


def highest_average_risk() -> pd.DataFrame:
    query = """
        SELECT c.name, AVG(wf.risk_score) AS risk_moyen
        FROM weather_forecasts wf
        JOIN cities c ON c.id = wf.city_id
        GROUP BY c.name
        ORDER BY risk_moyen DESC
        LIMIT 10;
    """
    return _run_query(query)


def max_risk_periods() -> pd.DataFrame:
    query = """
        SELECT wf.forecast_date, AVG(wf.risk_score) AS risk_moyen
        FROM weather_forecasts wf
        GROUP BY wf.forecast_date
        ORDER BY risk_moyen DESC
        LIMIT 10;
    """
    return _run_query(query)


def city_highest_risk_day() -> pd.DataFrame:
    query = """
        SELECT DISTINCT ON (c.id)
               c.name,
               wf.forecast_date,
               wf.risk_score
        FROM weather_forecasts wf
        JOIN cities c ON c.id = wf.city_id
        ORDER BY c.id, wf.risk_score DESC, wf.forecast_date ASC;
    """
    return _run_query(query)
