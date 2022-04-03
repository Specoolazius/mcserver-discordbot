"""
Project is under GNU GENERAL PUBLIC LICENSE 3.0

2022, created by Specoolazius
"""
import os.path

import discord
from discord.commands import slash_command

from libs import Client


class StartStop(discord.Cog):
    """< discord.Cog >

    Extension for starting and stopping the Minecraft server.
    """

    def __init__(self, bot: Client):
        self.bot = bot

    @slash_command(name='start')
    async def __execute_start(self, ctx: discord.ApplicationContext) -> None:
        await ctx.defer()
        self.bot.is_server_starting = True

        try:
            returncode = await self.bot.execute_shell('start.sh')
            self.bot.logger.info(f'Executed start.sh with exit code {returncode}')

        except Exception as e:
            self.bot.logger.error(
                f'Failed to run start.sh\n'
                f'Error: {e}'
            )
            await ctx.respond(
                f'Failed to execute start.sh\n'
                f'Check {os.path.join(self.bot.config.log_path, "discord.log")} for more detailed information'
            )

        else:
            await ctx.respond('Server is starting')

    @slash_command(name='stop')
    async def __execute_stop(self, ctx: discord.ApplicationContext) -> None:
        await ctx.defer()
        await ctx.respond('Not implemented yet')
