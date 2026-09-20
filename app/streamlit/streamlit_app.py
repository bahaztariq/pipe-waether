import pandas as pd
import streamlit as st
from sqlalchemy import text

from app.db.db import database


st.set_page_config(page_title="Pipe Weather", page_icon=":cloud:", layout="wide")


@st.cache_data(ttl=300)
def load_forecasts():
	query = text(
		"""
		SELECT c.name AS city, c.latitude, c.longitude,
			   wf.forecast_date, wf.temp_max, wf.temp_min,
			   wf.precipitation, wf.precipitation_probability,
			   wf.wind_max, wf.wind_gusts, wf.weather_code,
			   wf.risk_score, wf.risk_level
		FROM weather_forecasts wf
		JOIN cities c ON c.id = wf.city_id
		ORDER BY wf.forecast_date, c.name
		"""
	)
	return pd.read_sql_query(query, database.engine)


st.title("Pipe Weather")
st.caption("Prévisions et risques météorologiques pour les opérations de livraison")

try:
	forecasts = load_forecasts()
except Exception as error:
	st.error("La base PostgreSQL n'est pas encore disponible.")
	st.code(str(error))
	st.stop()

if forecasts.empty:
	st.warning("Aucune prévision n'est encore disponible. Exécutez le DAG Airflow.")
	st.stop()

forecasts["forecast_date"] = pd.to_datetime(forecasts["forecast_date"])

st.sidebar.header("Filtres")
cities = st.sidebar.multiselect(
	"Ville",
	options=sorted(forecasts["city"].unique()),
	default=sorted(forecasts["city"].unique()),
)
date_min = forecasts["forecast_date"].min().date()
date_max = forecasts["forecast_date"].max().date()
selected_dates = st.sidebar.date_input(
	"Période",
	value=(date_min, date_max),
	min_value=date_min,
	max_value=date_max,
)
risk_levels = st.sidebar.multiselect(
	"Niveau de risque",
	options=["Faible", "Modéré", "Elevé", "Extreme"],
	default=["Faible", "Modéré", "Elevé", "Extreme"],
)

filtered = forecasts[forecasts["city"].isin(cities) & forecasts["risk_level"].isin(risk_levels)]
if len(selected_dates) == 2:
	filtered = filtered[
		filtered["forecast_date"].dt.date.between(selected_dates[0], selected_dates[1])
	]

if filtered.empty:
	st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
	st.stop()

highest_risk = filtered.loc[filtered["risk_score"].idxmax()]
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Villes", filtered["city"].nunique())
kpi2.metric("Température maximale", f"{filtered['temp_max'].max():.1f} °C")
kpi3.metric("Précipitations maximales", f"{filtered['precipitation'].max():.1f} mm")
kpi4.metric("Périodes à risque", int((filtered["risk_score"] >= 50).sum()))
kpi5.metric("Risque maximal", f"{highest_risk['city']} ({highest_risk['risk_score']:.0f})")

st.subheader("Risque par ville et par date")
risk_chart = filtered.pivot_table(
	index="forecast_date", columns="city", values="risk_score", aggfunc="max"
)
st.line_chart(risk_chart)

left, right = st.columns(2)
with left:
	st.subheader("Villes les plus exposées")
	city_risk = (
		filtered.groupby("city", as_index=False)["risk_score"]
		.mean()
		.sort_values("risk_score", ascending=False)
	)
	st.bar_chart(city_risk.set_index("city"))
with right:
	st.subheader("Périodes les plus risquées")
	st.dataframe(
		filtered.nlargest(10, "risk_score")[
			["city", "forecast_date", "temp_max", "precipitation", "wind_max", "risk_score", "risk_level"]
		],
		use_container_width=True,
		hide_index=True,
	)

st.subheader("Prévisions filtrées")
st.dataframe(filtered, use_container_width=True, hide_index=True)
