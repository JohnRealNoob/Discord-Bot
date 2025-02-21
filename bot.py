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
        await self.load_cogs()
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands at startup.")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def load_cogs(self):
        cogs_dir = "./cogs"
        if not os.path.exists(cogs_dir) or not os.path.isdir(cogs_dir):
            print("No 'cogs' directory found. Skipping cog loading.")
            return

        cogs = [
            f"cogs.{filename[:-3]}"
            for filename in os.listdir(cogs_dir)
            if filename.endswith(".py") and filename not in EXCLUDED_COGS
        ]

        for cog in cogs:
            try:
                if cog in self.extensions:
                    await self.reload_extension(cog)
                    print(f"Reloaded cog: {cog}")
                else:
                    await self.load_extension(cog)
                    print(f"Loaded cog: {cog}")
            except Exception as e:
                print(f"Error loading {cog}: {e}")

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