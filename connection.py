# database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Crea connessione al database SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./motocross_manager.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sessione per le operazioni sul database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class per i modelli
Base = declarative_base()

def get_db():
    """Funzione per ottenere una sessione del database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()