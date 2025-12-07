import os
from urllib.parse import urlparse, parse_qs
import psycopg2


def _conn_from_url(db_url: str):
    parsed = urlparse(db_url)
    query = parse_qs(parsed.query)
    sslmode = query.get("sslmode", ["prefer"])[0]
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip("/"),
        user=parsed.username,
        password=parsed.password,
        sslmode=sslmode,
    )


def get_db():
    """
    Retorna conexão com prioridade para DATABASE_URL (Fly Postgres attach).
    Fallback para variáveis separadas DB_HOST/DB_NAME/DB_USER/DB_PASS.
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return _conn_from_url(db_url)

    host = os.getenv("DB_HOST", "localhost")
    name = os.getenv("DB_NAME", "analystic_a")
    user = os.getenv("DB_USER", "analystic_a")
    pw = os.getenv("DB_PASS", "analystic_a_secret")
    return psycopg2.connect(host=host, database=name, user=user, password=pw)
