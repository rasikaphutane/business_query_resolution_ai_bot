# init_db.py
from sqlalchemy import create_engine
from models import Base  # make sure this points to your actual models.py

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL)

# This will create tables based on Base metadata (i.e., your models)
Base.metadata.create_all(bind=engine)
