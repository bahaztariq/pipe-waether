"""Transformation des donnees Silver et calcul du risque."""

from pathlib import Path

import pandas as pd

from app.db.db import database


def calculer_risque(ligne):
    """Compute a basic risk score based on temperature, rainfall, and wind severity."""
    score = 0

    if ligne["Temp_Max"] > 35:
        score += 40
    elif ligne["Temp_Max"] > 30:
        score += 20

    if ligne["Temp_Min"] < 5:
        score += 30
    elif ligne["Temp_Min"] < 10:
        score += 15

    if ligne["Precipitation"] > 10:
        score += 30
    elif ligne["Precipitation"] > 0:
        score += 15

    return score


def load(
    input_file="silver/meteo_maroc.csv",
    output_file="Gold/meteo_maroc_features.csv",
    load_to_database=True,
):
    df = pd.read_csv(input_file)
    df["Date"] = pd.to_datetime(df["Date"])
    df["date"] = df["Date"].dt.date
    df["Temperature_Moyenne"] = (df["Temp_Max"] + df["Temp_Min"]) / 2
    df["is_rainy"] = df["Precipitation"] > 0

    df["temperature_category"] = pd.cut(
        df["Temperature_Moyenne"],
        bins=[-float("inf"), 10, 20, 30, float("inf")],
        labels=["Froide", "Douce", "Chaude", "Tres chaude"],
    )
    df["precipitation_category"] = pd.cut(
        df["Precipitation"],
        bins=[-float("inf"), 0, 10, float("inf")],
        labels=["Aucune", "Faible", "Forte"],
    )
    df["wind_category"] = pd.cut(
        df["Wind_Max"],
        bins=[-float("inf"), 30, 50, float("inf")],
        labels=["Faible", "Modere", "Fort"],
    )
    df["risk_score"] = df.apply(calculer_risque, axis=1)

    Path(output_file).parent.mkdir(exist_ok=True)
    df.to_csv(output_file, index=False)
    print("Fichier Gold enregistre.")

    if load_to_database:
        database.create_tables()
        rows_loaded = database.load_gold_dataframe(df)
        print(f"{rows_loaded} lignes Gold chargees dans PostgreSQL.")

    return df


if __name__ == "__main__":
    load()
