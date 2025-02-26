import discord
from discord.ext import commands
import asyncio
from config import TOKEN, ConfigError, PREFIX, INTENTS
from utils import setup_logging

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX, intents=INTENTS)

    async def on_ready(self):
        print(f"Logged on as {self.user} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} guilds")

    async def setup_hook(self):
        print("Setting up bot...")
        await self.load_extension("cogs")  # Load all cogs via __init__.py
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands at startup.")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

async def main():
    bot = Client()
    try:
        setup_logging()
        await bot.start(TOKEN)
    except ConfigError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure DISCORD_TOKEN and OWNER_ID are set correctly.")
    except discord.errors.LoginFailure:
        print("Invalid Discord token. Please verify your DISCORD_TOKEN in .env")
    except KeyboardInterrupt:
        print("Bot stopped by user")
        await bot.close()  
    except Exception as e:
        print(f"Bot failed to start: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())