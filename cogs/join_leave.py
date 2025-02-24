import discord
from discord.ext import commands
from discord import app_commands

from utils.sqlite import get_channel, insert_channel
class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def load(self, member: discord.Member, join: bool):
        guild_id = member.guild.id

        info = get_channel(guild_id=guild_id, join=join)

        return info
    
    async def write(self, interaction: discord.Interaction, join: bool, channel: int):
        guild_id = interaction.guild_id

        if not insert_channel(guild_id=guild_id, join=join, leave_channel=channel):
            await interaction.followup.send("```Failed to update channel```") 

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        greet_channel_id = await self.load(member=member, join=True)
        greet_image = self.load(member=member, key_type="greet_image")
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
        goodbye_channel_id = await self.load(member=member, join=False)
        goodbye_image = self.load(member=member, key_type="goodbye_image")
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
        await self.write(interaction=interaction, join=True, info=channel.id)

        await interaction.response.send_message(f"```You set {channel} to greet channel```")

    @app_commands.command(name="set_welcome_image", description="Set Image to Welcome User")
    async def set_welcome_image(self, interaction: discord.Interaction, url: str):
        await self.write(interaction=interaction, join=False, info=url)

        await interaction.response.send_message(f"```You set {url} to greet ```")

    @app_commands.command(name="set_goodbye_channel", description="Set Channel to Goodbye User")
    async def set_goodbye_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        channel_type = "goodbye"
        await self.write(interaction=interaction, key_type=channel_type, info=channel.id)

        await interaction.response.send_message(f"```You set {channel} to goodbye channel```")

    @app_commands.command(name="set_goodbye_image", description="Set Image to Goodbye User")
    async def set_goodbye_image(self, interaction: discord.Interaction, url: str):
        key_type = "goodbye_image"
        await self.write(interaction=interaction, key_type=key_type, info=url)

        await interaction.response.send_message(f"```You set {url} to goodbye ```")

async def setup(bot):
    await bot.add_cog(JoinLeave(bot))