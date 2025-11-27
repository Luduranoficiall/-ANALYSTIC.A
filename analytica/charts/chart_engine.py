import plotly.graph_objects as go
from db.database import get_db


def generate_chart(table, x, y):
    conn = get_db()
    cur = conn.cursor()

    q = f"SELECT {x}, {y} FROM {table} ORDER BY {x}"
    cur.execute(q)
    rows = cur.fetchall()

    x_vals = [row[0] for row in rows]
    y_vals = [row[1] for row in rows]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="lines+markers",
        line=dict(width=4),
        marker=dict(size=10)
    ))

    fig.update_layout(
        template="plotly_dark",
        title=f"{table.upper()} — {y} por {x}",
        xaxis_title=x,
        yaxis_title=y,
        height=600
    )

    return fig.to_json()
