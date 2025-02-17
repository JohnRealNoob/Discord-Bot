import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queue = {}

    def search_yt(self, query):
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
                logging.debug(f"Found song: {info['title']} - {info['url']}")
                return {"title": info["title"], "url": info["url"]}
        except Exception as e:
            logging.error(f"Error searching for YouTube video: {e}")
            return None

    async def play_next(self, ctx):
        logging.debug("Playing next song")
        if ctx.guild.id in self.queue and self.queue[ctx.guild.id]:
            song = self.queue[ctx.guild.id].pop(0)
            logging.debug(f"Playing song: {song['title']}")
            source = discord.FFmpegPCMAudio(song["url"], executable="ffmpeg", before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
            ctx.voice_client.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))

    @app_commands.command(name="play", description="Plays a song from YouTube")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You need to be in a voice channel!", ephemeral=True)
            return

        vc = interaction.guild.voice_client
        if not vc:
            logging.debug("Connecting to voice channel...")
            vc = await interaction.user.voice.channel.connect()
            self.voice_clients[interaction.guild.id] = vc
        else:
            logging.debug("Already connected to a voice channel.")

        song = self.search_yt(query)
        if song is None:
            await interaction.followup.send("Could not find the song.", ephemeral=True)
            return

        if interaction.guild.id not in self.queue:
            self.queue[interaction.guild.id] = []

        self.queue[interaction.guild.id].append(song)

        if not vc.is_playing():
            logging.debug("Starting to play the first song in the queue.")
            await self.play_next(interaction)

        await interaction.followup.send(f"Added **{song['title']}** to the queue!")

    @app_commands.command(name="skip", description="Skips the current song")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            logging.debug("Skipping the song.")
            vc.stop()
            await interaction.response.send_message("Skipped the song!", ephemeral=True)
        else:
            await interaction.response.send_message("No song is playing.", ephemeral=True)

    @app_commands.command(name="stop", description="Stops playing music and disconnects")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            logging.debug("Disconnecting from the voice channel.")
            await vc.disconnect()
            self.queue.pop(interaction.guild.id, None)
            await interaction.response.send_message("Disconnected from voice channel.")
        else:
            await interaction.response.send_message("I'm not connected to any voice channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))