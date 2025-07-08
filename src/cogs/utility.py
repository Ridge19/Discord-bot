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

    @commands.command()
    async def patchnote(self, ctx):
        """Fetches the latest commit message from the GitHub repository."""
        owner = "Ridge19"
        repo = "Discord-bot"
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("Couldn't fetch the latest commit right now.")
                    return
                data = await resp.json()
                if isinstance(data, list) and len(data) > 0:
                    commit = data[0]
                    message = commit["commit"]["message"]
                    author = commit["commit"]["author"]["name"]
                    sha = commit["sha"][:7]
                    commit_url = f"https://github.com/{owner}/{repo}/commit/{commit['sha']}"
                    await ctx.send(
                        f"**Latest Patchnote:**\n"
                        f"`{sha}` by **{author}**\n"
                        f"{message} at {commit['commit']['author']['date']}\n"
                        f"[View on GitHub]({commit_url})"
                    )
                else:
                    await ctx.send("No commits found.")

    @commands.command()
    async def feedback(self, ctx, *, feedback: str = None):
        """Sends feedback to the developer."""
        if not feedback:
            await ctx.send("Please provide some feedback.")
            return
        await ctx.send("Feedback received! Thank you for your input.")
        # Optionally, send feedback to a specific channel (replace CHANNEL_ID with your channel's ID)
        feedback_channel = self.bot.get_channel(1382393617364287638)
        if feedback_channel:
            await feedback_channel.send(f"Feedback from {ctx.author} ({ctx.author.id}): {feedback}")
            # Send feedback as a DM to the developer (replace with your user ID)
        developer_id = 325912667543961600
        developer = await self.bot.fetch_user(developer_id)
        if developer:
            try:
                await developer.send(f"Feedback from {ctx.author} ({ctx.author.id}): {feedback}")
            except Exception as e:
                await ctx.send("Could not send feedback to the developer via DM.")

async def setup(bot):
    await bot.add_cog(Utility(bot))