import discord
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command: Warn user
    @app_commands.command(name="warn", description="warn user")
    @app_commands.checks.has_permissions(administrator=True)
    async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):

        embed = discord.Embed(title="Warning", description=reason, color=discord.Color.red())

        try:
            await member.send(embed=embed)  # Attempt to send the DM
        except discord.Forbidden:
            print(f"Could not DM {member.name}. DMs might be disabled or the bot is blocked.")
        except discord.HTTPException as e:
            print(f"An error occurred while sending the DM to {member.name}: {e}")
    
async def setup(bot):
    await bot.add_cog(Utility(bot))