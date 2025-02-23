import discord
from discord import app_commands
from discord.ext import commands
import wavelink
from config import LAVALINK_HOST, LAVALINK_PASSWORD, LAVALINK_PORT

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.node_connected = False

    async def connect_nodes(self):
        try:
            node = wavelink.Node(
                uri=f'https://{LAVALINK_HOST}:{LAVALINK_PORT}',
                password=LAVALINK_PASSWORD
            )
            await wavelink.Pool.connect(nodes=[node], client=self.bot)
            self.node_connected = True
            print("Lavalink node connected successfully!")
        except Exception as e:
            print(f"Failed to connect to Lavalink: {e}")
            self.node_connected = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.node_connected:
            await self.connect_nodes()

    async def check_voice_channel(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
            return False
        return True

    async def ensure_node(self, interaction: discord.Interaction):
        if not self.node_connected:
            await interaction.response.send_message("Lavalink node not connected yet. Please try again in a moment.", ephemeral=True)
            return False
        return True

    # Event listener for track end (per latest wavelink docs)
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player: wavelink.Player = payload.player
        if payload.reason == "finished" and not player.queue.is_empty and not player.playing:
            next_track = player.queue.get()
            await player.play(next_track)
            if player.channel:
                await player.channel.send(f"Now playing: {next_track.title}")

    @app_commands.command(name="play", description="Play a song or playlist from YouTube")
    @app_commands.describe(query="The song or playlist URL to search for")
    async def play(self, interaction: discord.Interaction, query: str):
        if not await self.check_voice_channel(interaction) or not await self.ensure_node(interaction):
            return

        await interaction.response.defer()
        
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            player.autoplay = wavelink.AutoPlayMode.enabled  # Enable autoplay

        search_result = await wavelink.Playable.search(query)
        if not search_result:
            await interaction.followup.send("No songs or playlists found!")
            return

        print(f"Search result type: {type(search_result)}")

        if isinstance(search_result, wavelink.Playlist):
            tracks = search_result.tracks
            if not player.playing:
                await player.play(tracks[0])
                await interaction.followup.send(f"Now playing: {tracks[0].title} (from playlist: {search_result.name})")
                for track in tracks[1:]:
                    player.queue.put(track)
                await interaction.followup.send(f"Added {len(tracks) - 1} songs to the queue from playlist: {search_result.name}")
            else:
                for track in tracks:
                    player.queue.put(track)
                await interaction.followup.send(f"Added {len(tracks)} songs to the queue from playlist: {search_result.name}")
        else:
            track = search_result[0] if isinstance(search_result, list) else search_result
            if not player.playing:
                await player.play(track)
                await interaction.followup.send(f"Now playing: {track.title}")
            else:
                player.queue.put(track)
                await interaction.followup.send(f"Added to queue: {track.title}")

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
        # Autoplay should handle the next track, but we add a fallback
        if not player.queue.is_empty and not player.playing:
            next_track = player.queue.get()
            await player.play(next_track)
            await interaction.response.send_message(f"Now playing: {next_track.title}")

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
        if not await self.check_voice_channel(interaction) or not await self.ensure_node(interaction):
            return

        player: wavelink.Player = interaction.guild.voice_client
        if not player or player.queue.is_empty:
            await interaction.response.send_message("Queue is empty!", ephemeral=True)
            return

        queue_list = "\n".join([f"{i+1}. {track.title}" for i, track in enumerate(player.queue)])
        await interaction.response.send_message(f"Current queue:\n{queue_list}")

    @app_commands.command(name="disconnect", description="Disconnect the bot from voice")
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