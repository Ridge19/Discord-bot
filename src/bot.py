import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print("DISCORD_BOT_TOKEN:", os.getenv('DISCORD_BOT_TOKEN'))

# Load all cogs
initial_extensions = [
    'cogs.admin',
    'cogs.music',
    'cogs.fun',
    'cogs.utility',
    'cogs.stats'
]

async def main():
    for ext in initial_extensions:
        await bot.load_extension(ext)
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())