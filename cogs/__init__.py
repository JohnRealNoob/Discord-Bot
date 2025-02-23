import os
from discord.ext import commands

async def setup(bot: commands.Bot):
    cogs_dir = os.path.dirname(__file__)
    cogs = [
        f"cogs.{filename[:-3]}"
        for filename in os.listdir(cogs_dir)
        if filename.endswith(".py") and filename != "__init__.py"
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)  # Use await since load_extension is async
            print(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Error loading {cog}: {e}")