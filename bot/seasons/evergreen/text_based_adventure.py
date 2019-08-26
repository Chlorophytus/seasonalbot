import logging
import random

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class RecursiveDivider:
    """Naive implementation of an asynchronous recursive maze divider."""

    class Wall:
        """Internal type for walls in the subdivider."""

        def __init__(self, horizontal: bool, length: int, right_facing: bool, position: (int, int)):
            self.horizontal = horizontal
            self.length = length
            self.right_facing = right_facing
            self.x = position[0]
            self.y = position[1]

            if self.horizontal:
                if self.right_facing:
                    self.hole = random.randint(self.x + 1, self.x + self.length - 1)
                else:
                    self.hole = random.randint(self.x - self.length + 1, self.x - 1)
            else:
                if self.right_facing:
                    self.hole = random.randint(self.y + 1, self.y + self.length - 1)
                else:
                    self.hole = random.randint(self.y - self.length + 1, self.y - 1)

    def __init__(self, x: int, y: int, recursion_limit: int, maze_cb):
        self.x = x
        self.y = y
        self.complete = False
        self.maze_callback = maze_cb
        self.recursion = recursion_limit

        def determine_exteriors(wx: int, wy: int, xx: int, yy: int):
            return xx == wx or xx == 0 or yy == wy or yy == 0

        self.maze_data = [[determine_exteriors(x - 1, y - 1, xx, yy) for xx in range(x)] for yy in range(y)]

    async def start_division(self):
        """
        Seed the recursive divider, bifurcating until the maze is finished.

        This is an asynchronous and recursive call.
        """
        horizontal = random.getrandbits(1)
        seed_wall = None
        if horizontal:
            seed_wall = RecursiveDivider.Wall(True, self.x - 2, True, (1, random.randint(2, self.y - 2)))
        else:
            seed_wall = RecursiveDivider.Wall(False, self.y - 2, True, (random.randint(2, self.x - 2), 1))
        await self.branch_wall_with_hole(seed_wall)

    def bisect_wall(self, length: int, right_facing: bool, trunk):
        """
        Bisect a wall, `length` being an upper bound.

        :param length: How long to make this next wall?
        :param right_facing: Does the branch wall face the right of the trunk?
        :param trunk: Original wall to bisect.
        """
        if trunk.horizontal:
            if right_facing:
                return RecursiveDivider.Wall(not trunk.horizontal, length, right_facing,
                                             (trunk.x, trunk.y - trunk.length))
            else:
                return RecursiveDivider.Wall(not trunk.horizontal, length, right_facing,
                                             (trunk.x, trunk.y))
        else:
            if right_facing:
                return RecursiveDivider.Wall(not trunk.horizontal, length, right_facing,
                                             (trunk.x - trunk.length, trunk.y))
            else:
                return RecursiveDivider.Wall(not trunk.horizontal, length, right_facing,
                                             (trunk.x, trunk.y))

    def draw_wall(self, trunk: Wall):
        """Plot a wall on the maze"""
        if trunk.horizontal:
            if trunk.right_facing:
                for i in range(trunk.x, trunk.x + trunk.length):
                    self.maze_data[i][trunk.y] = i != trunk.hole
            else:
                for i in range(trunk.x - trunk.length, trunk.x):
                    self.maze_data[i][trunk.y] = i != trunk.hole
        else:
            if trunk.right_facing:
                for i in range(trunk.y, trunk.y + trunk.length):
                    self.maze_data[trunk.x][i] = i != trunk.hole
            else:
                for i in range(trunk.y - trunk.length, trunk.y):
                    self.maze_data[trunk.x][i] = i != trunk.hole

    async def branch_wall_with_hole(self, trunk: Wall):
        """
        Make a wall in the grid, with a random hole, then do branching calls

        :param trunk: The attributes for the wall to branch.
        """
        if self.recursion < 1:
            if not self.complete:
                self.maze_callback(self)
                self.complete = True
            return

        self.recursion -= 1

        next_walls = None
        self.draw_wall(trunk)

        partitioning_at = random.randint(0, trunk.length - 1)
        next_walls = (self.bisect_wall(partitioning_at, True, trunk),
                      self.bisect_wall(partitioning_at, False, trunk))

        await self.branch_wall_with_hole(next_walls[0])
        await self.branch_wall_with_hole(next_walls[1])


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
