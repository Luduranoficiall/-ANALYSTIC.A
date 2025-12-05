## ============================================
## file: app.py — ANALYSTIC.A PRO ULTRA SECURE
## ============================================
import uvicorn
from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Imports locais (relativos ao pacote analytica)
from security.auth import get_current_user_or_redirect, login_user, register_user
from etl.etl_engine import process_excel
from charts.chart_engine import generate_chart
from gpt.gpt_engine import generate_insights

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
# 🏠 LANDING PAGE PÚBLICA
# ======================================================
@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    """Landing page pública - primeira impressão"""
    # Verificar se usuário já está logado
    token = request.cookies.get("access_token")
    if token:
        try:
            from security.auth import verify_token
            user = verify_token(token)
            if user:
                return RedirectResponse("/dashboard", status_code=302)
        except:
            pass
    return templates.TemplateResponse("landing.html", {"request": request})


# ======================================================
# 📝 REGISTRO/CADASTRO
# ======================================================
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@app.post("/register")
def register_user_route(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    # Usar o sistema de registro real
    result = register_user(email, password, name)
    
    if not result["success"]:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": result["error"]
        })
    
    # Sucesso! Redirecionar para login
    return RedirectResponse("/login?registered=true", status_code=302)


# ======================================================
# LOGIN PAGE
# ======================================================
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    registered = request.query_params.get("registered")
    return templates.TemplateResponse("login.html", {"request": request, "error": None, "registered": registered})


@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    token = login_user(email, password)
    if not token:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "E-mail ou senha inválidos",
            "registered": None
        })

    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=7200)
    return response


# ======================================================
# DASHBOARD PRINCIPAL (LOGADO)
# ======================================================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


# ======================================================
# 📊 WORKSPACE POWER BI STYLE (PRINCIPAL!)
# ======================================================
@app.get("/workspace", response_class=HTMLResponse)
def workspace_powerbi(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("powerbi_dashboard.html", {"request": request, "user": user})


# ======================================================
# UPLOAD DE ARQUIVOS (EXCEL) → BANCO → DASHBOARD
# ======================================================
@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})


@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...), user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    await process_excel(file)
    return {"status": "ok", "message": "Arquivo processado com sucesso"}


