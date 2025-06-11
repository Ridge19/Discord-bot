import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

# music
from ytmusicapi import YTMusic
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# Initialize the bot with a command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Event listener for when the bot has successfully connected to Discord
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

@bot.command()
async def creator(ctx):
    print(f'Created by: {discord.utils.get(bot.get_all_members(), id=325912667543961600).name}')  # Replace with actual creator ID
    message = f'Created by: {discord.utils.get(bot.get_all_members(), id=325912667543961600).name}'
    await ctx.send(message)

# Example command that the bot can respond to
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

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
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
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

    # Use yt_dlp to get the audio stream
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': False,
        'noplaylist': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    # Play the audio in the voice channel
    vc.play(discord.FFmpegPCMAudio(audio_url))

@bot.command()
async def stop(ctx):
    """Stops the music and makes the bot leave the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped music and left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

# Run the bot with the token
if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN not found in .env file.")
    bot.run(TOKEN)