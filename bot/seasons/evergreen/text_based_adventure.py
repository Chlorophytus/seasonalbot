import logging

from discord.ext import commands

log = logging.getLogger(__name__)


class TextBasedAdventure(commands.Cog):
    """A text-based adventure game."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Pong!"""
        await ctx.send("Pong!")


def setup(bot):
    """Text-based adventure Cog load."""
    bot.add_cog(TextBasedAdventure(bot))
    log.info("TextBasedAdventure cog loaded")