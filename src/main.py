import os 
from bot import DiscordBot
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    bot = DiscordBot()
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))