import discord
from discord.ext import commands
import asyncio
import os
from config.config import TOKEN, GUILD_ID

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        #try:
            #synced = await self.tree.sync(guild=discord.Object(id=GUILD_ID))  # Fast sync
            #print(f"Synced {len(synced)} commands for development.")
        #except Exception as e:
            #print(f"Sync Error: {e}")

    async def load_cogs(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                extension = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(extension)  # Changed from client to self
                    print(f"Loaded cog: {extension}")
                except Exception as e:
                    print(f"Failed to load {extension}: {e}")

client = Client()

@client.tree.command(name="sync", description="owner only", guild=discord.Object(id=GUILD_ID))
async def sync(interaction: discord.Interaction):
    await client.tree.sync(guild=discord.Object(id=GUILD_ID))
    print('Command tree synced.')
    
async def main():

    async with client:
        await client.load_cogs()
        await client.start(TOKEN)

asyncio.run(main())
