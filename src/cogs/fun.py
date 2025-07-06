import discord
from discord.ext import commands
import aiohttp

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

async def setup(bot):
    await bot.add_cog(Fun(bot))