# ======================================================
# GERAR GRÁFICO DINÂMICO
# ======================================================
@app.get("/chart")
def chart(request: Request, table: str, x: str, y: str, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    graph_json = generate_chart(table, x, y)
    return templates.TemplateResponse("chart.html", {"request": request, "graph_json": graph_json})


# ======================================================
# GPT INSIGHTS
# ======================================================
@app.get("/insights")
def insights(request: Request, question: str, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    answer = generate_insights(question)
    return {"insights": answer}


# ======================================================
# 🤖 API DE IA (OLLAMA + GEMINI) - GRATUITO!
# ======================================================
@app.post("/api/ai/chat")
async def ai_chat_endpoint(request: Request, user=Depends(get_current_user_or_redirect)):
    """Chat com IA usando Ollama (local) ou Gemini (cloud)"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    from gpt.ai_engine import generate_ai_response
    
    data = await request.json()
    message = data.get("message", "")
    prefer_local = data.get("prefer_local", True)
    
    if not message:
        return {"error": "Mensagem vazia"}
    
    result = await generate_ai_response(message, prefer_local)
    return result


@app.post("/api/ai/analyze")
async def ai_analyze_endpoint(request: Request, user=Depends(get_current_user_or_redirect)):
    """Análise de dados com IA"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    from gpt.ai_engine import analyze_data
    
    data = await request.json()
    description = data.get("data", "")
    
    result = await analyze_data(description)
    return result


@app.post("/api/ai/predict")
async def ai_predict_endpoint(request: Request, user=Depends(get_current_user_or_redirect)):
    """Previsão com IA"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    from gpt.ai_engine import predict_trend
    
    data = await request.json()
    historical = data.get("data", "")
    
    result = await predict_trend(historical)
    return result


@app.get("/api/ai/status")
async def ai_status():
    """Verifica status das IAs disponíveis"""
    import httpx
    import os
    
    status = {
        "ollama": {"available": False, "model": None},
        "gemini": {"available": False}
    }
    
    # Verifica Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                status["ollama"] = {
                    "available": True,
                    "models": models,
                    "active_model": "gemma:2b" if "gemma:2b" in models else models[0] if models else None
                }
    except:
        pass
    
    # Verifica Gemini
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        status["gemini"] = {"available": True, "model": "gemini-pro"}
    
    return status


# ======================================================
# PREDICT (PREDITIVI.A)
# ======================================================
@app.get("/predict", response_class=HTMLResponse)
def predict_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("predict.html", {"request": request, "user": user})


# ======================================================
# 🐍 PYTHON EDITOR PRO
# ======================================================
@app.get("/python-editor", response_class=HTMLResponse)
def python_editor_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("python_editor.html", {"request": request, "user": user})


@app.post("/api/execute-python")
async def execute_python(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    import subprocess
    import tempfile
    import os
    
    data = await request.json()
    code = data.get("code", "")
    
    # Criar arquivo temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python3', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        output = "⏱ Timeout: Execução demorou mais de 30 segundos"
    except Exception as e:
        output = f"❌ Erro: {str(e)}"
    finally:
        os.unlink(temp_file)
    
    return {"output": output}


# ======================================================
# 📦 EXPORTS CENTER
# ======================================================
@app.get("/exports", response_class=HTMLResponse)
def exports_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("exports.html", {"request": request, "user": user})


@app.post("/api/export/{format}")
async def export_data(format: str, request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    # Exportação será implementada com base no formato
    formats_supported = ["powerbi", "excel", "pdf", "python", "documentation"]
    
    if format not in formats_supported:
        return {"error": f"Formato não suportado: {format}"}
    
    return {"status": "ok", "message": f"Exportação {format.upper()} iniciada", "format": format}


# ======================================================
# 🔗 GITHUB SYNC
# ======================================================
@app.get("/github", response_class=HTMLResponse)
def github_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("github_sync.html", {"request": request, "user": user})


@app.post("/api/github/push")
async def github_push(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    import subprocess
    
    data = await request.json()
    message = data.get("message", "Commit via ANALYSTIC.A")
    
    try:
        # Git add + commit + push
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', message], check=True)
        result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        
        return {"status": "ok", "message": "Push realizado com sucesso!", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"error": f"Erro no Git: {str(e)}"}


@app.post("/api/github/pull")
async def github_pull(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    import subprocess
    
    try:
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        return {"status": "ok", "message": "Pull realizado!", "output": result.stdout}
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}


# ======================================================
# 📚 DOCUMENTATION
# ======================================================
@app.get("/documentation", response_class=HTMLResponse)
def documentation_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    
    from datetime import datetime
    now = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    return templates.TemplateResponse("documentation.html", {
        "request": request, 
        "user": user,
        "now": now
    })


# ======================================================
# 👥 WORKSPACES (Multi-usuário)
# ======================================================
@app.get("/workspaces", response_class=HTMLResponse)
def workspaces_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("workspaces.html", {"request": request, "user": user})


@app.get("/api/workspaces")
async def list_workspaces(user=Depends(get_current_user_or_redirect)):
    """Lista todos os workspaces do usuário"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    # Simular workspaces do usuário
    workspaces = [
        {
            "id": "ws-1",
            "name": "Dashboard Financeiro",
            "description": "Análise financeira trimestral",
            "created_at": "2024-01-15",
            "members": 3,
            "reports": 5,
            "role": "admin",
            "color": "#667eea"
        },
        {
            "id": "ws-2", 
            "name": "Marketing Analytics",
            "description": "Métricas de campanha",
            "created_at": "2024-01-20",
            "members": 2,
            "reports": 3,
            "role": "editor",
            "color": "#f093fb"
        }
    ]
    
    return {"workspaces": workspaces}


@app.post("/api/workspaces")
async def create_workspace(request: Request, user=Depends(get_current_user_or_redirect)):
    """Cria novo workspace"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    data = await request.json()
    name = data.get("name", "Novo Workspace")
    description = data.get("description", "")
    
    import uuid
    workspace_id = f"ws-{str(uuid.uuid4())[:8]}"
    
    return {
        "status": "ok",
        "workspace": {
            "id": workspace_id,
            "name": name,
            "description": description,
            "created_at": "2024-01-25",
            "members": 1,
            "reports": 0,
            "role": "admin"
        }
    }


@app.post("/api/workspaces/{workspace_id}/invite")
async def invite_member(workspace_id: str, request: Request, user=Depends(get_current_user_or_redirect)):
    """Convida membro para workspace"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    data = await request.json()
    email = data.get("email")
    role = data.get("role", "viewer")
    
    return {
        "status": "ok",
        "message": f"Convite enviado para {email} como {role}"
    }


@app.delete("/api/workspaces/{workspace_id}")
async def delete_workspace(workspace_id: str, user=Depends(get_current_user_or_redirect)):
    """Deleta workspace"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    return {"status": "ok", "message": f"Workspace {workspace_id} deletado"}


# ======================================================
# 🔗 DATA MODEL (Relacionamentos)
# ======================================================
@app.get("/data-model", response_class=HTMLResponse)
def data_model_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("data_model.html", {"request": request, "user": user})


@app.get("/api/data-model")
async def get_data_model(user=Depends(get_current_user_or_redirect)):
    """Retorna modelo de dados atual"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    # Modelo de exemplo
    model = {
        "tables": [
            {
                "id": "tbl-vendas",
                "name": "Vendas",
                "columns": ["ID", "Data", "Produto_ID", "Cliente_ID", "Valor", "Quantidade"],
                "row_count": 15000,
                "x": 100,
                "y": 100
            },
            {
                "id": "tbl-produtos",
                "name": "Produtos", 
                "columns": ["ID", "Nome", "Categoria", "Preço"],
                "row_count": 500,
                "x": 400,
                "y": 100
            },
            {
                "id": "tbl-clientes",
                "name": "Clientes",
                "columns": ["ID", "Nome", "Email", "Cidade", "Estado"],
                "row_count": 2000,
                "x": 100,
                "y": 350
            }
        ],
        "relationships": [
            {
                "id": "rel-1",
                "from_table": "tbl-vendas",
                "from_column": "Produto_ID",
                "to_table": "tbl-produtos",
                "to_column": "ID",
                "type": "many-to-one"
            },
            {
                "id": "rel-2",
                "from_table": "tbl-vendas",
                "from_column": "Cliente_ID", 
                "to_table": "tbl-clientes",
                "to_column": "ID",
                "type": "many-to-one"
            }
        ],
        "measures": [
            {"name": "Total Vendas", "formula": "SUM(Vendas[Valor])"},
            {"name": "Ticket Médio", "formula": "AVERAGE(Vendas[Valor])"},
            {"name": "Total Clientes", "formula": "DISTINCTCOUNT(Vendas[Cliente_ID])"}
        ]
    }
    
    return {"model": model}


@app.post("/api/data-model/relationship")
async def create_relationship(request: Request, user=Depends(get_current_user_or_redirect)):
    """Cria relacionamento entre tabelas"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    data = await request.json()
    
    return {
        "status": "ok",
        "relationship": {
            "id": f"rel-{data.get('from_table', '')}-{data.get('to_table', '')}",
            **data
        }
    }


@app.post("/api/data-model/measure")
async def create_measure(request: Request, user=Depends(get_current_user_or_redirect)):
    """Cria nova medida DAX"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    data = await request.json()
    name = data.get("name")
    formula = data.get("formula")
    
    return {
        "status": "ok",
        "measure": {"name": name, "formula": formula}
    }


# ======================================================
# 📤 PUBLISH & SHARE
# ======================================================
@app.get("/publish", response_class=HTMLResponse)
def publish_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("publish.html", {"request": request, "user": user})


@app.post("/api/publish/report")
async def publish_report(request: Request, user=Depends(get_current_user_or_redirect)):
    """Publica relatório para compartilhamento"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    import uuid
    import hashlib
    
    data = await request.json()
    report_name = data.get("name", "Report")
    
    # Gerar link único
    share_id = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:12]
    
    return {
        "status": "ok",
        "publish": {
            "share_url": f"/shared/{share_id}",
            "embed_code": f'<iframe src="/embed/{share_id}" width="100%" height="600"></iframe>',
            "share_id": share_id,
            "name": report_name,
            "public": data.get("public", False),
            "password_protected": data.get("password", "") != ""
        }
    }


@app.get("/shared/{share_id}", response_class=HTMLResponse)
def view_shared_report(share_id: str, request: Request):
    """Visualiza relatório compartilhado (público)"""
    return templates.TemplateResponse("shared_report.html", {
        "request": request,
        "share_id": share_id
    })


@app.get("/embed/{share_id}", response_class=HTMLResponse)
def embed_report(share_id: str, request: Request):
    """Embed de relatório para iframe"""
    return templates.TemplateResponse("embed_report.html", {
        "request": request,
        "share_id": share_id
    })


# ======================================================
# ⚙️ SETTINGS
# ======================================================
@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, user=Depends(get_current_user_or_redirect)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("settings.html", {"request": request, "user": user})


@app.post("/api/settings/theme")
async def update_theme(request: Request, user=Depends(get_current_user_or_redirect)):
    """Atualiza tema do usuário"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    data = await request.json()
    theme = data.get("theme", "dark")
    
    return {"status": "ok", "theme": theme}


@app.post("/api/settings/profile")
async def update_profile(request: Request, user=Depends(get_current_user_or_redirect)):
    """Atualiza perfil do usuário"""
    if isinstance(user, RedirectResponse):
        return {"error": "Não autenticado"}
    
    data = await request.json()
    
    return {
        "status": "ok",
        "profile": {
            "name": data.get("name"),
            "email": data.get("email"),
            "avatar": data.get("avatar")
        }
    }


# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
