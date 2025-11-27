# ============================================
# file: etl_engine.py
# ============================================
import pandas as pd
from database import get_db
import os


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
