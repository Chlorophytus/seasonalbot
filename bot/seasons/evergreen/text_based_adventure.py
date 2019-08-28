import logging
import random

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class RecursiveDivider:
    """
    Naive implementation of an asynchronous recursive maze divider.

    FIXME: I will gradually fix the recursive maze generator over the course of the next few days.
    """

    class Wall:
        """Randomly generated wall for the maze divider."""

        def __init__(self, horizontal: bool, bounds: [(int, int)]):
            """
            Make a wall definition and extrapolate values for branching.

            :param horizontal: True if horizontal.
            :param bounds: Bounding box.
                at 0: The upper left corner.
                at 1: The lower right corner.
            """
            self.horizontal = horizontal
            self.bounds = bounds

            if self.horizontal:
                self.start = (random.randint(self.bounds[0][0], self.bounds[1][0]), self.bounds[0][1])
                self.end = (self.start[0], self.bounds[1][1])
                # Horizontal, get a random X to plop a passage in
                # Remember that walls go left-to-right.
                # This means that we offset rightward. This is addition.
                self.passage = random.randint(self.start[0], self.end[0])
                # Upward is item 0, downward is item 1
                self.partitions_at = [self.randint_excluded(self.start[0], self.end[0], self.passage) for _ in
                                      range(2)]
                self.next_bounds = [
                    [self.start, (self.partitions_at[0], self.end[1])],
                    [(self.partitions_at[1], self.end[1]), self.end]
                ]
            else:
                self.start = (self.bounds[0][0], random.randint(self.bounds[0][1], self.bounds[1][1]))
                self.end = (self.bounds[1][0], self.start[1])
                # Vertical, get a random Y coordinate.
                # Remember that walls go up-to-down.
                # This means that we offset downward. This is addition.
                self.passage = random.randint(self.start[1], self.end[1])
                # Leftward is item 0, rightward is item 1
                self.partitions_at = [self.randint_excluded(self.start[1], self.end[1], self.passage) for _ in
                                      range(2)]
                self.next_bounds = [
                    [self.start, (self.end[0], self.partitions_at[0])],
                    [(self.end[0], self.partitions_at[1]), self.end]
                ]
            print(f"{self.horizontal} {self.next_bounds}")

        @staticmethod
        def randint_excluded(a: int, b: int, exclusion: int) -> int:
            """
            Random integer with an exclusion. The value returned is never the exclusion.

            :param a: Minimum.
            :param b: Maximum.
            :param exclusion: The value to not generate.
            :return: A value either between a and `exclusion - 1` or `exclusion + 1` and b.
            """
            if random.getrandbits(1):
                return random.randint(a, exclusion - 1)
            else:
                return random.randint(exclusion + 1, b)

    def __init__(self, done_callback, recursion_max: int, size: (int, int)):
        self.recursion = recursion_max
        self.size = size
        self.data = [[False] * (size[1])] * (size[0])
        self.done_callback = done_callback
        self.done = False

    @staticmethod
    def determine_orientation(dimensions: (int, int)) -> bool:
        """Determine orientation of the wall"""
        if dimensions[0] == dimensions[1]:
            return random.getrandbits(1)
        else:
            return dimensions[1] > dimensions[0]

    async def start(self):
        """Start dividing the maze."""
        horizontal = self.determine_orientation(self.size)
        await self.recurse(RecursiveDivider.Wall(horizontal, [
            (0, 0),
            self.size
        ]))

    async def recurse(self, parent: Wall):
        """Do not call this method. Recurses steps through the maze."""
        if self.recursion < 1:
            if not self.done:
                self.done = True
                self.done_callback(self)
            return
        self.recursion -= 1

        if parent.horizontal:
            for i in range(parent.start[0], parent.end[0]):
                print(f"{parent.start} {i}")
        else:
            for i in range(parent.start[1], parent.end[1]):
                print(f"{parent.start} {i}")

        await self.recurse(RecursiveDivider.Wall(not parent.horizontal, parent.next_bounds[0]))
        await self.recurse(RecursiveDivider.Wall(not parent.horizontal, parent.next_bounds[1]))


class TextBasedAdventure(commands.Cog):
    """A text-based adventure game."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Pong!"""
        await ctx.send("Pong!")

    @commands.command()
    async def embedpages(self, ctx):
        """Page embedder test"""
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

        pages = [page1, page2, page3]

        message = await ctx.send(embed=page1)

        await message.add_reaction('\u23ee')
        await message.add_reaction('\u25c0')
        await message.add_reaction('\u25b6')
        await message.add_reaction('\u23ed')

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
