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
        print(f"Commands loaded: {len(self.tree.get_commands())}")
        print(f"Logged in as {self.user}")
        try:
            synced = await self.tree.sync(guild=discord.Object(id=GUILD_ID))
            await asyncio.sleep(2)  # Wait to avoid rate limits
            await self.tree.sync()  # Sync globally (for production)

            print(f"Synced {len(synced)} commands for development.")
        except Exception as e:
            print(f"Sync Error: {e}")

    async def load_cogs(self):
        cogs = []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                cogs.append(f"cogs.{filename[:-3]}")
        for cog in cogs:
            module = import_module(cog)
            if module.__name__ in self.extensions:
                await self.reload_extension(module.__name__)
            else:
                await self.load_extension(module.__name__)

client = Client()
    
async def main():
    async with client:
        await client.load_cogs()
        await client.start(TOKEN)

asyncio.run(main())