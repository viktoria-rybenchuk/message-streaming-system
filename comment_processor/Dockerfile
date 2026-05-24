FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY comment_processor/ comment_processor/
COPY .env .env

RUN mkdir -p /app/logs

CMD ["python", "-m", "comment_processor.main"]