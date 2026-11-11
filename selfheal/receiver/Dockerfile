FROM python:3.11-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# targets.json is copied in by deploy.sh from selfheal/targets.json
COPY main.py targets.json ./

CMD exec gunicorn -b :$PORT -w 1 --threads 4 --timeout 30 main:app
