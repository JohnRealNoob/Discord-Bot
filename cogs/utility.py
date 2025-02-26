import discord
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warn a user with a reason")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The member to warn", reason="The reason for the warning")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        """Warn a specified member with a given reason."""
        if user == interaction.user:
            await interaction.response.send_message("You cannot warn yourself!", ephemeral=True)
            return
        if user.bot:
            await interaction.response.send_message("You cannot warn bots!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Warning",
            description=f"You’ve been warned in **{interaction.guild.name}** for: {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Warned by {interaction.user}")

        try:
            await user.send(embed=embed)
            await interaction.response.send_message(f"Successfully warned {user.mention} for: `{reason}`", ephemeral=True)
        except discord.Forbidden:
            print(f"Could not DM {user.name}. DMs might be disabled or the bot is blocked.")
            await interaction.response.send_message(
                f"Warned {user.mention} for: `{reason}`, but they couldn’t be DM’d (DMs disabled or bot blocked).",
                ephemeral=True
            )
        except discord.HTTPException as e:
            print(f"DM error for {user.name}: {e}")
            await interaction.response.send_message(
                f"Failed to DM {user.mention} for: `{reason}` due to an error: {e}",
                ephemeral=True
            )
    
    @app_commands.command(name="src", description="github source code")
    async def srcode(self, interaction: discord.Interaction):
        await interaction.response.send_message("https://github.com/JohnRealNoob/Discord-Bot", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))