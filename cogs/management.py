import discord
from discord import app_commands
from discord.ext import commands
import os

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_owner(self, interaction: discord.Interaction):
        """Check if the user is the bot owner."""
        return await self.bot.is_owner(interaction.user)

    @app_commands.command(name="sync", description="Sync all slash commands.")
    async def sync(self, interaction: discord.Interaction):
        """Sync all application commands (slash commands)."""
        if not await self.is_owner(interaction):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        try:
            synced = await self.bot.tree.sync()
            await interaction.response.send_message(f"Synced `{len(synced)}` commands globally!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Sync error: {e}", ephemeral=True)

    @app_commands.command(name="reload", description="Reload a cog or all cogs.")
    async def reload(self, interaction: discord.Interaction, cog: str):
        """Reload a specific cog or all cogs dynamically."""
        if not await self.is_owner(interaction):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        if cog.lower() == "all":
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
            cog_name = f"cogs.{cog}"
            try:
                await self.bot.reload_extension(cog_name)
                await interaction.response.send_message(f"Successfully reloaded `{cog}`!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Error reloading `{cog}`: {e}", ephemeral=True)

    @app_commands.command(name="load", description="load specific cog")
    async def load_cog(self, interaction: discord.Interaction, cog_name: str):
        if not await self.is_owner(interaction):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        try:
            # Load the cog
            await self.bot.load_extension(f"cogs.{cog_name}")
            await interaction.response.send_message(f"Cog {cog_name} loaded successfully.")
        except Exception as e:
            await interaction.response.send_message(f"Error loading {cog_name}: {str(e)}")


async def setup(bot):
    await bot.add_cog(Management(bot))