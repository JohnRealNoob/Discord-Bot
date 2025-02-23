import asyncio
import discord

class MusicPlayer:
    def __init__(self, guild, ydl):
        self.guild = guild
        self.ydl = ydl
        self.queue = []
        self.current_song = None
        self.voice_client = None
        self.is_playing = False
        self._lock = asyncio.Lock()

    async def add_song(self, video_id, title):
        async with self._lock:
            self.queue.append({"video_id": video_id, "title": title})
            print(f"Added to queue: {title} (ID: {video_id}), Queue length: {len(self.queue)}")
            if not self.is_playing and self.voice_client and self.voice_client.is_connected():
                print("Starting playback from add_song")
                await self.play_next_song()

    async def play_next_song(self):
        """Play the next song in the queue."""
        async with self._lock:
            if not self.queue:
                self.current_song = None
                self.is_playing = False
                if self.voice_client and self.voice_client.is_connected():
                    print("Queue empty, disconnecting")
                    await self.voice_client.disconnect()
                return

            self.current_song = self.queue.pop(0)
            self.is_playing = True
            print(f"Playing next song: {self.current_song['title']}")
            await self.play_song(self.current_song)

    async def play_song(self, song):
        """Play a song using its video ID or pre-extracted audio URL."""
        if song.get('url'):  # Use pre-extracted URL if available
            audio_url = song['url']
        else:
            video_url = f"https://www.youtube.com/watch?v={song['video_id']}"
            try:
                with self.ydl:
                    info = self.ydl.extract_info(video_url, download=False)
                    if not info or 'url' not in info:
                        raise ValueError(f"Failed to get audio for '{song['title']}'")
                    audio_url = info['url']
                print(f"Extracted audio URL for {song['title']}: {audio_url}")
            except Exception as e:
                print(f"Error extracting '{song['title']}': {e}")
                self.is_playing = False
                await asyncio.sleep(1)
                if self.queue:
                    await self.play_next_song()
                return

        try:
            source = discord.FFmpegPCMAudio(audio_url, executable="ffmpeg")
            if self.voice_client.is_playing():
                self.voice_client.stop()
            self.voice_client.play(source, after=lambda e: self._after_playback(e))
            print(f"Started playing: {song['title']}")
        except Exception as e:
            print(f"Error playing '{song['title']}': {e}")
            self.is_playing = False
            await asyncio.sleep(1)
            if self.queue:
                await self.play_next_song()

    def _after_playback(self, error):
        if error:
            print(f"Playback error: {error}")
        self.is_playing = False
        if self.voice_client and self.voice_client.is_connected():
            print("Song finished, scheduling next")
            asyncio.run_coroutine_threadsafe(self.play_next_song(), self.voice_client.loop)

    async def stop(self):
        """Stop playback and clear the queue."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        self.queue.clear()
        self.current_song = None
        self.is_playing = False

    def skip(self):
        """Skip the current song."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()

    def pause(self):
        """Pause the current song."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_playing = False

    def resume(self):
        """Resume a paused song."""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_playing = True

    def get_queue(self):
        """Return a copy of the current queue."""
        return self.queue.copy() if self.queue else []

    def clear_queue(self):
        """Clear the queue without stopping the current song."""
        self.queue.clear()