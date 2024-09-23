# Script to load database url
import os
from dotenv import load_dotenv

load_dotenv()

os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL')