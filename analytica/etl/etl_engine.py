import pandas as pd
import os
import sys

# Adiciona o diretório raiz de analytica ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import get_db


async def process_excel(file):
    df = pd.read_excel(await file.read())

    conn = get_db()
    cur = conn.cursor()

    table_name = os.path.splitext(file.filename)[0].lower()

    cols = ", ".join(df.columns)

    for _, row in df.iterrows():
        values = "', '".join(str(v) for v in row.values)
        q = f"INSERT INTO {table_name} ({cols}) VALUES ('{values}')"
        cur.execute(q)

    conn.commit()
