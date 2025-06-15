import os 
from bot import DiscordBot

if __name__ == '__main__':
    bot = DiscordBot()
    bot.run(os.getenv('DISCORD_TOKEN'))