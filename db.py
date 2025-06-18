# db.py
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            dbname="blogdb",
            user="postgres",
            password="hopalover1",
            host="localhost",
            cursor_factory=RealDictCursor
        )
    return g.db