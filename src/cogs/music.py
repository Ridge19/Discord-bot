import discord
from discord.ext import commands
from ytmusicapi import YTMusic
import yt_dlp

music_queues = {}

def get_guild_queue(ctx):
    return music_queues.setdefault(ctx.guild.id, [])

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # play song 
    @commands.command()
    async def play(self, ctx, *, music_name: str):
        """Searches YouTube Music and plays the first result's audio in your voice channel."""
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                vc = await channel.connect()
            else:
                vc = ctx.voice_client
        else:
            await ctx.send("You must be in a voice channel to use this command.")
            return

        ytmusic = YTMusic()
        results = ytmusic.search(music_name, filter="songs")
        if not results:
            await ctx.send("No results found for your search.")
            return

        track = results[0]
        title = track.get("title", "Unknown")
        artists = ", ".join([a['name'] for a in track.get("artists", [])])
        video_id = track.get("videoId")
        if not video_id:
            await ctx.send("No playable link found for this track.")
            return

        url = f"https://www.youtube.com/watch?v={video_id}"
        await ctx.send(f"Playing **{title}** by **{artists}**\n{url}")

        if vc.is_playing():
            vc.stop()

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch',
            'extract_flat': 'in_playlist',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -ar 48000 -ac 2 -f s16le -af "dynaudnorm=f=200:g=15"'
        }
        vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))

    # skip current song 
    @commands.command()
    async def skip(self, ctx):
        """Skips the currently playing track."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped the current track.")
        else:
            await ctx.send("Nothing is playing to skip.")

    # stop current song and disconnect from voice channel
    @commands.command()
    async def stop(self, ctx):
        """Stops the music and disconnects from the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Stopped music and left the voice channel.")
        else:
            await ctx.send("I'm not in a voice channel.")

    # add song to queue and play if nothing is playing
    @commands.command()
    async def queue(self, ctx, *, music_name: str):
        """Adds a song to the queue and plays it if nothing is playing."""
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                vc = await channel.connect()
            else:
                vc = ctx.voice_client
        else:
            await ctx.send("You must be in a voice channel to use this command.")
            return

        ytmusic = YTMusic()
        results = ytmusic.search(music_name, filter="songs")
        if not results:
            await ctx.send("No results found for your search.")
            return

        track = results[0]
        title = track.get("title", "Unknown")
        artists = ", ".join([a['name'] for a in track.get("artists", [])])
        video_id = track.get("videoId")
        if not video_id:
            await ctx.send("No playable link found for this track.")
            return

        url = f"https://www.youtube.com/watch?v={video_id}"
        queue = get_guild_queue(ctx)
        queue.append({
            "title": title,
            "artists": artists,
            "url": url
        })

        await ctx.send(f"Queued **{title}** by **{artists}**.")

        # If nothing is playing, start playing the next song in the queue
        if not vc.is_playing() and not vc.is_paused():
            await self.play_next(ctx)

    # skip the next song in the queue
    @commands.command()
    async def play_next(self, ctx):
        queue = get_guild_queue(ctx)
        if not queue:
            await ctx.send("Queue is empty. Leaving the voice channel.")
            await ctx.voice_client.disconnect()
            return

        track = queue.pop(0)
        title = track.get("title", "Unknown")
        artists = track.get("artists", "Unknown")
        url = track.get("url")

        await ctx.send(f"Now playing **{title}** by **{artists}**\n{url}")

        ydl_opts = {
            'format': 'bestaudio[abr>=96]/bestaudio/best',
            'quiet': True,
            'extract_flat': False,
            'noplaylist': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -ar 48000 -ac 2 -f s16le -af "dynaudnorm=f=200:g=15"'
        }

        vc = ctx.voice_client
        def after_playing(error):
            fut = discord.utils.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error in after_playing: {e}")

        vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=after_playing)

async def setup(bot):
    await bot.add_cog(Music(bot))