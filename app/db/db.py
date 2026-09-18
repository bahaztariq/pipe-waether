import os
from datetime import date

from sqlalchemy import Float, String, Date, ForeignKey, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session, sessionmaker

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = os.getenv("POSTGRES_DB", "db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")

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


database = Database.get_instance()
