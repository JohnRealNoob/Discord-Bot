# cogs/management.py
import discord
from discord import app_commands
from discord.ext import commands
import os
from config import OWNER_ID

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_ids = {OWNER_ID}

    async def is_owner(self, interaction: discord.Interaction):
        return interaction.user.id in self.owner_ids

    @app_commands.command(name="sync", description="Sync all slash commands.")
    async def sync(self, interaction: discord.Interaction):
        if not await self.is_owner(interaction):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        try:
            synced = await self.bot.tree.sync()
            await interaction.response.send_message(f"Synced `{len(synced)}` commands globally!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Sync error: {e}", ephemeral=True)

    def get_available_cogs(self):
        cogs_dir = "./cogs"
        if not os.path.exists(cogs_dir):
            return []
        return [f[:-3] for f in os.listdir(cogs_dir) if f.endswith(".py") and f != "__init__.py"]

    @app_commands.command(name="reload", description="Reload a cog or all cogs.")
    @app_commands.choices(cog=[
        app_commands.Choice(name="all", value="all"),
        *[app_commands.Choice(name=cog, value=cog) for cog in get_available_cogs()]
    ])
    async def reload(self, interaction: discord.Interaction, cog: app_commands.Choice[str]):
        if not await self.is_owner(interaction):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        selected_cog = cog.value
        if selected_cog.lower() == "all":
            reloaded = []
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py") and filename != "__init__.py":
                    cog_name = f"cogs.{filename[:-3]}"
                    try:
                        await self.bot.reload_extension(cog_name)
                        reloaded.append(cog_name)
                    except Exception as e:
                        await interaction.response.send_message(f"Error reloading `{cog_name}`: {e}", ephemeral=True)
                        return
            await interaction.response.send_message(f"Reloaded `{len(reloaded)}` cogs!", ephemeral=True)
        else:
            cog_name = f"cogs.{selected_cog}"
            try:
                await self.bot.reload_extension(cog_name)
                await interaction.response.send_message(f"Successfully reloaded `{selected_cog}`!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Error reloading `{selected_cog}`: {e}", ephemeral=True)

    @app_commands.command(name="load", description="Load a specific cog")
    @app_commands.choices(cog_name=[
        app_commands.Choice(name=cog, value=cog) for cog in get_available_cogs()
    ])
    async def load_cog(self, interaction: discord.Interaction, cog: app_commands.Choice[str]):
        if not await self.is_owner(interaction):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        try:
            await self.bot.load_extension(f"cogs.{cog.value}")
            await interaction.response.send_message(f"Cog `{cog.value}` loaded successfully.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error loading `{cog.value}`: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Management(bot))