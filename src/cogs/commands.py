import discord
from discord.ext import commands
import difflib

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
        elif isinstance(error, commands.CommandNotFound):
            cmd_input = ctx.message.content.lstrip('!').split()[0]
            known_commands = [cmd.name for cmd in self.bot.commands]
            suggestion = difflib.get_close_matches(cmd_input, known_commands, n=1, cutoff=0.6)
            if suggestion:
                await ctx.send(f"❓ Command `{cmd_input}` not found. Did you mean `!{suggestion[0]}`?")
            else:
                await ctx.send("Command not found. Use `!help` to see available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument. Please check the command usage.")
        else:
            await ctx.send(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))