from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5433/ojdb")

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()
