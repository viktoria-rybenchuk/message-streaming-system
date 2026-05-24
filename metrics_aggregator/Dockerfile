FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY metrics_aggregator/ metrics_aggregator/
COPY .env .env

RUN mkdir -p /app/logs /app/reports

CMD ["python", "-m", "metrics_aggregator.main", "/app/logs"]