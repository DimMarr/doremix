import os
import psycopg2
from psycopg2 import OperationalError

def connect_db():
    try:
        DB_URL = os.getenv("DATABASE_URL") # Environnement variable from the docker-compose.yaml
        conn = psycopg2.connect(DB_URL)
        return conn
    except OperationalError as e:
        print(f"Error: {e}")