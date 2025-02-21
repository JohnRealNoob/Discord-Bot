# bot.py
import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN, ConfigError, PREFIX, INTENTS, EXCLUDED_COGS

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX, intents=INTENTS)

    async def on_ready(self):
        print(f"Logged on as {self.user} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} guilds")

    async def setup_hook(self):
        print("Setting up bot...")
        await self.load_extension("cogs")
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands at startup.")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

client = Client()

if __name__ == "__main__":
    try:
        asyncio.run(client.start(TOKEN))
    except ConfigError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure DISCORD_TOKEN and OWNER_ID are set correctly.")
    except discord.errors.LoginFailure:
        print("Invalid Discord token. Please verify your DISCORD_TOKEN in .env")
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot failed to start: {e}")