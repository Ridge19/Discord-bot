import difflib
import discord
from discord.ext import commands
import aiohttp

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def define(self, ctx, *, word: str = None):
        """Looks up the definition of a word using dictionaryapi.dev."""
        if not word:
            await ctx.send("Please provide a word to define. Usage: `!define <word>`")
            return

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send(f"Could not find a definition for '{word}'.")
                    return
                data = await resp.json()
                try:
                    entry = data[0]
                    word_text = entry.get("word", word)
                    phonetic = entry.get("phonetic", "")
                    meanings = entry.get("meanings", [])
                    if not meanings:
                        await ctx.send(f"No definitions found for '{word_text}'.")
                        return
                    part_of_speech = meanings[0].get("partOfSpeech", "")
                    definitions = meanings[0].get("definitions", [])
                    definition = definitions[0].get("definition", "No definition found.") if definitions else "No definition found."
                    example = definitions[0].get("example", None) if definitions else None

                    msg = f"**{word_text}** {phonetic}\n*{part_of_speech}*\n**Definition:** {definition}"
                    if example:
                        msg += f"\n*Example:* {example}"
                    await ctx.send(msg)
                except Exception:
                    await ctx.send(f"Could not parse the definition for '{word}'.")

    @commands.command()
    async def quote(self, ctx, *, text: str = None):
        """Quotes the previous message sent by a user in the chat if no text is provided."""
        if text:
            await ctx.send(f"> {text}\n— {ctx.author.mention}")
            return

        messages = []
        async for msg in ctx.channel.history(limit=2):
            messages.append(msg)
        if len(messages) < 2:
            await ctx.send("No previous message found to quote.")
            return

        prev_msg = messages[1]
        await ctx.send(f"> {prev_msg.content}\n— {prev_msg.author.mention}, {prev_msg.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    @commands.command()
    async def restart(self, ctx):
        """Restarts the bot (Pterodactyl will auto-restart it)."""
        if ctx.author.id != 325912667543961600:
            await ctx.send("You do not have permission to restart the bot.")
            return
        await ctx.send("Restarting the bot...")
        await self.bot.close()  # This will exit the process, Pterodactyl will restart it
    
    @commands.command()
    async def user(self, ctx, member: discord.Member = None):
        """Displays user info."""
        member = member or ctx.author
        embed = discord.Embed(title=f"{member}", color=member.color)
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Mention", value=member.mention)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Top Role", value=member.top_role.name)
        embed.add_field(name="Status", value=str(member.status).title())
        await ctx.send(embed=embed)

    # detect and correct common command errors
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return
        elif isinstance(error, commands.CommandNotFound):
            # Smart suggestion using difflib
            cmd_input = ctx.message.content.lstrip('!').split()[0]
            known_commands = [cmd.name for cmd in self.bot.commands]
            suggestion = difflib.get_close_matches(cmd_input, known_commands, n=1, cutoff=0.6)

            if suggestion:
                await ctx.send(f"❓ Command `{cmd_input}` not found. Did you mean `!{suggestion[0]}`?")
            else:
                await ctx.send("Command not found. Use `!help` to see available commands.")
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument. Please check the command usage.")
            return
        else:
            await ctx.send(f"An error occurred: {error}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await self.on_command_error(ctx, error)

async def setup(bot):
    await bot.add_cog(Utility(bot))