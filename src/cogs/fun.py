import discord
from discord.ext import commands
import aiohttp
import random 

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['urmum'])
    async def yourmum(self, ctx):
        """gets a random 'yo mama' joke from yomama-jokes.com API."""
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
        """gets a random joke from jokeapi.dev API."""
        url = "https://v2.jokeapi.dev/joke/Any"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
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
    async def rps(self, ctx, choice: str = None):
        """Play Rock, Paper, Scissors with the bot."""
        valid_choices = ['rock', 'paper', 'scissors']

        if choice is None:
            await ctx.send("Please choose either Rock, Paper or Scissors to play.")
            return

        user_choice = choice.lower()
        if user_choice not in valid_choices:
            await ctx.send("Invalid choice! Please choose either Rock, Paper or Scissors.")
            return
        
        bot_choice = random.choice(valid_choices).lower()
        result = None
        if user_choice == bot_choice:
            result = f"Its a tie! bot picked {bot_choice}"
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
                (user_choice == 'paper' and bot_choice == 'rock') or \
                (user_choice == 'scissors' and bot_choice == 'paper'):
            result = f"You win! Bot picked {bot_choice}."
        else:
            result = f"You lose! Bot picked {bot_choice}."

        await ctx.send(result)


async def setup(bot):
    await bot.add_cog(Fun(bot))