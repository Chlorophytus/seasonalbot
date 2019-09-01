import logging
import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class TextBasedAdventure(commands.Cog):
    """A text-based adventure game."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def embedpages(self, ctx):
        page1 = discord.Embed(
            title='Page 1/3',
            description='Description',
            colour=discord.Colour.orange()
        )
        page2 = discord.Embed(
            title='Page 2/3',
            description='Description',
            colour=discord.Colour.orange()
        )
        page3 = discord.Embed(
            title='Page 3/3',
            description='Description',
            colour=discord.Colour.orange()
        )
        inventory = discord.Embed(
            title='Inventory',
            description='Description',
            colour=discord.Colour.red()
        )

        # Default to None, if not none then the equipped item should show in bold
        inventory.add_field(name="Keys", value="None", inline=True)
        inventory.add_field(name="Weapons", value="None", inline=True)
        inventory.add_field(name="Power-Ups", value="None", inline=True)

        pages = [page1, page2, page3]

        message = await ctx.send(embed=page1)

        await message.add_reaction('\u23ee')
        await message.add_reaction('\u25c0')
        await message.add_reaction('\u25b6')
        await message.add_reaction('\u23ed')
        await message.add_reaction('\U0001F392')

        i = 0
        emoji = ''

        while True:
            if emoji == '\u23ee':
                i = 0
                await message.edit(embed=pages[i])
            if emoji == '\u25c0':
                if i > 0:
                    i -= 1
                    await message.edit(embed=pages[i])
            if emoji == '\u25b6':
                if i < 2:
                    i += 1
                    await message.edit(embed=pages[i])
            if emoji == '\u23ed':
                i = 2
                await message.edit(embed=pages[i])
            if emoji == '\U0001F392':
                await message.edit(embed=inventory)

            res = await ctx.bot.wait_for('reaction_add', timeout=30)
            if res is None:
                break
            if str(res[1]) != 'SeasonalBotTestBot#1418':  # Example: 'MyBot#1111'
                emoji = str(res[0].emoji)
                await message.remove_reaction(res[0].emoji, res[1])

        await message.clear_reactions()


def setup(bot):
    """Text-based adventure Cog load."""
    bot.add_cog(TextBasedAdventure(bot))
    log.info("TextBasedAdventure cog loaded")
