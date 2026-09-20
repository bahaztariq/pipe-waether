import os
from datetime import date

import pandas as pd
from sqlalchemy import Date, Float, ForeignKey, String, UniqueConstraint, create_engine, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session, sessionmaker

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = os.getenv("POSTGRES_DB", "db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


class Base(DeclarativeBase):
    pass


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    forecasts: Mapped[list["WeatherForecast"]] = relationship(back_populates="city", cascade="all, delete-orphan")


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"
    __table_args__ = (
        UniqueConstraint("city_id", "forecast_date", name="uq_weather_city_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False, index=True)
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    temp_max: Mapped[float] = mapped_column(Float, nullable=False)
    temp_min: Mapped[float] = mapped_column(Float, nullable=False)
    precipitation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    precipitation_probability: Mapped[float] = mapped_column(Float, nullable=True)
    wind_max: Mapped[float] = mapped_column(Float, nullable=True)
    wind_gusts: Mapped[float] = mapped_column(Float, nullable=True)
    weather_code: Mapped[int] = mapped_column(nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(30), nullable=True)

    city: Mapped[City] = relationship(back_populates="forecasts")


class Database:
    """Singleton database access class used to share one engine and session factory."""
    _instance: "Database | None" = None

    def __new__(cls, database_url: str | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.engine = create_engine(database_url or DATABASE_URL, echo=False)
            cls._instance.SessionLocal = sessionmaker(
                bind=cls._instance.engine,
                autoflush=False,
                autocommit=False,
            )
        return cls._instance

    @classmethod
    def get_instance(cls, database_url: str | None = None) -> "Database":
        if cls._instance is None:
            return cls(database_url)
        return cls._instance

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def execute_query(self, query):
        with self.engine.begin() as connection:
            return connection.execute(text(query))

    def get_session(self) -> Session:
        return self.SessionLocal()

    def load_gold_dataframe(self, df: pd.DataFrame) -> int:
        """Upsert Gold forecasts so repeated runs refresh existing dates."""
        if df.empty:
            return 0

        self.create_tables()
        city_df = df[["Ville", "Latitude", "Longitude"]].drop_duplicates(subset=["Ville"]).copy()
        city_df = city_df.rename(columns={"Ville": "name", "Latitude": "latitude", "Longitude": "longitude"})

        with self.get_session() as session:
            for city in city_df.itertuples(index=False):
                existing_city = session.scalar(select(City).where(City.name == city.name))
                if existing_city is None:
                    session.add(City(name=city.name, latitude=city.latitude, longitude=city.longitude))
            session.commit()

            city_ids = {
                city.name: city.id
                for city in session.scalars(select(City)).all()
            }

        weather_df = df.rename(
            columns={
                "Ville": "city_name",
                "Date": "forecast_date",
                "Temp_Max": "temp_max",
                "Temp_Min": "temp_min",
                "Precipitation": "precipitation",
                "Precipitation_Probability": "precipitation_probability",
                "Wind_Max": "wind_max",
                "Wind_Gusts": "wind_gusts",
                "Weather_Code": "weather_code",
                "risk_score": "risk_score",
            }
        ).copy()
        weather_df["forecast_date"] = pd.to_datetime(weather_df["forecast_date"]).dt.date
        weather_df["city_id"] = weather_df["city_name"].map(city_ids)
        weather_df["risk_level"] = weather_df["risk_score"].apply(
            lambda score: "Extreme" if score >= 75 else "Elevé" if score >= 50 else "Modéré" if score >= 25 else "Faible"
        )
        weather_df = weather_df.dropna(subset=["city_id"])
        weather_df = weather_df.drop_duplicates(subset=["city_id", "forecast_date"])
        weather_df = weather_df[[
            "city_id",
            "forecast_date",
            "temp_max",
            "temp_min",
            "precipitation",
            "precipitation_probability",
            "wind_max",
            "wind_gusts",
            "weather_code",
            "risk_score",
            "risk_level",
        ]]

        records = weather_df.to_dict(orient="records")
        statement = insert(WeatherForecast.__table__).values(records)
        update_columns = {
            column.name: getattr(statement.excluded, column.name)
            for column in WeatherForecast.__table__.columns
            if column.name not in {"id", "city_id", "forecast_date"}
        }
        statement = statement.on_conflict_do_update(
            constraint="uq_weather_city_date",
            set_=update_columns,
        )
        with self.engine.begin() as connection:
            connection.execute(statement)
        return len(records)


database = Database.get_instance()
