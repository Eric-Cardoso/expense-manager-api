FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt 

COPY . /app/

