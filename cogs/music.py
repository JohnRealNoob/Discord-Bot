import discord
from discord.ext import commands
from discord  import app_commands
import asyncio
import yt_dlp
import json
import urllib.parse, urllib.request, re
from utils.manage_file import *
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.song_cache = {}
        self.voice_clients = {}
        self.timeout_duration = 60
        self.dirname = "data"
        self.filename = "music_playlist.json"
        self.file_path = check_file_exists(dirname=self.dirname, filename=self.filename)
        self.youtube_base_url = 'https://www.youtube.com/'
        self.youtube_results_url = self.youtube_base_url + 'results?'
        self.youtube_watch_url = self.youtube_base_url + 'watch?v='
        self.yt_dl_options = {"format": "bestaudio/best"}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    async def search_yt(self, interaction: discord.Interaction, music: str):
        if "youtube.com" not in music and "youtu.be" not in music:
            query_string = urllib.parse.urlencode({"search_query": music})
            content = urllib.request.urlopen(self.youtube_results_url + query_string)
            search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

            if not search_results:
                await interaction.followup.send("No YouTube results found.", ephemeral=True)
                return None
        else:
            music = self.youtube_watch_url + search_results[0]  # Convert search result to URL

        return music

    async def extract_song(self, interaction: discord.Interaction, music: str):
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(music, download=False))
            url = data['url']
            title = data.get("title", "Unknown title")
        except Exception as e:
            print(f"Error fetching YouTube video: {e}")
            await interaction.followup.send("Failed to retrieve the song.", ephemeral=True)
            return None
        return title, url
    
    async def add_queues(self, interaction: discord.Interaction, url: str, music: str, title: str):
        # Queue the song if another is playing
        self.queues.setdefault(interaction.guild_id, []).append(url)
        self.song_cache.setdefault(interaction.guild_id, []).append((music, title))

    async def play(self, interaction: discord.Interaction, url: str):
        # Play audio
        guild_id = interaction.guild_id

        player = discord.FFmpegOpusAudio(url, **self.ffmpeg_options)

        channel = interaction.user.voice.channel
        vc = self.voice_clients.get(interaction.guild.id)

        if vc is None or not vc.is_connected():
            try:
                vc = await channel.connect()
                self.voice_clients[interaction.guild.id] = vc
            except Exception as e:
                print(f"Voice connection error: {e}")
                await interaction.followup.send("Failed to connect to the voice channel.", ephemeral=True)
                return

        vc.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop))

    async def play_next(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id

        # Ensure queue exists and is not empty
        if guild_id not in self.queues or not self.queues[guild_id]:
            # No more songs in the queue, disconnect from voice if no one is in the channel
            voice_client = self.voice_clients.get(guild_id)
            if voice_client and not voice_client.channel.members:
                await voice_client.disconnect()  # Disconnect the bot
            return  # No more songs, do nothing

        # Get next song
        link = self.queues[guild_id].pop(0) 

        # Ensure bot is still connected to voice
        voice_client = self.voice_clients.get(guild_id)
        if not voice_client or not voice_client.is_connected():
            return  # Bot is not in voice, stop processing

        # Call play function with the new song
        await self.play(interaction=interaction, url=link)
    
    async def add_playlist(self, interaction: discord.Interaction, pl_name: str, title: str, url: str):
        user_id = interaction.user.id

        playlist = load_json(self.file_path) or {}

        if user_id not in playlist:
            playlist[user_id] = {}  # Initialize a dictionary for the user

        if pl_name not in playlist[user_id]:
            playlist[user_id][pl_name] = []  # Initialize the playlist as an empty list

        playlist.que[user_id][pl_name].append((title, url))

        with open(self.file_path, "w") as file:
            json.dump(playlist, file, indent=4)

    async def add_queue_playlist(self, interaction: discord.Interaction, pl_name: str):
        user_id = interaction.user.id
        
        playlist = load_json(self.file_path) or {}

        for song in playlist[user_id][pl_name]:
            music = song[1]
            url = await self.extract_song(interaction=interaction, music=music)
            self.queues.setdefault(interaction.guild_id, []).append(url)
            self.song_cache.setdefault(interaction.guild_id, []).append(song)

    @app_commands.command(name="play", description="play music")
    async def play_music(self, interaction: discord.Interaction, music: str):
        await interaction.response.defer(thinking=True)  # Prevents interaction timeout

        # Ensure user is in a voice channel
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You need to be in a voice channel!", ephemeral=True)
            return

        # Get or connect to the voice client
        vc = interaction.guild.voice_client
        if not vc:
            try:
                vc = await interaction.user.voice.channel.connect()
                self.voice_clients[interaction.guild_id] = vc
            except Exception as e:
                print(f"Voice connection error: {e}")
                await interaction.followup.send("Failed to connect to the voice channel.", ephemeral=True)
                return

        song_url = None
        video_title = None

        music = await self.search_yt(interaction=interaction, music=music)
        if not music:
            return

        result = await self.extract_song(interaction=interaction, music=music)
        video_title, song_url = result if result else ("Unknown Title", None)
        if not song_url:
            return

        # Create an embed message
        embed_play = discord.Embed(
            title=f"▶️ | Now Playing: {video_title}",
            description=f"Requested by {interaction.user.mention}",
            color=discord.Colour.blurple()
        )
        embed_play.add_field(name="🔗 Link", value=f"[Watch on YouTube]({music})", inline=False)

        embed_append = discord.Embed(
            title= f"▶️ | Added {video_title} to the queue.",
            description=f"Requested by {interaction.user.mention}",
            color=discord.Colour.blurple()
        )
        embed_append.add_field(name="🔗 Link", value=f"[Watch on YouTube]({music})", inline=False)

        if vc.is_playing():
            await self.add_queues(interaction=interaction, url=song_url, music=music, title=video_title)
            await interaction.followup.send(embed=embed_append)
        else:
            await self.play(interaction=interaction, url=song_url)
            await interaction.followup.send(embed=embed_play)  # Correctly sends the embed

    @app_commands.command(name="add_playlist", description="Add song to your playlist")
    async def add_pl(self, interaction: discord.Interaction, pl_name: str, music):

        music = await self.search_yt(interaction=interaction, music=music)
        if not music:
            return
        result = await self.extract_song(interaction=interaction, music=music)
        video_title, song_url = result if result else ("Unknown Title", None)
        if not song_url:
            return
        
        await self.add_playlist(interaction=interaction, pl_name=pl_name, title=video_title, url=music)

    @app_commands.command(name="clear_queue", description="Clear bot current queue")
    async def clear_queue(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if interaction.guild_id in self.queues:
            self.queues[interaction.guild_id].clear()
            await interaction.followup.send("Queue cleared!", ephemeral=True)
        else:
            await interaction.followup.send("There is no queue to clear", ephemeral=True)

    @app_commands.command(name="pause", description="Pause the currently playing song")
    async def pause(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        voice_client = interaction.guild.voice_client  # Get the voice client directly

        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.followup.send("⏸️ Paused the music!", ephemeral=True)
        else:
            await interaction.followup.send("❌ No music is currently playing.", ephemeral=True)

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client  # Get the voice client directly

        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("▶️ Resumed the music!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No music is paused.", ephemeral=True)

    @app_commands.command(name="skip", description="Skip the currently playing song")
    async def skip(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = interaction.guild.id
        voice_client = self.voice_clients.get(guild_id)

        if not voice_client or not voice_client.is_playing():
            await interaction.followup.send("❌ No music is currently playing.", ephemeral=True)
            return

        # Stop the current song
        voice_client.stop()

        # If there's another song in the queue, play the next one
        await self.play_next(interaction)

        await interaction.followup.send("⏭️ Skipped to the next song!", ephemeral=True)

    @app_commands.command(name="stop", description="Stop the music and clear the queue")
    async def stop(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        voice_client = self.voice_clients.get(guild_id)

        if voice_client:
            voice_client.stop()  # Stop the current song
            self.queues[guild_id] = []  # Clear the queue
            await voice_client.disconnect()  # Disconnect from the voice channel
            await interaction.response.send_message("⏹️ Stopped the music and cleared the queue!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ The bot is not connected to a voice channel.", ephemeral=True)

    @app_commands.command(name="queue", description="Show the current music queue")
    async def queue(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        guild_id = interaction.guild_id

        # Create an embed to display the queue
        embed = discord.Embed(title="🎶 | Music Queue", color=discord.Colour.blurple())

        # Check if queue exists and is not empty
        if guild_id not in self.queues or not self.queues[guild_id]:
            embed.description = "The queue is currently empty"
            await interaction.followup.send(embed=embed)
            return
        
        # List the songs in the queue
        queue_list = ""
        for index, song in enumerate(self.song_cache[guild_id], start=1):
            url, title = song
            queue_list += f"**{index}.** [{title}]({url})\n"

        embed.description = queue_list

        # Send the queue embed
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))