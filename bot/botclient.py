from abc import ABC
import asyncio
from configparser import ConfigParser
from datetime import datetime
import logging
import os
import random
import re
from typing import Any

import discord
from discord.commands import slash_command
from discord.ext import tasks
from mcstatus import JavaServer

CONFIG_PATH = 'config'


class Configs(object):
    """< object >

    This contains all configs and settings defined in config.ini and settings.ini
    """

    def __init__(self):
        self.start_time = datetime.now()
        path_list = re.split('/| \\\\', CONFIG_PATH)

        config = ConfigParser(allow_no_value=True)
        config.read(f'{os.path.join(*path_list, "") or ""}config.ini')

        self.__login_token = config.get('discord', 'token')

        self.server_address = config.get('mcserver', 'server_address')
        self.server_port = config.getint('mcserver', 'server_port', fallback=25565)

        self.admin_ids = config.get('perms', 'admin_ids')
        if self.admin_ids:
            self.admin_ids = [int(admin_id) for admin_id in self.admin_ids.split(' ')]

        self.role_ids = config.get('perms', 'role_ids')
        if self.admin_ids:
            self.role_ids = [int(admin_id) for admin_id in self.admin_ids.split(' ')]

        self.executable_commands = {
            'start': config.getboolean('perms', 'start', fallback=True),
            'stop': config.getboolean('perms', 'stop', fallback=False),
            'status': config.getboolean('perms', 'status', fallback=True),
            'dev_commands': config.getboolean('perms', 'false', fallback=False),
        }

        config.read(f'{os.path.join(*path_list, "") or ""}settings.ini')

        self.log_path = config.get('logging', 'path', fallback=os.path.join('logs', ''))
        self.log_level = config.getint('logging', 'level', fallback=logging.INFO)

        self.retry_in_seconds = config.getint('presence', 'retry_in_seconds', fallback=15)
        self.server_start_timout = config.getint('presence', 'server_start_timout', fallback=300)

        self.debug_guilds = config.get('debug', 'debug_guilds', fallback=None)
        if self.debug_guilds:
            self.debug_guilds = [int(guild_id) for guild_id in self.debug_guilds.split(' ')]

        self.intents = discord.Intents.none()
        self.mc_flags = discord.MemberCacheFlags.from_intents(self.intents)

    @property
    def auth_token(self) -> str:
        """< property >

        This ensures the authentication token can only be used once.
        After that it gets deleted for protection reasons

        :return: OAuth Token
        """

        try:
            token = self.__login_token
            del self.__login_token

        except AttributeError:
            raise Exception('OAuth token has already been used once')

        else:
            return token


class BotClient(discord.Bot, ABC):
    """< discord.Bot >

    The bot class
    """

    def __init__(self):
        self.__config = Configs()
        self.logger = self.__setup_logger(self.__config.log_level)

        super(BotClient, self).__init__(
            # default presence
            activity=discord.Game('Beep Boop! Loading...'),
            status=discord.Status.idle,

            # debug
            debug_guilds=self.config.debug_guilds,
        )

        self.mc_server = JavaServer(
            self.__config.server_address,
            self.__config.server_port
        )
        self.presence_manager = Presence(self)

    def run(self, *args: Any, **kwargs: Any) -> None:
        """< function >

        Starts the bot and automatically gets the configured token.
        """

        super(BotClient, self).run(self.__config.auth_token)

    @property
    def config(self) -> Configs:
        """< property >

        The default config should not be changeable even on runtime.
        This ensures its read-only.

        :return: Butter default config
        """

        return self.__config

    @property
    def color(self) -> int:
        """< property >

        Depending on the setting set in ButterConfig either
        the bot's default color gets returned or a random
        always bright color.

        :return: hex-Color
        """

        colors: list[int] = [0, 255, random.randint(0, 255)]
        random.shuffle(colors)

        return int('0x%02x%02x%02x' % tuple(colors), 16)

    def __setup_logger(self, level: int = logging.INFO) -> logging.Logger:
        """< function >

        Basic logging abilities
        """

        path_list = re.split('/| \\\\', self.__config.log_path)

        for i, folder in enumerate(path_list):
            # filtering empty strings (e.g. for using source folder)
            if not folder:
                continue

            try:
                # creates folders
                os.mkdir(os.path.join(*path_list[:i + 1]))

            except FileExistsError:
                continue

        logger = logging.getLogger('discord')
        logger.setLevel(level)

        formatter = logging.Formatter(fmt='[%(asctime)s] - %(levelname)s: %(name)s: %(message)s')

        file_handler = logging.FileHandler(filename=f'{os.path.join(*path_list, "") or ""}discord.log',
                                           encoding='utf-8', mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    async def on_ready(self) -> None:
        """< coroutine >

        Logs when the bot is online.
        """

        self.logger.info('Bot successfully started')


class Presence(object):
    """<object>

    A class for simply managing the bot's presence.
    """

    def __init__(self, bot: BotClient):
        self.bot = bot
        self.mc_server = self.bot.mc_server
        self.__server_online_presence.start()

        """
        await self.bot.change_presence(
            activity=self.bot.activity,
            status=self.bot.status
        )"""

    @tasks.loop()
    async def __server_online_presence(self):
        try:
            self.bot.logger.debug('Getting server information')
            status = await self.mc_server.async_status()

            await self.bot.change_presence(
                activity=discord.Game(
                    name=f'with {status.players.online} players'
                )
            )
            await asyncio.sleep(40)

            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=self.bot.config.server_address
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


class Developer(discord.Cog):
    """< discord.Cog >

    Some developer tools for managing the bot.
    """

    def __init__(self, bot: BotClient):
        self.bot = bot

    async def __permission_granter(self, *path: str) -> int:
        process = await asyncio.create_subprocess_shell(
            cmd=f'sudo chmod +x {os.path.join(os.getcwd(), *path)}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        self.bot.logger.info(f'Finished bot update with exit code {process.returncode}')
        if process.returncode:
            self.bot.logger.error(f'stderr:\n{stderr.decode()}')

        else:
            self.bot.logger.info(f'stdout:\n{stdout.decode()}')

        return process.returncode

    __dev_group = SlashCommandGroup(name='dev', description='Developer settings')

    @__dev_group.command(name='update')
    async def __update_bot(self, ctx: discord.ApplicationContext):
        response = await ctx.respond('starting update...')

        if await self.__permission_granter('scripts', 'update.sh') == 0:
            print('okay')

        else:
            await ctx.respond('Failed to update. Check the log files for further information')


class Status(discord.Cog):
    """< discord.Cog >

    An extension to display servers status
    """

    def __init__(self, bot: BotClient):
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
            await ctx.respond(embed=discord.Embed(
                title=f'Server offline',
                description=f'(**{self.bot.config.server_address}** on port {self.bot.config.server_port})',
                colour=self.bot.color,
                timestamp=datetime.now()
            )
            )


class StartStop(discord.Cog):
    """< discord.Cog >

    """


if __name__ == '__main__':
    BotClient().run()
