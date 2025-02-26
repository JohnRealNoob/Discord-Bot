FROM python:3.13.2-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]