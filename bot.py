import discord
from discord.ext import commands
import asyncio
import os
from importlib import import_module
from config.config import TOKEN, GUILD_ID

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def setup_hook(self):

        print("Loading cogs...")
        await self.load_cogs()

        # Sync commands once when bot starts
        
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands at startup.")
        except Exception as e:
            print(f"Sync error: {e}")

    async def load_cogs(self):
        cogs_dir = "./cogs"
        if not os.path.exists(cogs_dir) or not os.path.isdir(cogs_dir):
            print("No cogs directory found.")
            return  

        cogs = [f"cogs.{filename[:-3]}" for filename in os.listdir(cogs_dir) if filename.endswith(".py") and filename != "__init__.py"]
        
        for cog in cogs:
            try:
                if cog in self.extensions:
                    await self.reload_extension(cog)
                else:
                    await self.load_extension(cog)
                print(f"Loaded cog: {cog}")  
            except Exception as e:
                print(f"Error loading {cog}: {e}")

client = Client()

async def main():
    async with client:
        await client.start(TOKEN)

asyncio.run(main())  # Runs the bot asynchronously
