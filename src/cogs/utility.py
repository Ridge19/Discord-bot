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
        await ctx.send(f"> {prev_msg.content}\n— {prev_msg.author.mention}")

class CustomHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
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
    await bot.add_cog(Utility(bot))
    bot.help_command = CustomHelp()