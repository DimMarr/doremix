from fastapi import FastAPI
import os
import psycopg2
from psycopg2 import OperationalError

app = FastAPI()

def get_db_version():
    db_url = os.getenv("DATABASE_URL")
    conn = None
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        return version
    except OperationalError as e:
        return str(e)
    finally:
        if conn:
            conn.close()

@app.get("/")
def read_root():
    return {"message": "L'API Python fonctionne !"}

@app.get("/db-test")
def test_db():
    result = get_db_version()
    if "PostgreSQL" in result:
        return {"status": "success", "db_version": result}
    else:
        return {"status": "error", "details": result}