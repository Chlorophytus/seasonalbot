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

        def __init__(self, horizontal: bool, segment_start: (int, int), segment_end: (int, int),
                     room_start: (int, int), room_end: (int, int), lazy: bool = True):
            """
            Make a wall.

            :param horizontal: True if horizontal.
            :param segment_start: The upper left corner of the line.
            :param segment_end: The lower-right corner of the line.
            :param room_start: The upper-left corner of the room.
            :param room_end: The lower-right corner of the room.
            :param lazy: If false, a passage is automatically made.
            """
            self.horizontal = horizontal
            self.segment_start = segment_start
            self.segment_end = segment_end
            self.room_start = room_start
            self.room_end = room_end

            if self.horizontal:
                self.length = self.segment_end[0] - self.segment_start[0]
            else:
                self.length = self.segment_end[1] - self.segment_start[1]

            if not lazy:
                self.passage = self.calculate_passage()

        def calculate_passage(self) -> (int, int):
            """Calculate a passage, able to be placed into the wall."""
            return RecursiveDivider.random_position(self.segment_start, self.segment_end)

    def __init__(self, done_callback, recursion_max: int, size: int):
        self.recursion = recursion_max
        self.size = size
        self.data = [False] * (size ** 2)
        self.done_callback = done_callback
        self.done = False

    @staticmethod
    def determine_orientation(dimensions: (int, int)) -> bool:
        """Determine orientation of the wall"""
        if dimensions[0] == dimensions[1]:
            return random.getrandbits(1)
        else:
            return dimensions[1] > dimensions[0]

    @staticmethod
    def random_position(a: (int, int), b: (int, int)) -> (int, int):
        """
        Determine a random position.

        :param a: Minimum (bounding box, upper left)
        :param b: Maximum (bounding box, lower right)
        :return: A random position inside the bounding box formed by `a` and `b`.
        """
        if a[0] == b[0]:
            return a[0], random.randint(a[1], b[1])
        elif a[1] == b[1]:
            return random.randint(a[0], b[0]), a[1]
        else:
            return random.randint(a[0], b[0]), random.randint(a[1], b[1])

    def split_wall(self, parent: Wall, left_side_relative: bool):
        """
        Split the specified wall.

        :param parent: The parent wall.
        :param left_side_relative:
            If a horizontal parent:
                - split upward if true.
                - else split downward.
            If a vertical parent:
                - split leftward if true.
                - else split rightward.
        """
        passage = None
        wall = None
        if left_side_relative:
            # NOTE: The passage variable can signify the next wall's placement.
            passage = self.random_position(parent.room_start, parent.segment_end)
            if parent.horizontal:
                wall = RecursiveDivider.Wall(False, (passage[0], parent.room_start[1]),
                                             (passage[0], parent.segment_end[1]),
                                             parent.room_start, (passage[0], parent.room_end[1]))
            else:
                wall = RecursiveDivider.Wall(True, (parent.room_start[0], passage[1]),
                                             (parent.segment_end[0], passage[1]),
                                             parent.room_start, (parent.room_end[0], passage[1]))
        else:
            passage = self.random_position(parent.segment_start, parent.room_end)
            if parent.horizontal:
                wall = RecursiveDivider.Wall(False, (passage[0], parent.segment_start[1]),
                                             (passage[0], parent.room_end[1]),
                                             (passage[0], parent.room_start[1]), parent.room_end)
            else:
                wall = RecursiveDivider.Wall(True, (parent.segment_start[0], passage[1]),
                                             (parent.room_end[0], passage[1]),
                                             (parent.room_start[0], passage[1]), parent.room_end)

        wall.passage = passage
        return wall

    async def start(self):
        """Start dividing the maze."""
        horizontal = self.determine_orientation((self.size - 1, self.size - 1))
        seed_position = self.random_position((0, 0), (self.size - 1, self.size - 1))
        if horizontal:
            await self.recurse(RecursiveDivider.Wall(True, (0, seed_position[1]), (self.size - 1, seed_position[1]),
                                                     (0, 0), (self.size - 1, self.size - 1), False))
        else:
            await self.recurse(RecursiveDivider.Wall(False, (seed_position[0], 0), (seed_position[0], self.size - 1),
                                                     (0, 0), (self.size - 1, self.size - 1), False))

    async def recurse(self, parent: Wall):
        """Recursively divides the maze."""
        if self.recursion < 1:
            if not self.done:
                self.done = True
                self.done_callback(self)
            return
        self.recursion -= 1

        walls = [
            self.split_wall(parent, True),
            self.split_wall(parent, False)
        ]

        if parent.horizontal:
            for i in range(parent.segment_start[0], parent.segment_end[0] + 1):
                self.data[parent.segment_start[1] * self.size + i] = i != parent.passage[0]
        else:
            for i in range(parent.segment_start[1], parent.segment_end[1] + 1):
                self.data[i * self.size + parent.segment_start[0]] = i != parent.passage[1]

        for wall in walls:
            await self.recurse(wall)


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
