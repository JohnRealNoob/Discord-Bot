import discord
from discord import app_commands
from discord.ext import commands
import wavelink
from config import LAVALINK_HOST, LAVALINK_PASSWORD, LAVALINK_PORT

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def connect_nodes(self):
        try:
            node = wavelink.Node(
                uri=f'https://{LAVALINK_HOST}:{LAVALINK_PORT}',
                password=LAVALINK_PASSWORD
            )
            await wavelink.Pool.connect(nodes=[node], client=self.bot)
            print("Lavalink node connected successfully!")
        except Exception as e:
            print(f"Failed to connect to Lavalink: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_nodes()

    async def check_voice_channel(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
            return False
        return True

    async def ensure_node(self, interaction: discord.Interaction):
        nodes = wavelink.Pool.nodes
        if not nodes:
            await interaction.response.send_message("Lavalink node not connected yet. Please try again in a moment.", ephemeral=True)
            return False
        return True

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player: wavelink.Player = payload.player
        if payload.reason == "finished" and not player.queue.is_empty and not player.playing:
            next_track = player.queue.get()
            await player.play(next_track)
            if player.channel:
                duration = self.format_duration(next_track.length)
                await player.channel.send(
                    f"Now playing:\n**Title:** {next_track.title}\n**Link:** {next_track.uri}\n**Duration:** {duration}"
                )

    def format_duration(self, milliseconds: int) -> str:
        seconds = milliseconds // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds %= 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    @app_commands.command(name="play", description="Play a song or playlist from YouTube")
    @app_commands.describe(query="The song or playlist URL to search for")
    async def play(self, interaction: discord.Interaction, query: str):
        if not await self.check_voice_channel(interaction) or not await self.ensure_node(interaction):
            return

        await interaction.response.defer()
        
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            player.autoplay = wavelink.AutoPlayMode.enabled

        try:
            search_result = await wavelink.Playable.search(query)
        except wavelink.LavalinkLoadException:
            await interaction.followup.send("Invalid url", ephemeral=True)
            return

        if not search_result:
            await interaction.followup.send("No songs or playlists found!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎶 | Music Queue",
            description=f"Requested by {interaction.user.mention}",
            color=discord.Colour.blurple()
        )

        if isinstance(search_result, wavelink.Playlist):
            tracks = search_result.tracks
            total_length_ms = sum(track.length for track in tracks)  # Sum all track lengths in milliseconds
            total_duration = self.format_duration(total_length_ms)   # Convert to MM:SS
            first_track = tracks[0]
            duration = self.format_duration(first_track.length)
            playlist_link = query if query.startswith("http") else tracks[0].uri

            embed.add_field(
                name=f"Add Playlist",
                value=f"Added from playlist: [{search_result.name}]({playlist_link})\n**{len(tracks)} song(s)** from the playlist\nTotal Duration: {total_duration}",
                inline=False
            )

            if not player.playing:
                await player.play(first_track)
                for track in tracks[1:]:
                    player.queue.put(track)
            else:
                for track in tracks:
                    player.queue.put(track)
        else:
            track = search_result[0] if isinstance(search_result, list) else search_result
            duration = self.format_duration(track.length)
            embed.add_field(
                name=f"Add  Queue",
                value=f"**[{track.title}]({track.uri})**\nDuration: {duration}",
                inline=False
            )
            if not player.playing:
                await player.play(track)
            else:
                player.queue.put(track)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        if not await self.check_voice_channel(interaction) or not await self.ensure_node(interaction):
            return

        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.playing:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
            return

        await player.stop()
        await interaction.response.send_message("Song skipped!")
        if not player.queue.is_empty and not player.playing:
            next_track = player.queue.get()
            await player.play(next_track)
            duration = self.format_duration(next_track.length)
            await interaction.response.send_message(
                f"Now playing:\n**Title:** {next_track.title}\n**Link:** {next_track.uri}\n**Duration:** {duration}"
            )

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        if not await self.check_voice_channel(interaction) or not await self.ensure_node(interaction):
            return

        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.playing:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
            return
        if player.paused:
            await interaction.response.send_message("Music is already paused!", ephemeral=True)
            return

        await player.pause(True)
        await interaction.response.send_message("Music paused!")

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        if not await self.check_voice_channel(interaction) or not await self.ensure_node(interaction):
            return

        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.paused:
            await interaction.response.send_message("Music is not paused!", ephemeral=True)
            return

        await player.pause(False)
        await interaction.response.send_message("Music resumed!")

    @app_commands.command(name="queue", description="Show the current queue")
    async def queue(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not await self.check_voice_channel(interaction) or not await self.ensure_node(interaction):
            return

        player: wavelink.Player = interaction.guild.voice_client
        if not player or player.queue.is_empty:
            await interaction.followup.send("Queue is empty!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎶 | Music Queue",
            color=discord.Colour.blurple()
        )

        queue_list = "\n".join(
            [f"**{i+1}.** [{track.title}]({track.uri})\n" for i, track in enumerate(player.queue)]
        )
        embed.description = queue_list
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="stop", description="Disconnect the bot from voice")
    async def disconnect(self, interaction: discord.Interaction):
        if not await self.check_voice_channel(interaction) or not await self.ensure_node(interaction):
            return

        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            await interaction.response.send_message("Not connected to voice!", ephemeral=True)
            return

        await player.disconnect()
        await interaction.response.send_message("Disconnected from voice channel!")

async def setup(bot):
    await bot.add_cog(Music(bot))