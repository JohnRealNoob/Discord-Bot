import discord
from discord.ext import commands
from discord import app_commands

import os
from dotenv import load_dotenv

import ai.chatgpt
from languages.languages import Language
from discord_features.pagination import Pagination
from file_functions.logging import discord_log
from file_functions.hex import Hex
from file_functions.json import ChannelJson
from file_functions.logging import discord_log
import ai

import server.webserver

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID =  int(os.environ.get("GUILD_ID"))
GUILD_ID = discord.Object(id=ID)
gpt_ai = ai.chatgpt.Chatgpt(os.getenv("OPENAI_API_KEY"))
class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}")

        try:
            guild = discord.Object(id=ID)
            synced = await self.tree.sync(guild=guild)
            print(f"synced {len(synced)} commands to guild {guild.id}")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_member_join(interaction: discord.Interaction, member: discord.Member):
        greet_channel_id = ChannelJson.load("greet")
        greet_image = ChannelJson.load("greet_image")
        join_time = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

        if greet_channel_id == None:
            return
        
        greet_channel = await client.fetch_channel(greet_channel_id)

        embed = discord.Embed(title=f"WELCOME {member.display_name}", description=f"{member.mention}", color=discord.Colour.greyple())
        embed.add_field(name="Happy to see 😊", value="A smile is a welcomed sight that invites people in")
        embed.set_image(url=greet_image)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar)
        embed.set_footer(text=f"{member.guild.name} ⋅ {join_time}", icon_url=member.guild.icon.url if member.guild.icon else None)

        await greet_channel.send(embed=embed)

    async def on_member_remove(interaction: discord.Interaction, member: discord.Member):
        goodbye_channel_id = ChannelJson.load("goodbye")
        goodbye_image = ChannelJson.load("goodbye_image")
        join_time = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

        if goodbye_channel_id == None:
            return
        goodbye_channel = await client.fetch_channel(goodbye_channel_id)

        embed = discord.Embed(title=f"GOODBYE {member.display_name}", description=f"{member.mention}", color=discord.Colour.greyple())
        embed.add_field(name="We hope not to see you again 🤬", value="Every new beginning comes from some other beginning’s end.")
        embed.set_image(url=goodbye_image)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar)
        embed.set_footer(text=f"{member.guild.name} ⋅ {join_time}" ,icon_url=member.guild.icon.url if member.guild.icon else None)

        await goodbye_channel.send(embed=embed)

intents = discord.Intents.all()
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
    channel_type = "greet"
    ChannelJson.write(key_type=channel_type, info=channel.id)

    await interaction.response.send_message(f"```You set {channel} to greet channel```")

@client.tree.command(name="set_welcome_image", description="Set Image to Welcome User", guild=GUILD_ID)
async def set_welcome_image(interaction: discord.Interaction, url: str):
    key_type = "greet_image"
    ChannelJson.write(key_type=key_type, info=url)

    await interaction.response.send_message(f"```You set {url} to greet ```")

@client.tree.command(name="set_goodbye_channel", description="Set Channel to Goodbye User", guild=GUILD_ID)
async def set_goodbye_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    channel_type = "goodbye"
    ChannelJson.write(key_type=channel_type, info=channel.id)

    await interaction.response.send_message(f"```You set {channel} to goodbye channel```")

@client.tree.command(name="set_goodbye_image", description="Set Image to Goodbye User", guild=GUILD_ID)
async def set_goodbye_image(interaction: discord.Interaction, url: str):
    key_type = "goodbye_image"
    ChannelJson.write(key_type=key_type, info=url)

    await interaction.response.send_message(f"```You set {url} to goodbye ```")

@client.tree.command(name="ask", description="ask bot power by chatgpt-4o", guild=GUILD_ID)
async def ask_chatgpt(interaction: discord.Interaction, question: str):
    response = ai.chatgpt.ai.reponse(question)

    await interaction.response.send_message(response)

client.run(TOKEN)

server.webserver.keep_alive()