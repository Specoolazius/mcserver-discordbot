import asyncio
import os.path

import discord
from discord.commands import slash_command

from libs import ServerBot


class Executer(discord.Cog):

    def __init__(self, bot: ServerBot):
        self.bot = bot

    @slash_command(name='start')
    async def __start_server(self, ctx: discord.ApplicationContext) -> None:
        await ctx.defer()

        await asyncio.create_subprocess_exec(
            os.path.join('scripts', 'start-server.sh'),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await ctx.respond('starting server')

    @slash_command(name='stop')
    async def __stop_server(self, ctx: discord.ApplicationContext) -> None:
        if ctx.user.id not in self.bot.admin_ids:
            await ctx.respond('You don\'t have permissions to do that', ephemeral=True)
            return

        await ctx.respond('Stopping server')


def setup(bot: ServerBot):
    bot.add_cog(Executer(bot))
