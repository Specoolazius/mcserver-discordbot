"""
Project is under GNU GENERAL PUBLIC LICENSE 3.0

2022, created by Specoolazius
"""

import asyncio
import os

import discord
from discord.commands import SlashCommandGroup

from libs import Client


class Admin(discord.Cog):
    """< discord.Cog >

    Some developer tools for managing the bot.
    """

    def __init__(self, bot: Client):
        self.bot = bot

    __dev_group = SlashCommandGroup(name='dev', description='Developer settings')

    @__dev_group.command(name='update')
    async def __update_bot(self, ctx: discord.ApplicationContext) -> None:
        await ctx.defer()

        if 0 == await self.bot.execute_shell('update.sh'):
            await ctx.respond('Updated bot from https://github.com/Specoolazius/mcserver-discordbot\n'
                              'You may need to restart the bot')

        else:
            await ctx.respond(f'Failed to update bot. Check {os.path.join(self.bot.config.log_path, "discord.log")} '
                              f'for more detailed information')

    @__dev_group.command(name='restart')
    async def __restart_service(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond('attempting restart...')
        self.bot.logger.info('Restarting bot...')

        process = await asyncio.create_subprocess_shell(cmd=f'sudo systemctl restart {self.bot.config.service_name}')
        # await process.communicate()

