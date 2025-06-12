import discord
from discord.ext import commands
import os
import aiohttp
# music
from ytmusicapi import YTMusic
import yt_dlp
#github 
import requests

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# Initialize the bot with a command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Event listener for when the bot has successfully connected to Discord
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print("DISCORD_BOT_TOKEN:", os.getenv(f'DISCORD_BOT_TOKEN'))

@bot.command()
async def creator(ctx):
    """Sends the username of the creator with the given user ID."""
    creator_id = 325912667543961600
    creator_user = await bot.fetch_user(creator_id)
    if creator_user:
        message = f'Created by: {creator_user.name}'
    else:
        message = 'Creator not found.'
    await ctx.send(message)

# list audit entries (Top 5 latest)
@bot.command()
@commands.has_permissions(administrator=True)
async def audit(ctx):
    """Lists the 5 latest entries in the server's audit log."""
    entries = []
    async for entry in ctx.guild.audit_logs(limit=5):
        entries.append(f"Action: {entry.action.name}, User: {entry.user}, Target: {entry.target}, Reason: {entry.reason}")
    if entries:
        await ctx.send('\n'.join(entries))
    else:
        await ctx.send("No audit log entries found.")

# Error handling for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
        return
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
        return
    else:
        await ctx.send(f"An error occurred: {error}")

@bot.command()
async def play(ctx, *, music_name: str):
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
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '96',
        }],
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

    audio = discord.FFmpegPCMAudio(url, options="-vn")
    vc.play(discord.PCMVolumeTransformer(audio, volume=0.3))

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

    # If nothing is playing, start playing
    if not vc.is_playing() and not vc.is_paused():
        await play_next(ctx)

@bot.command()
async def skip(ctx):
    """Skips the current song and plays the next in queue."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped current track.")
        # Play the next song in the queue, if any
        await play_next(ctx)
    else:
        await ctx.send("Nothing is playing to skip.")

@bot.command()
async def stop(ctx):
    """Stops the music and makes the bot leave the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped music and left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command(aliases=['urmum'])
async def yourmum(ctx):
    """Sends a random 'yo mama' joke from yomamma-api.herokuapp.com."""
    url = "https://www.yomama-jokes.com/api/v1/jokes/random/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("Couldn't fetch a joke right now.")
                return
            data = await resp.json()
            joke = data.get("joke", "No joke found.")
            await ctx.send(joke)

@bot.command()
async def joke(ctx):
    """Sends a random joke from jokeapi.dev."""
    url = "https://v2.jokeapi.dev/joke/Any"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(f"Response status: {resp.status}")
            if resp.status != 200:
                await ctx.send("Couldn't fetch a joke right now.")
                return
            data = await resp.json()
            # JokeAPI can return either a 'single' or 'twopart' joke
            if data.get("type") == "single":
                joke = data.get("joke", "No joke found.")
            elif data.get("type") == "twopart":
                joke = f"{data.get('setup', '')}\n{data.get('delivery', '')}"
            else:
                joke = "No joke found."
            await ctx.send(joke)

@bot.command()
async def ping(ctx):
    """Returns the bot's latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency} ms")

@bot.command()
async def stats(ctx):
    """Returns the bot's statistics."""
    embed = discord.Embed(title="Bot Statistics", color=discord.Color.blue())
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)} ms", inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def restart(ctx):
    """Restarts the bot (Pterodactyl will auto-restart it)."""
    if ctx.author.id != 325912667543961600:
        await ctx.send("You do not have permission to restart the bot.")
        return
    await ctx.send("Restarting the bot...")
    await bot.close()  # This will exit the process, Pterodactyl will restart it

@bot.command()
async def intro(ctx):
    """Sends an introduction message."""
    intro_message = (
        "Hello! I'm a Discord bot created by the developer: Ridge (@riidgyy)\n"
        "I can find music, tell jokes, define words, get statistics and much more!\n"
        "I'm still a work in progress. Feedback is welcome!\n"
        "Use `!help` to see what I can do."
    )
    await ctx.send(intro_message)

@bot.command()
async def feedback(ctx, *, feedback: str = None):
    """Sends feedback to the developer."""
    if not feedback:
        await ctx.send("Please provide some feedback.")
        return
    await ctx.send("Feedback received! Thank you for your input.")
    # Optionally, send feedback to a specific channel (replace CHANNEL_ID with your channel's ID)
    feedback_channel = bot.get_channel(1382393617364287638)
    if feedback_channel:
        await feedback_channel.send(f"Feedback from {ctx.author} ({ctx.author.id}): {feedback}")
        # Send feedback as a DM to the developer (replace with your user ID)
    developer_id = 325912667543961600
    developer = await bot.fetch_user(developer_id)
    if developer:
        try:
            await developer.send(f"Feedback from {ctx.author} ({ctx.author.id}): {feedback}")
        except Exception as e:
            await ctx.send("Could not send feedback to the developer via DM.")

@bot.command()
async def patchnote(ctx):
    """Fetches the latest commit message from the GitHub repository."""
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

# Run the bot with the token
if __name__ == '__main__':
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))