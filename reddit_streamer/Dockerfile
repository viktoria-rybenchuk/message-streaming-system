FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reddit_streamer/ reddit_streamer/
COPY datasets/ datasets/
COPY .env .env

CMD ["python", "-m", "reddit_streamer.main"]