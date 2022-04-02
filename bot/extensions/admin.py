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
        await ctx.respond('starting update...')

        if 0 == await self.bot.execute_shell('update.sh'):
            await ctx.respond('Updated bot from https://github.com/Specoolazius/mcserver-discordbot\n'
                              'You may need to restart the bot')

        else:
            await ctx.respond(f'Failed to update bot. Check {os.path.join(self.bot.config.log_path, "discord.log")} '
                              f'for more detailed information')

    @__dev_group.command(name='restart')
    async def __restart_service(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond('attempting restart...')
        await asyncio.create_subprocess_shell(f'sudo systemctl restart')
