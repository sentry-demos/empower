FROM python:3.11-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

CMD exec gunicorn -b :$PORT -w 1 --threads 4 --timeout 30 main:app
