import discord
from discord.ext import commands
from discord import app_commands

from utils.sqlite import update, get
class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = member.guild.id
        greet_channel_id = await get(guild_id=guild_id, type_="join_channel_id")
        greet_image = await get(guild_id=guild_id, type_="join_image")
        join_time = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

        if greet_channel_id == None:
            return
        
        greet_channel = await self.bot.fetch_channel(greet_channel_id)

        embed = discord.Embed(title=f"WELCOME {member.display_name}", description=f"{member.mention}", color=discord.Colour.greyple())
        embed.add_field(name="Happy to see 😊", value="A smile is a welcomed sight that invites people in")
        embed.set_image(url=greet_image)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar)
        embed.set_footer(text=f"{member.guild.name} ⋅ {join_time}", icon_url=member.guild.icon.url if member.guild.icon else None)

        await greet_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_id = member.guild.id
        goodbye_channel_id = get(guild_id=guild_id, type_="leave_channel_id")
        goodbye_image = await get(guild_id=guild_id, type_="leave_image")
        join_time = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

        if goodbye_channel_id == None:
            return
        goodbye_channel = await self.bot.fetch_channel(goodbye_channel_id)

        embed = discord.Embed(title=f"GOODBYE {member.display_name}", description=f"{member.mention}", color=discord.Colour.greyple())
        embed.add_field(name="We hope not to see you again 🤬", value="Every new beginning comes from some other beginning’s end.")
        embed.set_image(url=goodbye_image)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar)
        embed.set_footer(text=f"{member.guild.name} ⋅ {join_time}" ,icon_url=member.guild.icon.url if member.guild.icon else None)

        await goodbye_channel.send(embed=embed)

    @app_commands.command(name="set_welcome_channel", description="Set Channel to Welcome User")
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        interaction.response.defer()
        guild_id = interaction.guild.id

        try:
            await update(guild_id=guild_id, data=channel, type_="join_channel_id")
            await interaction.followup.send(f"```You set {channel} to welcome channel```")
        except Exception as e:
            await interaction.followup.send(f"```Fail to update welcome channel : {e}```")

    @app_commands.command(name="set_welcome_image", description="Set Image to Welcome User")
    async def set_welcome_image(self, interaction: discord.Interaction, url: str):
        interaction.response.defer()
        guild_id = interaction.guild.id
        
        try:
            await update(guild_id=guild_id, data=url, type_="join_image")
            await interaction.followup.send(f"```You set {url} to welcome images```")
        except Exception as e:
            await interaction.followup.send(f"```Fail to update welcome images : {e}```")

    @app_commands.command(name="set_goodbye_channel", description="Set Channel to Goodbye User")
    async def set_goodbye_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        interaction.response.defer()
        guild_id = interaction.guild.id

        try:
            await update(guild_id=guild_id, data=channel, type_="leave_channel_id")
            await interaction.followup.send(f"```You set {channel} to goodbye channel```")
        except Exception as e:
            await interaction.followup.send(f"```Fail to update goodbye channel : {e}```")

    @app_commands.command(name="set_goodbye_image", description="Set Image to Goodbye User")
    async def set_goodbye_image(self, interaction: discord.Interaction, url: str):
        interaction.response.defer()
        guild_id = interaction.guild.id
        
        try:
            await update(guild_id=guild_id, data=url, type_="leave_image")
            await interaction.followup.send(f"```You set {url} to goodbye images```")
        except Exception as e:
            await interaction.followup.send(f"```Fail to update goodbye images : {e}```")

async def setup(bot):
    await bot.add_cog(JoinLeave(bot))