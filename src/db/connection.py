import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Acquiring .env contents 
load_dotenv()

# Storing url variable in local variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Creates db engine using parameters from url, create session factory (explicit commits, no automatic flushing of changes to db)   
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creates base class (allows models to map to db automatically)
Base = declarative_base()