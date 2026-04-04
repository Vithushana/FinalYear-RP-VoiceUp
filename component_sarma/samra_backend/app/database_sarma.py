from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.settings_sarma import settings

# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

# Create a configured "Session" class 
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()
