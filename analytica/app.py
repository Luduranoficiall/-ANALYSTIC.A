## ============================================
## file: app.py — ANALYSTIC.A PRO ULTRA SECURE
## ============================================
import uvicorn
from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Imports locais (relativos ao pacote analytica)
from security.auth import get_current_user, login_user
from etl.etl_engine import process_excel
from charts.chart_engine import generate_chart
from gpt.gpt_engine import generate_insights
from schemas import LoginSchema

# Prometheus (opcional, apenas se instalado)
try:
    from prometheus_client import Counter, Histogram, generate_latest
    PROMETHEUS_ENABLED = True
    REQUEST_COUNT = Counter("requests_total", "Total Requests")
    LATENCY = Histogram("request_latency_seconds", "Request latency")
except ImportError:
    PROMETHEUS_ENABLED = False

# ======================================================
# FASTAPI APP
# ======================================================
app = FastAPI(title="ANALYSTIC.A PRO ULTRA SECURE — Power BI + GPT")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================
# METRICS (PROMETHEUS)
# ======================================================
@app.get("/metrics")
def metrics():
    if PROMETHEUS_ENABLED:
        return Response(generate_latest(), media_type="text/plain")
    return {"status": "prometheus not installed"}


# ======================================================
# LOGIN PAGE
# ======================================================
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, data: LoginSchema):
    token = login_user(data.email, data.password)
    if not token:
        raise HTTPException(400, "Credenciais inválidas")

    response = RedirectResponse("/", status_code=302)
    response.set_cookie("access_token", token, httponly=True)
    return response


# ======================================================
# DASHBOARD PRINCIPAL
# ======================================================
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


# ======================================================
# UPLOAD DE ARQUIVOS (EXCEL) → BANCO → DASHBOARD
# ======================================================
@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    await process_excel(file)
    return {"status": "ok", "message": "Arquivo processado com sucesso"}


# ======================================================
# GERAR GRÁFICO DINÂMICO
# ======================================================
@app.get("/chart")
def chart(request: Request, table: str, x: str, y: str, user=Depends(get_current_user)):
    graph_json = generate_chart(table, x, y)
    return templates.TemplateResponse("chart.html", {"request": request, "graph_json": graph_json})


# ======================================================
# GPT INSIGHTS
# ======================================================
@app.get("/insights")
def insights(question: str, user=Depends(get_current_user)):
    answer = generate_insights(question)
    return {"insights": answer}


# ======================================================
# PREDICT (PREDITIVI.A)
# ======================================================
@app.get("/predict", response_class=HTMLResponse)
def predict_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("predict.html", {"request": request})


# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
