import asyncio
import time

import discord
from discord.ext import tasks


class Presence(object):
    """<object>

    A class for simply managing the bot's presence.
    """

    def __init__(self, bot):
        from libs import Client
        bot: Client

        self.bot = bot
        self.mc_server = self.bot.mc_server
        self.retry_in_seconds = self.bot.config.retry_in_seconds

        self.__server_online_presence.start()

    @tasks.loop()
    async def __server_online_presence(self):
        _time = time.time()

        try:
            self.bot.logger.debug('Getting server information')
            status = await self.mc_server.async_status()

            self.bot.is_server_starting = False

            await self.bot.change_presence(
                activity=discord.Game(
                    name=f'with {status.players.online} player{"s" if status.players.online != 1 else ""}',
                ),
                status=discord.Status.online
            )

            await asyncio.sleep(40)
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=self.bot.config.server_address,
                )
            )

            await asyncio.sleep(20)

        except asyncio.TimeoutError:
            if self.bot.is_server_starting and self.bot.last_start + self.bot.config.server_start_timout < time.time():
                self.bot.is_server_starting = False

            # ToDo: better presence
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f'{self.bot.config.server_address} starting' if self.bot.is_server_starting else
                    f'offline: [self.server.address]',
                ),
                status=discord.Status.idle
            )

            # abs -> simple fix if for any reason the sleep_time is negative
            sleep_time = abs(_time - time.time() + self.retry_in_seconds)
            self.bot.logger.debug(f'Server offline, retrying in {round(sleep_time, 4)} seconds')
            await asyncio.sleep(sleep_time)

    @__server_online_presence.before_loop
    async def __before_status(self) -> None:
        """< coroutine >

        Waits until the bot has fully started in case the server
        is already online
        """

        await self.bot.wait_until_ready()
        self.bot.logger.info('presence loaded')
