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

    # Add queue, skip, stop, etc. here as in your original code

async def setup(bot):
    await bot.add_cog(Music(bot))