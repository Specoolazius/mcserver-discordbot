"""
Project is under GNU GENERAL PUBLIC LICENSE 3.0

2022, created by Specoolazius
"""

import asyncio
from datetime import datetime
import pprint

import discord
from discord.commands import slash_command
import mcstatus.pinger

from libs import Client


class Status(discord.Cog):
    """< discord.Cog >

    An extension to display servers status
    """

    def __init__(self, bot: Client):
        self.bot = bot
        self.mc_server = self.bot.mc_server

    @slash_command(name='info')
    async def __show_server_info(self, ctx: discord.ApplicationContext) -> None:
        print()
        """
        .add_field(
                        name='Version',
                        value="\n".join(re.split(", | ", status.version.name)),
                    )
        """

    @slash_command(name='status')
    async def __show_status(self, ctx: discord.ApplicationContext) -> None:
        print('exec')
        await ctx.defer()
        try:
            status: mcstatus.pinger.PingResponse = await self.mc_server.async_status()
            pprint.pprint(vars(status))

            query = await self.mc_server.async_query()
            pprint.pprint(vars(query))

            await ctx.respond(
                embed=discord.Embed(
                    title=f'Minecraft server status!',
                    description=f'(**{self.bot.config.server_address}** on port {self.bot.config.server_port})',
                    colour=self.bot.color,
                    timestamp=datetime.now()
                ).add_field(
                    name='Server Ping',
                    value=f'**﹂**``{round(status.latency, 2)} ms``',
                    # value=f'**⌊** **🏓 Pong!** with **``{round(status.latency, 2)}``** ms'
                ).add_field(
                    name='Players online',
                    value=f'**﹂**  ``{status.players.online} players``',
                )
            )

        except asyncio.TimeoutError or OSError:
            # ToDo: Check os Error on booting
            # ToDo: add is starting and create embed
            await ctx.respond(
                embed=discord.Embed(
                    title=f'Server offline',
                    description=f'(**{self.bot.config.server_address}** on port {self.bot.config.server_port})',
                    colour=self.bot.color,
                    timestamp=datetime.now()
                )
            )
