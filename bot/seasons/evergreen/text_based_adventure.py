import logging
import random

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


def determine_hole_singularity(hmin: int, hmax: int) -> int:
    """
    If a hole is at an obvious singularity, pick the spot between the min and the max.

    Otherwise, we pick a spot randomly.
    """
    if hmax - hmin > 3:
        return random.randint(hmin + 1, hmax - 1)
    else:
        return hmin + 1


class RecursiveDivider:
    """Naive implementation of an asynchronous recursive maze divider."""

    def __init__(self, x: int, y: int, maze_cb):
        self.x = x
        self.y = y
        self.complete = False
        self.maze_callback = maze_cb

        def determine_exteriors(wx: int, wy: int, xx: int, yy: int):
            return xx == wx or xx == 0 or yy == wy or yy == 0

        self.maze_data = [[determine_exteriors(x - 1, y - 1, xx, yy) for xx in range(x)] for yy in range(y)]

    async def start_division(self):
        """
        Seed the recursive divider, bifurcating until the maze is finished.

        This is an asynchronous and recursive call.
        """
        branch_horizontal = random.getrandbits(1)

        w = self.y if branch_horizontal else self.x
        wall_at = random.randint(2, w - 2)
        holes_at = (determine_hole_singularity(1, wall_at - 1), determine_hole_singularity(wall_at + 1, w - 1))

        for i in range(self.x if branch_horizontal else self.y):
            if branch_horizontal:
                self.maze_data[i][wall_at] = i != holes_at[0] or i != holes_at[1]
            else:
                self.maze_data[wall_at][i] = i != holes_at[0] or i != holes_at[1]

        if branch_horizontal:
            await self.branch_and_divide(0, wall_at - 1, w - wall_at + 1, True)
        else:
            await self.branch_and_divide(wall_at, 0, w - wall_at + 1, False)

    async def branch_and_divide(self, x: int, y: int, delta: int, branch_horizontal: bool):
        """
        Branch, then divide a section of the maze.

        Call `start_division` instead when in a production environment.
        """
        w = x if branch_horizontal else y

        if w + delta - 2 < 3:
            if not self.complete:
                self.complete = True
                self.maze_callback(self)
            return

        # Minima and maxima for the main parts of the walls
        wall_bounds = (w + 2, w + delta - 2)

        # Split.
        wall_split_at = random.randint(wall_bounds[0] + 1, wall_bounds[1] - 1)
        next_walls_at = (random.randint(wall_bounds[0], wall_split_at - 1), random.randint(wall_split_at + 1,
                                                                                           wall_bounds[1]))

        holes_at = (determine_hole_singularity(next_walls_at[0], wall_split_at),
                    determine_hole_singularity(wall_split_at, next_walls_at[1]))

        for i in range(wall_bounds[0], wall_split_at - 1):
            if branch_horizontal:
                self.maze_data[i][y] = i != holes_at[0]
            else:
                self.maze_data[x][i] = i != holes_at[0]

        for i in range(wall_split_at + 1, wall_bounds[1]):
            if branch_horizontal:
                self.maze_data[i][y] = i != holes_at[1]
            else:
                self.maze_data[x][i] = i != holes_at[1]

        if branch_horizontal:
            await self.branch_and_divide(next_walls_at[0], y, wall_split_at - next_walls_at[0], False)
            await self.branch_and_divide(wall_split_at, y, next_walls_at[1] - wall_split_at, False)
        else:
            await self.branch_and_divide(x, next_walls_at[0], wall_split_at - next_walls_at[0], True)
            await self.branch_and_divide(x, wall_split_at, next_walls_at[1] - wall_split_at, True)


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
