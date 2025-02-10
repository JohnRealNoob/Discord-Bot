import discord
from discord.ext import commands
from discord import app_commands

import os, asyncio
from dotenv import load_dotenv

from languages.languages import Language
from discord_features.pagination import Pagination
from discord_features.logging import discord_log
from file_functions.hex import Hex
from music.help_cog import help_cog
from music.music_cog import music_cog

import server.webserver

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID =  int(os.environ.get("GUILD_ID"))
GUILD_ID = discord.Object(id=ID)

class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}")

        try:
            guild = discord.Object(id=ID)
            synced = await self.tree.sync(guild=guild)
            print(f"synced {len(synced)} commands to guild {guild.id}")
        except Exception as e:
            print(f"Error syncing commands: {e}")

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

client.remove_command("help")

discord_log()

lang_instance = Language()

# Command: Search Language Code
@client.tree.command(name="search_languages", description="Search for languages code", guild=GUILD_ID)
async def search_lang(interaction: discord.Interaction, lang: str):
    lang_code = Language.search_language_code(lang)
    await interaction.response.send_message(lang_code)

# Command: Translate Languages
@client.tree.command(name="translate", description="translate to any languages", guild=GUILD_ID)
async def translate(interaction: discord.Interaction, lang_code: str, *, text: str):
    translated = Language.translate_text(lang_code, text)
    await interaction.response.send_message(translated)

# Command: List All Available Language
@client.tree.command(name="show_languages", description="translate to any languages", guild=GUILD_ID)
async def show_lang(interaction: discord.Interaction):
    async def get_page(page: int):
        L = 10 # Element per page
        emb = discord.Embed(title="Available Languages", description="", color=discord.Color.dark_gray())
        offset = (page-1) * L
        for language in dict(list(lang_instance.languages.items())[offset:offset+L]).items():
            emb.description += f"{language[1].capitalize()} (`{language[0]}`)\n"
        emb.set_author(name=f"Requested by {interaction.user}")
        n = Pagination.compute_total_pages(len(lang_instance.languages), L)
        emb.set_footer(text=f"Page {page} from {n}")
        return emb, n

    await Pagination(interaction, get_page).navegate()

# Command: Warn user
@client.tree.command(name="warn", description="warn user", guild=GUILD_ID)
@app_commands.checks.has_permissions(administrator=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):

    embed = discord.Embed(title="Warning", description=reason, color=discord.Color.red())

    try:
        await member.send(embed=embed)  # Attempt to send the DM
    except discord.Forbidden:
        print(f"Could not DM {member.name}. DMs might be disabled or the bot is blocked.")
    except discord.HTTPException as e:
        print(f"An error occurred while sending the DM to {member.name}: {e}")

# Command: Make file from hex
@client.tree.command(name="make_file_hex", description="Make file from base 16", guild=GUILD_ID)
async def warn(interaction: discord.Interaction, hex_string: str):
    
    hex = Hex(hex_string)
    success, file_name = hex.make_from_hex()

    if success:
        await interaction.response.send_message(file=discord.File(file_name))
        os.remove(file_name)
    else:
        await interaction.response.send_message(file_name)

@client.tree.command(name="set_welcome_channel", description="Set Channel to Welcome User", guild=GUILD_ID)
async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    pass

@client.tree.command(name="set_goodbye_channel", description="Set Channel to Goodbye User", guild=GUILD_ID)
async def set_goodbye_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    pass

client.run(TOKEN)

server.webserver.keep_alive()