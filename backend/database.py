import os

# Load environment variables and SQLAlchemy database utilities.
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Read variables from the local .env file into the process environment.
load_dotenv()

# Retrieve the database connection URL from the environment.
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the shared SQLAlchemy engine used for database connections.
engine = create_engine(DATABASE_URL)


# Configure a factory that creates database sessions bound to the engine.
SessionLocal = sessionmaker(
    bind=engine
)


# Base class inherited by all SQLAlchemy ORM models.
class Base(DeclarativeBase):
    pass

# FastAPI dependency that provides a session and always closes it afterward.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
