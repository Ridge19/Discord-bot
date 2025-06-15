import discord
from discord.ext import commands
import os
import aiohttp
from ytmusicapi import YTMusic
import yt_dlp
import requests


class DiscordBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, *args, **kwargs)
        self.music_queues = {}

        # Register commands and events
        self.add_command(self.creator)
        self.add_command(self.audit)
        self.add_command(self.play)
        self.add_command(self.queue)
        self.add_command(self.skip)
        self.add_command(self.stop)
        self.add_command(self.yourmum)
        self.add_command(self.joke)
        self.add_command(self.ping)
        self.add_command(self.stats)
        self.add_command(self.restart)
        self.add_command(self.intro)
        self.add_command(self.feedback)
        self.add_command(self.patchnote)
        self.add_listener(self.on_ready)
        self.add_listener(self.on_command_error)

    async def on_ready(self):
        print(f'Logged in as {self.user.name} - {self.user.id}')
        print("DISCORD_BOT_TOKEN:", os.getenv(f'DISCORD_BOT_TOKEN'))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found.")
            return
        else:
            await ctx.send(f"An error occurred: {error}")

    def get_guild_queue(self, ctx):
        return self.music_queues.setdefault(ctx.guild.id, [])

<<<<<<< HEAD
    @commands.command()
    async def creator(self, ctx):
        creator_id = 325912667543961600
        creator_user = await self.fetch_user(creator_id)
        if creator_user:
            message = f'Created by: {creator_user.name}'
=======
    track = results[0]
    title = track.get("title", "Unknown")
    artists = ", ".join([a['name'] for a in track.get("artists", [])])
    video_id = track.get("videoId")
    if not video_id:
        await ctx.send("No playable link found for this track.")
        return

    url = f"https://www.youtube.com/watch?v={video_id}"
    await ctx.send(f"Playing **{title}** by **{artists}**\n{url}")

    # Stop any current audio
    if vc.is_playing():
        vc.stop()

    # Use yt_dlp to get the best audio stream
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

    # Set FFmpeg options for 48kHz PCM audio
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -ar 48000 -ac 2 -f s16le'
    }

    # Play the audio in the voice channel as 48kHz PCM
    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))

# Music queue dictionary: {guild_id: [track_dict, ...]}
music_queues = {}

def get_guild_queue(ctx):
    return music_queues.setdefault(ctx.guild.id, [])

async def play_next(ctx):
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

    # audio = discord.FFmpegPCMAudio(url, options="-vn")
    # vc.play(discord.PCMVolumeTransformer(audio, volume=0.2))
    source = discord.FFmpegOpusAudio(audio_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
    vc.play(source)

    ffmpeg_options = {
        'options': '-vn -b:a 96k'
    }

    vc = ctx.voice_client
    def after_playing(error):
        fut = discord.utils.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f"Error in after_playing: {e}")

    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=after_playing)

@bot.command()
async def queue(ctx, *, music_name: str):
    """Adds a song to the queue and plays if nothing is playing."""
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            vc = await channel.connect()
>>>>>>> parent of 8a6ae35 (- added normalisation of audio)
        else:
            message = 'Creator not found.'
        await ctx.send(message)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def audit(self, ctx):
        entries = []
        async for entry in ctx.guild.audit_logs(limit=5):
            entries.append(f"Action: {entry.action.name}, User: {entry.user}, Target: {entry.target}, Reason: {entry.reason}")
        if entries:
            await ctx.send('\n'.join(entries))
        else:
            await ctx.send("No audit log entries found.")

    @commands.command()
    async def play(self, ctx, *, music_name: str):
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

    async def play_next(self, ctx):
        queue = self.get_guild_queue(ctx)
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
            fut = discord.utils.run_coroutine_threadsafe(self.play_next(ctx), self.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error in after_playing: {e}")

        vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=after_playing)

    @commands.command()
    async def queue(self, ctx, *, music_name: str):
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
        queue = self.get_guild_queue(ctx)
        queue.append({
            "title": title,
            "artists": artists,
            "url": url
        })

        await ctx.send(f"Queued **{title}** by **{artists}**.")

        if not vc.is_playing() and not vc.is_paused():
            await self.play_next(ctx)

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped current track.")
            await self.play_next(ctx)
        else:
            await ctx.send("Nothing is playing to skip.")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Stopped music and left the voice channel.")
        else:
            await ctx.send("I'm not in a voice channel.")

    @commands.command(aliases=['urmum'])
    async def yourmum(self, ctx):
        url = "https://www.yomama-jokes.com/api/v1/jokes/random/"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("Couldn't fetch a joke right now.")
                    return
                data = await resp.json()
                joke = data.get("joke", "No joke found.")
                await ctx.send(joke)

    @commands.command()
    async def joke(self, ctx):
        url = "https://v2.jokeapi.dev/joke/Any"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"Response status: {resp.status}")
                if resp.status != 200:
                    await ctx.send("Couldn't fetch a joke right now.")
                    return
                data = await resp.json()
                if data.get("type") == "single":
                    joke = data.get("joke", "No joke found.")
                elif data.get("type") == "twopart":
                    joke = f"{data.get('setup', '')}\n{data.get('delivery', '')}"
                else:
                    joke = "No joke found."
                await ctx.send(joke)

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency} ms")

    @commands.command()
    async def stats(self, ctx):
        embed = discord.Embed(title="Bot Statistics", color=discord.Color.blue())
        embed.add_field(name="Users", value=len(self.users), inline=True)
        embed.add_field(name="Servers", value=len(self.guilds), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.latency * 1000)} ms", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def restart(self, ctx):
        if ctx.author.id != 325912667543961600:
            await ctx.send("You do not have permission to restart the bot.")
            return
        await ctx.send("Restarting the bot...")
        await self.close()

    @commands.command()
    async def intro(self, ctx):
        intro_message = (
            "Hello! I'm a Discord bot created by the developer: Ridge (@riidgyy)\n"
            "I can find music, tell jokes, define words, get statistics and much more!\n"
            "I'm still a work in progress. Feedback is welcome!\n"
            "Use `!help` to see what I can do."
        )
        await ctx.send(intro_message)

    @commands.command()
    async def feedback(self, ctx, *, feedback: str = None):
        if not feedback:
            await ctx.send("Please provide some feedback.")
            return
        await ctx.send("Feedback received! Thank you for your input.")
        # Only send feedback to the current channel
        await ctx.channel.send(f"Feedback from {ctx.author} ({ctx.author.id}): {feedback}")
        developer_id = 325912667543961600
        developer = await self.fetch_user(developer_id)
        if developer:
            try:
                await developer.send(f"Feedback from {ctx.author} ({ctx.author.id}): {feedback}")
            except Exception as e:
                await ctx.send("Could not send feedback to the developer via DM.")

    @commands.command()
    async def patchnote(self, ctx):
        owner = "Ridge19"
        repo = "Discord-bot"
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("Couldn't fetch the latest commit right now.")
                    return
                data = await resp.json()
                if isinstance(data, list) and len(data) > 0:
                    commit = data[0]
                    message = commit["commit"]["message"]
                    author = commit["commit"]["author"]["name"]
                    sha = commit["sha"][:7]
                    commit_url = f"https://github.com/{owner}/{repo}/commit/{commit['sha']}"
                    await ctx.send(
                        f"**Latest Patchnote:**\n"
                        f"`{sha}` by **{author}**\n"
                        f"{message} at {commit['commit']['author']['date']}\n"
                        f"[View on GitHub]({commit_url})"
                    )
                else:
                    await ctx.send("No commits found.")