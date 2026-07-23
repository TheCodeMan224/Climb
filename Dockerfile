# Imagen del backend Climb (Fase 1): app Flet web + psycopg2 hacia PostgreSQL.
FROM python:3.11-slim

# libpq-dev + build-essential para psycopg2.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8550
# main.py arranca Flet en modo web sobre $PORT (AppView.WEB_BROWSER).
CMD ["python", "main.py"]
