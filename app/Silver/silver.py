"""Nettoyage des donnees Bronze."""

import json
from pathlib import Path

import pandas as pd


def transform(bronze_dir="bronze", output_file="silver/meteo_maroc.csv"):
    bronze_runs = sorted(
        [path for path in Path(bronze_dir).iterdir() if (path / "cities.csv").exists()]
    )
    bronze_run = bronze_runs[-1]
    cities = pd.read_csv(bronze_run / "cities.csv")

    tableaux = []
    for number, city in enumerate(cities["city"]):
        weather_file = bronze_run / f"{number:04d}_{city.replace(' ', '_')}.json"
        if not weather_file.exists():
            continue

        with weather_file.open(encoding="utf-8") as file:
            daily = json.load(file)["daily"]

        tableau = pd.DataFrame({
            "Date": daily["time"],
            "Ville": city,
            "Latitude": cities.iloc[number]["lat"],
            "Longitude": cities.iloc[number]["lng"],
            "Temp_Max": daily["temperature_2m_max"],
            "Temp_Min": daily["temperature_2m_min"],
            "Precipitation": daily["precipitation_sum"],
            "Precipitation_Probability": daily["precipitation_probability_max"],
            "Wind_Max": daily["wind_speed_10m_max"],
            "Wind_Gusts": daily["wind_gusts_10m_max"],
            "Weather_Code": daily["weather_code"],
        })
        tableaux.append(tableau)

    df = pd.concat(tableaux, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Precipitation"] = df["Precipitation"].fillna(0)
    df = df.dropna(subset=["Date", "Temp_Max", "Temp_Min"])
    df = df.drop_duplicates()

    Path(output_file).parent.mkdir(exist_ok=True)
    df.to_csv(output_file, index=False)
    print("Fichier Silver enregistre.")
    return df


if __name__ == "__main__":
    transform()
