from fastapi import FastAPI
from connect_db import connect_db

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "L'API Python fonctionne !"}
    
@app.get("/db-test")
def db_test():
    conn = connect_db()
    with conn.cursor() as curs:
        curs.execute("SELECT version();")
        version = curs.fetchone()[0]
        return version