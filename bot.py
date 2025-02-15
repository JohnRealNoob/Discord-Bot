import discord
from discord.ext import commands
import asyncio
import os
from config.config import TOKEN, GUILD_ID

intents = discord.Intents.all()  # Enable all intents if needed
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))  # Fast sync
        print(f"✅ Synced {len(synced)} commands for development.")
    except Exception as e:
        print(f"❌ Sync Error: {e}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"🔹 Loaded cog: {filename}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
