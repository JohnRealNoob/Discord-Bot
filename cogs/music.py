import discord
from discord.ext import commands
from discord  import app_commands
import asyncio
import yt_dlp
import urllib.parse, urllib.request, re

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.voice_clients = {}
        self.song_info_cache = {}
        self.voice_client_timeout_tasks = {}
        self.timeout_duration = 60
        self.youtube_base_url = 'https://www.youtube.com/'
        self.youtube_results_url = self.youtube_base_url + 'results?'
        self.youtube_watch_url = self.youtube_base_url + 'watch?v='
        self.yt_dl_options = {"format": "bestaudio/best"}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    async def reset_inactivity_timer(self, guild_id: int):
        #Reset the inactivity timeout timer.
        if guild_id in self.voice_client_timeout_tasks:
            self.voice_client_timeout_tasks[guild_id].cancel()

        task = asyncio.create_task(self.check_inactivity_and_disconnect(guild_id))
        self.voice_client_timeout_tasks[guild_id] = task

    async def check_inactivity_and_disconnect(self, guild_id: int):
        #Check for inactivity and disconnect the bot after the specified timeout.
        await asyncio.sleep(self.timeout_duration)

        voice_client = self.voice_clients.get(guild_id)

        if voice_client and not voice_client.channel.members:
            await voice_client.disconnect()  # Disconnect bot if no users in the voice channel
            del self.voice_client_timeout_tasks[guild_id]  # Remove the task after disconnect

    async def play(self, interaction: discord.Interaction, music: str):
        # Play audio
        player = discord.FFmpegOpusAudio(music, **self.ffmpeg_options)
        interaction.guild.voice_client.play(player, after=lambda e: self.bot.loop.create_task(self.play_next(interaction)))

    async def play_next(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id

        # Ensure queue exists and is not empty
        if guild_id not in self.queues or not self.queues[guild_id]:
            # No more songs in the queue, disconnect from voice if no one is in the channel
            voice_client = self.voice_clients.get(guild_id)
            if voice_client and not voice_client.channel.members:
                await voice_client.disconnect()  # Disconnect the bot
            return  # No more songs, do nothing

        title, link = self.queues[guild_id].pop(0)  # Get next song

        # Ensure bot is still connected to voice
        voice_client = self.voice_clients.get(guild_id)
        if not voice_client or not voice_client.is_connected():
            return  # Bot is not in voice, stop processing

        # Reset timeout timer
        await self.reset_inactivity_timer(guild_id)

        # Call play function with the new song
        await self.play(interaction=interaction, music=link)

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
                self.voice_clients[interaction.guild.id] = vc
            except Exception as e:
                print(f"Voice connection error: {e}")
                await interaction.followup.send("Failed to connect to the voice channel.", ephemeral=True)
                return

        song_url = None
        video_title = None

        # Search for YouTube video if not a direct link
        if "youtube.com" not in music and "youtu.be" not in music:
            query_string = urllib.parse.urlencode({"search_query": music})
            content = urllib.request.urlopen(self.youtube_results_url + query_string)
            search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

            if not search_results:
                await interaction.followup.send("No YouTube results found.", ephemeral=True)
                return

            music = self.youtube_watch_url + search_results[0]  # Convert search result to URL

        # Check cache or fetch video info
        if music not in self.song_info_cache:
            loop = asyncio.get_event_loop()
            try:
                data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(music, download=False))
                song_url = data['url']
                video_title = data.get("title", "Unknown title")
                
                # Cache the song info
                self.song_info_cache[music] = (video_title, song_url)
            except Exception as e:
                print(f"Error fetching YouTube video: {e}")
                await interaction.followup.send("Failed to retrieve the song.", ephemeral=True)
                return
        else:
            video_title, song_url = self.song_info_cache[music]

        # Create an embed message
        embed = discord.Embed(
            title=f"▶️ | Now Playing: {video_title}",
            description=f"Requested by {interaction.user.mention}",
            color=discord.Colour.blurple()
        )
        embed.add_field(name="🔗 Link", value=f"[Watch on YouTube]({music})", inline=False)

        if vc.is_playing():
            # Queue the song if another is playing
            if interaction.guild.id not in self.queues:
                self.queues[interaction.guild_id] = []
            self.queues[interaction.guild_id].append((video_title, song_url))
            await interaction.followup.send(f"Added **{video_title}** to the queue.")
        else:
            self.play(interaction=interaction, music=music)
            await interaction.followup.send(embed=embed)  # Correctly sends the embed

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

        # Check if queue exists and is not empty
        if guild_id not in self.queues or not self.queues[guild_id]:
            await interaction.followup.send("The queue is currently empty.", ephemeral=True)
            return

        # Create an embed to display the queue
        embed = discord.Embed(title="🎶 | Music Queue", color=discord.Colour.blurple())

        # List the songs in the queue
        queue_list = ""
        for index, url in enumerate(self.queues[guild_id], start=1):
            # Check if the song info is cached, otherwise fetch it
            title = self.song_info_cache.get(url, "Unknown Title")

            # If the title isn't cached, fetch it
            if title == "Unknown Title":
                try:
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
                    title = data.get("title", "Unknown Title")

                    # Cache the title for future use
                    self.song_info_cache[url] = title
                except Exception as e:
                    print(f"Error fetching song info: {e}")
                    title = "Unknown Title"

            queue_list += f"**{index}.** [{title}]({url})\n"

        embed.description = queue_list

        # Send the queue embed
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))