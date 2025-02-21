import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import os
from utils.manage_file import *

# Suppress yt-dlp logging noise
yt_dlp.utils.bug_reports_message = lambda: ''

# Playlist file paths
USER_PLAYLISTS_FILE = check_file_exists(dirname="data", filename="user_playlists.json")
GUILD_PLAYLISTS_FILE = check_file_exists(dirname="data", filename="guild_playlists.json")

class MusicPlayer:
    def __init__(self, guild, ydl):
        self.guild = guild
        self.ydl = ydl
        self.queue = []
        self.current_song = None
        self.voice_client = None

    def add_song(self, video_id, title):
        self.queue.append({"video_id": video_id, "title": title})
        if not self.current_song and self.voice_client:
            asyncio.run_coroutine_threadsafe(self.play_next_song(), self.voice_client.loop)

    async def play_next_song(self):
        if not self.queue:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()
            self.current_song = None
            return
        song = self.queue.pop(0)
        self.current_song = song
        await self.play_song(song)

    async def play_song(self, song):
        video_url = f"https://www.youtube.com/watch?v={song['video_id']}"
        try:
            with self.ydl:
                info = self.ydl.extract_info(video_url, download=False)
                audio_url = info['url']
            source = discord.FFmpegPCMAudio(audio_url, executable="ffmpeg")
            self.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(), self.voice_client.loop))
        except Exception as e:
            print(f"Error playing song {song['title']}: {e}")
            await self.play_next_song()

    def stop(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        self.queue.clear()
        self.current_song = None

    def skip(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()  # Triggers play_next_song via after callback

    def pause(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()

    def resume(self):
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()

    def get_queue(self):
        return self.queue.copy() if self.queue else []

    def clear_queue(self):
        self.queue.clear()

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cog_dir = os.path.dirname(os.path.abspath(__file__))
        cookie_path = os.path.join(cog_dir, '..', 'cookies.txt')
        self.ydl = yt_dlp.YoutubeDL({
            'format': 'bestaudio',
            'noplaylist': False,
            'quiet': True,
            'ignoreerrors': True,
            'cookiefile': cookie_path
        })
        self.music_players = {}
        # Load playlists
        self.user_playlists = load_json(file_path=USER_PLAYLISTS_FILE)
        self.guild_playlists = load_json(file_path=GUILD_PLAYLISTS_FILE)

    def get_music_player(self, guild):
        if guild.id not in self.music_players:
            self.music_players[guild.id] = MusicPlayer(guild, self.ydl)
        return self.music_players[guild.id]

    async def ensure_voice(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("You need to be in a voice channel to use this command!", ephemeral=True)
            return None
        guild = interaction.guild
        music_player = self.get_music_player(guild)
        if not music_player.voice_client or not music_player.voice_client.is_connected():
            music_player.voice_client = await interaction.user.voice.channel.connect()
        elif music_player.voice_client.channel != interaction.user.voice.channel:
            await interaction.response.send_message("I'm already in a different voice channel. Please join me there!", ephemeral=True)
            return None
        return music_player

    @app_commands.command(name="play", description="Play a song from a name or YouTube link (Supports playlists)")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        music_player = await self.ensure_voice(interaction)
        if not music_player:
            return
        try:
            with self.ydl:
                if "youtube.com" in query or "youtu.be" in query:
                    info = self.ydl.extract_info(query, download=False)
                else:
                    info = self.ydl.extract_info(f"ytsearch:{query}", download=False)
                    if 'entries' in info and info['entries']:
                        info = info['entries'][0]
                embed = discord.Embed(
                    title="🎶 | Music Queue Update",
                    description=f"Requested by {interaction.user.mention}",
                    color=discord.Colour.blurple()
                )
                added_count = 0
                if 'entries' in info:  # Playlist
                    for entry in info['entries']:
                        if entry and 'id' in entry and 'title' in entry:
                            music_player.add_song(entry['id'], entry['title'])
                            added_count += 1
                    embed.add_field(
                        name="Added to Queue",
                        value=f"**{added_count} song(s)** from the playlist",
                        inline=False
                    )
                else:  # Single song
                    video_id = info['id']
                    video_title = info['title']
                    music_url = f"https://www.youtube.com/watch?v={video_id}"
                    music_player.add_song(video_id, video_title)
                    embed.add_field(
                        name="Added to Queue",
                        value=f"[**{video_title}**]({music_url})",
                        inline=False
                    )
                await interaction.followup.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ | Error",
                description=f"Failed to add song: {str(e)}",
                color=discord.Colour.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="addplaylist", description="Add a song or playlist to a personal or guild playlist")
    @app_commands.describe(
        type="Type of playlist",
        playlist_name="Name of the playlist",
        query="Song name or YouTube link"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="Personal", value="personal"),
        app_commands.Choice(name="Guild", value="guild")
    ])
    async def addplaylist(self, interaction: discord.Interaction, type: app_commands.Choice[str], playlist_name: str, query: str):
        await interaction.response.defer()
        try:
            with self.ydl:
                if "youtube.com" in query or "youtu.be" in query:
                    info = self.ydl.extract_info(query, download=False)
                else:
                    info = self.ydl.extract_info(f"ytsearch:{query}", download=False)
                    if 'entries' in info and info['entries']:
                        info = info['entries'][0]
                songs_to_add = []
                if 'entries' in info:  # Playlist
                    for entry in info['entries']:
                        if entry and 'id' in entry and 'title' in entry:
                            songs_to_add.append({"video_id": entry['id'], "title": entry['title']})
                else:  # Single song
                    songs_to_add.append({"video_id": info['id'], "title": info['title']})
                if type.value == "personal":
                    user_id = str(interaction.user.id)
                    if user_id not in self.user_playlists:
                        self.user_playlists[user_id] = {}
                    if playlist_name not in self.user_playlists[user_id]:
                        self.user_playlists[user_id][playlist_name] = []
                    self.user_playlists[user_id][playlist_name].extend(songs_to_add)
                    write_json(file_path=USER_PLAYLISTS_FILE, data=self.user_playlists)
                    await interaction.followup.send(f"Added {len(songs_to_add)} song(s) to your personal playlist '{playlist_name}'.", ephemeral=True)
                else:  # guild
                    guild_id = str(interaction.guild.id)
                    if guild_id not in self.guild_playlists:
                        self.guild_playlists[guild_id] = {}
                    if playlist_name not in self.guild_playlists[guild_id]:
                        self.guild_playlists[guild_id][playlist_name] = []
                    self.guild_playlists[guild_id][playlist_name].extend(songs_to_add)
                    write_json(file_path=GUILD_PLAYLISTS_FILE, data=self.guild_playlists)
                    await interaction.followup.send(f"Added {len(songs_to_add)} song(s) to the guild playlist '{playlist_name}'.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to add to playlist: {str(e)}", ephemeral=True)

    @app_commands.command(name="playplaylist", description="Play a personal or guild playlist")
    @app_commands.describe(
        type="Type of playlist",
        playlist_name="Name of the playlist"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="Personal", value="personal"),
        app_commands.Choice(name="Guild", value="guild")
    ])  
    async def playplaylist(self, interaction: discord.Interaction, type: app_commands.Choice[str], playlist_name: str):
        await interaction.response.defer()
        music_player = await self.ensure_voice(interaction)
        if not music_player:
            return
        try:
            if type.value == "personal":
                user_id = str(interaction.user.id)
                if user_id not in self.user_playlists or playlist_name not in self.user_playlists[user_id]:
                    await interaction.followup.send(f"You don't have a personal playlist named '{playlist_name}'.", ephemeral=True)
                    return
                playlist = self.user_playlists[user_id][playlist_name]
            else:  # guild
                guild_id = str(interaction.guild.id)
                if guild_id not in self.guild_playlists or playlist_name not in self.guild_playlists[guild_id]:
                    await interaction.followup.send(f"The guild doesn't have a playlist named '{playlist_name}'.", ephemeral=True)
                    return
                playlist = self.guild_playlists[guild_id][playlist_name]
            for song in playlist:
                music_player.add_song(song['video_id'], song['title'])
            await interaction.followup.send(f"Added {len(playlist)} song(s) from '{playlist_name}' to the queue.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to play playlist: {str(e)}", ephemeral=True)

    @app_commands.command(name="stop", description="Stop playback and disconnect the bot")
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        music_player = await self.ensure_voice(interaction)
        if not music_player:
            return
        music_player.stop()
        if music_player.voice_client:
            await music_player.voice_client.disconnect()
        await interaction.followup.send("Stopped playback and disconnected.", ephemeral=True)

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        await interaction.response.defer()
        music_player = await self.ensure_voice(interaction)
        if not music_player:
            return
        if not music_player.current_song:
            await interaction.followup.send("Nothing is playing to skip!", ephemeral=True)
            return
        music_player.skip()
        await interaction.followup.send(f"Skipped: **{music_player.current_song['title']}**", ephemeral=True)

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        await interaction.response.defer()
        music_player = await self.ensure_voice(interaction)
        if not music_player:
            return
        if not music_player.voice_client.is_playing():
            await interaction.followup.send("Nothing is playing to pause!", ephemeral=True)
            return
        music_player.pause()
        await interaction.followup.send("Paused playback.", ephemeral=True)

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        await interaction.response.defer()
        music_player = await self.ensure_voice(interaction)
        if not music_player:
            return
        if not music_player.voice_client.is_paused():
            await interaction.followup.send("Playback is not paused!", ephemeral=True)
            return
        music_player.resume()
        await interaction.followup.send("Resumed playback.", ephemeral=True)

    @app_commands.command(name="queue", description="Show the current song queue")
    async def show_queue(self, interaction: discord.Interaction):
        await interaction.response.defer()
        music_player = await self.ensure_voice(interaction)
        if not music_player:
            return
        queue = music_player.get_queue()
        if not queue and not music_player.current_song:
            await interaction.followup.send("The queue is empty!", ephemeral=True)
            return
        embed = discord.Embed(title="🎶 | Music Queue", color=discord.Colour.blurple())
        if music_player.current_song:
            current_url = f"https://www.youtube.com/watch?v={music_player.current_song['video_id']}"
            embed.add_field(
                name="▶️ | Now Playing",
                value=f"[**{music_player.current_song['title']}**]({current_url})",
                inline=False
            )
        if queue:
            queue_list = "\n".join(
                f"**{i}**. [{song['title']}](https://www.youtube.com/watch?v={song['video_id']})"
                for i, song in enumerate(queue, start=1)
            )
            embed.add_field(name="⏭️ | Up Next", value=queue_list, inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="clear", description="Clear the song queue")
    async def clear_queue(self, interaction: discord.Interaction):
        await interaction.response.defer()
        music_player = await self.ensure_voice(interaction)
        if not music_player:
            return
        music_player.clear_queue()
        await interaction.followup.send("Cleared the queue!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))