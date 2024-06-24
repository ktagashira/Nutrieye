FROM python:slim

WORKDIR /app
COPY requirements.lock ./
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

WORKDIR /
COPY ./app /app/
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080