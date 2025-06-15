import os 
from bot import DiscordBot

if __name == '__main__':
    bot = DiscordBot()
    bot.run(os.getenv('DISCORD_TOKEN'))