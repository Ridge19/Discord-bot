import discord
from discord.ext import commands
import os
import json
from pathlib import Path
import datetime

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.STATS_FILE = Path("logs/command_stats/command_stats.json")

    def track_command_usage(self, command_name: str):
        self.STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if self.STATS_FILE.exists():
            with open(self.STATS_FILE, "r") as f:
                stats = json.load(f)
        else:
            stats = {}
        stats[command_name] = stats.get(command_name, 0) + 1
        with open(self.STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.track_command_usage(ctx.command.name)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def audit(self, ctx):
        """Lists the 5 latest entries in the server's audit log."""
        entries = []
        async for entry in ctx.guild.audit_logs(limit=5):
            entries.append(f"Action: {entry.action.name}, User: {entry.user}, Target: {entry.target}, Reason: {entry.reason}")
        if entries:
            await ctx.send('\n'.join(entries))
        else:
            await ctx.send("No audit log entries found.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def log(self, ctx, days: int = 7):
        """Logs messages from the last N days in the current channel to a txt file."""
        since = datetime.datetime.now() - datetime.timedelta(days=days)
        messages = []
        async for msg in ctx.channel.history(limit=None, after=since):
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
            messages.append(f"[{timestamp}] {msg.author.name}: {msg.content}")
        if not messages:
            await ctx.send("No messages found in the specified time range.")
            return
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)
        filename = f"{logs_dir}/chatlog_{ctx.channel.id}_{since.strftime('%Y%m%d')}_to_{datetime.datetime.utcnow().strftime('%Y%m%d')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(messages))
        await ctx.send(f"Chat log for the past {days} days saved as `{filename}`.")

async def setup(bot):
    await bot.add_cog(Admin(bot))