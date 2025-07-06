import discord
from discord.ext import commands
import aiohttp

class CustomHelp(commands.HelpCommand):
    async def help(self, mapping):
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are all my commands. Use `!help <command>` for more info.",
            color=discord.Color.blue()
        )
        for cog, commands_list in mapping.items():
            filtered = await self.filter_commands(commands_list, sort=True)
            if filtered:
                name = cog.qualified_name if cog else "No Category"
                value = "\n".join(f"`{c.name}`: {c.short_doc or 'No description'}" for c in filtered)
                embed.add_field(name=name, value=value, inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

async def setup(bot):
    bot.help_command = CustomHelp()  # Set the custom help command