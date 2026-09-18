

import json
from pathlib import Path

import pandas as pd
import requests


API_URL = "https://api.open-meteo.com/v1/forecast"
Params = {
    "past_days": 7,
    "forecast_days": 7,
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max",
    "timezone": "Africa/Casablanca",
}
BASE_DIR = Path(__file__).resolve().parents[2]
CITY_FILE = BASE_DIR / "app" / "bronze" / "cities.csv"
OUTPUT_FILE = BASE_DIR / "app" / "bronze" / "output.json"
city_coordinates = pd.read_csv(CITY_FILE, encoding="utf-8")
CITIES = {
    row.city: {"latitude": row.lat, "longitude": row.lng}
    for row in city_coordinates.itertuples()
}


def extract():
    """Charge les donnees des villes marocaines depuis Open-Meteo."""
    frames = []

    for city, coordinates in CITIES.items():
        try:
            response = requests.get(
                API_URL,
                params={**Params, **coordinates},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()["daily"]

            city_df = pd.DataFrame({
                "Date": data["time"],
                "Ville": city,
                "Temp_Max": data["temperature_2m_max"],
                "Temp_Min": data["temperature_2m_min"],
                "Precipitation": data["precipitation_sum"],
                "Precipitation_Probability": data["precipitation_probability_max"],
                "Wind_Max": data["wind_speed_10m_max"],
                "Wind_Gusts": data["wind_gusts_10m_max"],
                "Weather_Code": data["weather_code"],
            })
            frames.append(city_df)
            print(f"Donnees recuperees pour {city}.")
        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            print(f"Erreur API pour {city}: {error}")


    df = pd.concat(frames, ignore_index=True)
    for column in [
        "Temp_Max",
        "Temp_Min",
        "Precipitation",
        "Precipitation_Probability",
        "Wind_Max",
        "Wind_Gusts",
        "Weather_Code",
    ]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df.to_json(OUTPUT_FILE, orient='records', indent=4)

    return df.dropna(subset=["Date", "Temp_Max", "Temp_Min"]).drop_duplicates()


def main():
    print(extract())


if __name__ == "__main__":
    main()