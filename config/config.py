import os
from dotenv import load_dotenv
import discord

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID =  int(os.environ.get("GUILD_ID"))
GUILD_ID = discord.Object(id=ID)