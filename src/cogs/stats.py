import discord
from discord.ext import commands
import json
from pathlib import Path

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.STATS_FILE = Path("logs/command_stats/command_stats.json")

    @commands.command()
    async def popular(self, ctx, top: int = 3):
        """Shows the most commonly used commands."""
        if self.STATS_FILE.exists():
            with open(self.STATS_FILE, "r") as f:
                stats = json.load(f)
        else:
            await ctx.send("No command usage data yet.")
            return

        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        message = "**Most Used Commands:**\n"
        for i, (cmd, count) in enumerate(sorted_stats[:top], 1):
            message += f"{i}. `{cmd}` used {count} times\n"

        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Stats(bot))