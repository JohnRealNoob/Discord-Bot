# Overview
Discord-Bot is developed using [discord.py](https://github.com/Rapptz/discord.py) 
Store Data using [SQLite](https://www.sqlite.org/)
You can run the bot however you want. I have docker-compose for easy deployment on docker.
SQL is stored using db-data docker volume.

# Features
- Welcome and Goodbye message
- Transalte Languages using [deep-translator](https://github.com/nidhaloff/deep-translator)
- Play music using [Lavalink](https://github.com/lavalink-devs/Lavalink) and [Wavelink](https://github.com/PythonistaGuild/Wavelink) Library

# Installation

### Prerequisites

- [Docker](https://www.docker.com/)
- [Git](https://git-scm.com/)

### Clone Repository
```sh
git clone https://github.com/JohnRealNoob/Discord-Bot.git
cd Discord-Bot
```

### Create .env file

```sh
sudo nano .env
```

In .env file insert
```sh
DISCORD_TOKEN = "YOUR-BOT-TOKEN"
OWNER_ID = "YOUR-DISCORD-ID"
LAVALINK_HOST = "LAVALINK-HOST"
LAVALINK_PASSWORD = "LAVALINK-PASSWORD"
LAVALINK_PORT = "LAVALINK-PORT"
```

| VARIABLES | VALUES |
| -------- | ------- |
| `DISCORD_TOKEN` | [Discord Bot](https://discord.com/developers/applications) Token |
| `OWNER_ID` | [Discord User](https://discord.com/channels/@me) ID |
| `LAVALINK_HOST` | [Lavalink](https://github.com/lavalink-devs/Lavalink) Host IP Address |
| `LAVALINK_PASSWORD` | [Lavalink](https://github.com/lavalink-devs/Lavalink) Password |
| `LAVALINK_PORT` | [Lavalink](https://github.com/lavalink-devs/Lavalink) Port |

You can find free [Lavalink](https://lavalink.darrennathanael.com/) host here 

**Example**

```sh
DISCORD_TOKEN = diScod_bot76_toKEN
OWNER_ID = 12345678910
LAVALINK_HOST = lavalink_v4.muzykant.xyz
LAVALINK_PASSWORD = "https://discord.gg/v6sdrD9kPh"
LAVALINK_PORT = 443
```

# Deployment

In Discord-Bot Directory run
 ```sh
 docker compose up -d --build
 ```

To stop service
```sh
docker compose down
```

Restart service
```sh
docker compose restart
```

# License
Discord-Bot is open-source and available under the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.