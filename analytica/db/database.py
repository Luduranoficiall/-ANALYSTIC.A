import psycopg2
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "analystic_a")
DB_USER = os.getenv("DB_USER", "analystic_a")
DB_PASS = os.getenv("DB_PASS", "analystic_a_secret")


def get_db():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
    )
