import discord
from discord.ext import commands
from discord import app_commands

import json
import os

class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        self.filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "channel.json")

    def load(self, key_type: str):
        # Load JSON data safely
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        
        try:
            info = data[key_type]
        except Exception:
            return None
        
        return info
    
    def write(self, key_type: str, info: int):
        # Load JSON data safely
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}  # Initialize if file doesn't exist or is empty

        data[key_type] = info

        # Write back to JSON file
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)

    @app_commands.command(name="set_welcome_channel", description="Set Channel to Welcome User")
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        channel_type = "greet"
        self.write(key_type=channel_type, info=channel.id)

        await interaction.response.send_message(f"```You set {channel} to greet channel```")

    @app_commands.command(name="set_welcome_image", description="Set Image to Welcome User")
    async def set_welcome_image(self, interaction: discord.Interaction, url: str):
        key_type = "greet_image"
        self.write(key_type=key_type, info=url)

        await interaction.response.send_message(f"```You set {url} to greet ```")

    @app_commands.command(name="set_goodbye_channel", description="Set Channel to Goodbye User")
    async def set_goodbye_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        channel_type = "goodbye"
        self.write(key_type=channel_type, info=channel.id)

        await interaction.response.send_message(f"```You set {channel} to goodbye channel```")

    @app_commands.command(name="set_goodbye_image", description="Set Image to Goodbye User")
    async def set_goodbye_image(self, interaction: discord.Interaction, url: str):
        key_type = "goodbye_image"
        self.write(key_type=key_type, info=url)

        await interaction.response.send_message(f"```You set {url} to goodbye ```")

async def setup(bot):
    bot.add_cog(JoinLeave(bot))