"""
Project is under GNU GENERAL PUBLIC LICENSE 3.0

2022, created by Specoolazius
"""

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
        returncode = None
