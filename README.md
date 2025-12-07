# 📊 ANALYSTIC.A — Premium Analytics Platform

<div align="center">

![ANALYSTIC.A](https://img.shields.io/badge/ANALYSTIC.A-Premium%20Analytics-667eea?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Status](https://img.shields.io/badge/Status-Online-00d4aa?style=for-the-badge)
![Version](https://img.shields.io/badge/Versão-2.0-f093fb?style=for-the-badge)

### 🌐 **ACESSE A PLATAFORMA**

**Produção (Fly.io):** https://analystica.fly.dev


## 🚀 Deploy Profissional — Fly.io (produção)

**URL pública para clientes:**  
`https://analystica.fly.dev/`

### Como publicar (usando o que está em `/analytica`)
1. Instale o CLI: `curl -L https://fly.io/install.sh | sh` e exporte `PATH="$HOME/.fly/bin:$PATH"`
2. Login: `flyctl auth login`
3. Criar/app ou usar existente (nomes em minúsculas): `flyctl apps create analystica`
4. Deploy (usa `analytica/fly.toml` e `analytica/Dockerfile`):
   ```bash
   cd /home/luduranoficiall/Área\ de\ trabalho/TRABALHOS\ DA\ EXTRAORDINARIA.AI/TRABALHOS\ DA\ EXTRAORDINARIA.AI/📊\ ANALYTIC.A
   flyctl deploy --config analytica/fly.toml --dockerfile analytica/Dockerfile --app analystica
   ```
5. Secrets obrigatórias (exemplo):  
   `flyctl secrets set DB_HOST=... DB_NAME=... DB_USER=... DB_PASS=... SECRET_KEY=... HMAC_SECRET=... GEMINI_API_KEY=...`
6. Garantir 24/7:  
   `flyctl scale count 1` (ou 2 para HA) e confirme `auto_stop_machines = false` e `min_machines_running = 1` no `fly.toml`.
7. Logs/health: `flyctl logs -a analystica` e `flyctl status`.

**Sempre use a URL pública gerada pela Fly.io para o back-end.**

---

# 🔗 [**URL PÚBLICA FLY.IO**](https://analystica.fly.dev)

---

**A plataforma de Business Intelligence mais avançada do Brasil.**  
**Transforme seus dados em decisões inteligentes com IA integrada.**


[✨ Acessar Plataforma (Fly.io)](https://analystica.fly.dev) • [📚 Documentação](#documentação)

</div>

---

## 🚀 Recursos Principais

| Recurso | Descrição |
|---------|-----------|
| 🤖 **IA Integrada** | Ollama + Gemini 1.5 Flash para análises preditivas |
| 📊 **Dashboards Dinâmicos** | Visualizações interativas com drag & drop |
| 🔗 **Modelagem de Dados** | Relacionamentos visuais estilo Power BI |
| 👥 **Colaboração** | Workspaces compartilhados em tempo real |
| 🐍 **Python Nativo** | Execute scripts diretamente na plataforma |
| 🔒 **Segurança Enterprise** | Criptografia end-to-end + LGPD |

---

## 📘 MANUAL TÉCNICO DO DESENVOLVEDOR (Dev Manual)

### 1. Introdução
Este documento descreve todos os componentes técnicos do sistema ANALYTIC.A PRO ULTRA SECURE, sua arquitetura, padrões de desenvolvimento, requisitos, pipelines, APIs e melhores práticas de manutenção.

**Destinado a:**
- Desenvolvedores backend
- Desenvolvedores frontend
- DevOps / SRE
- Engenheiros de dados
- Integradores de API
- Times de segurança

### 2. Arquitetura do Sistema
O sistema utiliza uma arquitetura cloud-native, distribuída e segura.

```
ANALYTIC.A PRO ULTRA SECURE
│
├── API Gateway (FastAPI)
├── Auth Service (JWT + RSA 4096)
├── ETL Service (Event-driven)
├── Chart Service (Plotly)
├── GPT Service (Local + OpenAI)
├── Redis (Cache + Streams)
├── PostgreSQL (Data)
├── WebSockets Broadcast
├── Prometheus + Grafana
└── Frontend Ultra Premium
```

**Tecnologias:** Python 3.11, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, Plotly, Prometheus, Grafana, WebSockets, OpenAI + IA Local

### 3. Estrutura do Repositório
```
/analytica
 ├── app.py
 ├── db/
 │    └── database.py
 ├── etl/
 │    └── etl_engine.py
 ├── charts/
 │    ├── chart_engine.py
 │    └── realtime_publisher.py
 ├── gpt/
 │    ├── gpt_engine.py
 │    ├── cloud_engine.py
 │    └── local_engine.py
 ├── realtime/
 │    └── ws_server.py
 ├── security/
 │    ├── auth.py
 │    ├── crypto.py
 │    ├── rsa_engine.py
 │    ├── hmac_sign.py
 │    └── middleware.py
 ├── tenants/
 │    └── manager.py
 ├── static/
 ├── templates/
 ├── monitoring/
 │    └── prometheus.yml
 ├── k8s/
 │    ├── deployment.yml
 │    ├── service.yml
 │    ├── ingress.yml
 │    └── hpa.yml
 └── .github/
      └── workflows/deploy.yml
```

### 4. Instalação e Setup Local
**Requisitos:** Python 3.11, PostgreSQL 15+, Redis, Docker (opcional), OpenAI Key

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

### 5. Configuração de Variáveis de Ambiente
```
DB_URL=
OPENAI_API_KEY=
JWT_SECRET=
HMAC_SECRET=
LOCAL_LLM_URL=
REDIS_HOST=
TENANT_ID=
```

### 6. Segurança
- Autenticação: JWT RS256
- Senhas: PBKDF2
- Payloads: HMAC SHA-256
- Dados sensíveis: AES-256-GCM
- Token expira em 60 min
- Refresh via endpoint seguro
- Auditoria assinada via HMAC
- Rotação automática de chaves AES

### 7. Endpoints Principais
| Método | Rota      | Descrição           |
|--------|-----------|---------------------|
| GET    | /         | Dashboard           |
| POST   | /login    | Login JWT           |
| POST   | /upload   | Upload + ETL        |
| GET    | /chart    | Render de gráfico   |
| GET    | /insights | GPT Insights        |
| GET    | /metrics  | Prometheus          |

### 8. ETL (Event-Driven)
- Eventos: UPLOAD_COMPLETED, NEW_DATA, ANALYSIS_REQUEST
- Upload validado por HMAC
- ETL transforma e insere dados
- Publica evento Redis Stream
- WebSocket atualiza gráfico em tempo real

### 9. WebSockets (Tempo real)
`ws://SEU_DOMINIO/ws`

Payload exemplo:
```json
{
  "table": "vendas",
  "x": "mes",
  "y": "total"
}
```

### 10. IA (Local + OpenAI)
- IA Local (Ollama): http://localhost:11434/api/generate
- OpenAI GPT-4.1 (fallback premium)

### 11. Testes
- Unit: pytest
- Segurança: OWASP ZAP
- Performance: Locust
- Carga: k6

### 12. Deploy
- Docker: `docker-compose up -d`
- Kubernetes: `kubectl apply -f k8s/`
- CI/CD GitHub Actions: Automático no push para main.

---

## 📘 2. MANUAL DO CLIENTE / USUÁRIO FINAL (User Guide)

### 1. Acesso ao Sistema
Acesse via navegador: `https://SEU-DOMINIO.com.br`

### 2. Dashboard Principal
- KPIs principais
- Gráficos interativos
- Tendências
- Indicadores de performance
- Filtros e drill-down

### 3. Como fazer upload de dados
- Vá em Upload
- Envie Excel, CSV ou JSON
- Aguarde processamento
- Gráficos atualizam automaticamente

### 4. Gráficos em Tempo Real
- Dashboard atualiza automaticamente
- Novos pontos, linhas ou barras
- Sem recarregar a página

### 5. Insights com Inteligência Artificial
- Vá em PREDITIVI.A
- Digite uma pergunta
- IA analisa dados e retorna insights
- IA Local (LLaMA/Mistral) + OpenAI GPT-4.1

### 6. Segurança
- Criptografia ponta-a-ponta
- Tokens seguros
- Auditoria
- Isolamento por cliente

### 7. Versão Mobile
- Android, iOS, PWA
- Basta acessar no navegador ou instalar como PWA

### 8. Suporte
- Canal de suporte interno (via time de desenvolvimento)

---

## 🖥️ 3. LANDING PAGE PREMIUM

O arquivo `landing.html` está pronto para uso em seu domínio ou pasta raiz do projeto.

---

**ANALYTIC.A PRO ULTRA SECURE — O BI mais avançado, seguro e inteligente do mercado.**
