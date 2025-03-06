from pathlib import Path

import os
import dotenv
import sqlalchemy
from crewai.telemetry import Telemetry

dotenv.load_dotenv()

DB_PASSWORD=os.getenv("DB_PASSWORD", "password")
DB_USER=os.getenv("DB_USER", "user")
DB_ENDPOINT=os.getenv("DB_ENDPOINT", "localhost")
DB_PORT=os.getenv("DB_PORT", "5432")

__db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ENDPOINT}:{DB_PORT}/postgres'
ENGINE = sqlalchemy.create_engine(__db_url)

S3_BUCKET_NAME=os.getenv("S3_BUCKET_NAME","bucket")

PROJECT_ROOT = Path(__file__).parent.parent


# Disable CrewAI Telemetry
def noop(*args, **kwargs):
    pass


for attr in dir(Telemetry):
    if callable(getattr(Telemetry, attr)) and not attr.startswith("__"):
        setattr(Telemetry, attr, noop)
