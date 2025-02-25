FROM python:3.12.2-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DISCORD_TOKEN="YOUR_BOT_TOKEN" \
    OWNER_ID="668317895616626711" \
    LAVALINK_HOST="lavalink" \
    LAVALINK_PORT="2333" \
    LAVALINK_PASSWORD="youshallnotpass"

CMD ["python", "main.py"]