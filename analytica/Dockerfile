# Dockerfile para deploy do ANALYTIC.A PRO
FROM python:3.12-slim

# Trabalha dentro da pasta do app para manter imports relativos (security, etl, etc.)
WORKDIR /app/analytica

# Copia apenas o requirements da pasta analytica
COPY analytica/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia o código do app
COPY analytica/. .

EXPOSE 8080

# Usa uvicorn com mais workers (ajusta via env UVICORN_WORKERS se quiser)
ENV UVICORN_WORKERS=2
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8080 --workers ${UVICORN_WORKERS} --timeout-keep-alive 20"]
