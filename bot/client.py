from datetime import datetime
import logging
import os
from configparser import ConfigParser
from abc import ABC
import re
import random
from typing import Any

import discord
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


class Client(discord.Bot, ABC):
    """< discord.Bot >

    The bot class
    """

    def __init__(self):
        self.__config = Configs()
        self.logger = self.__setup_logger(self.__config.log_level)

        super(Client, self).__init__(
            # starting presence
            activity=discord.Game('Beep Boop! Loading...'),
            status=discord.Status.idle,
        )

        self.mc_server = JavaServer(
            self.__config.server_address,
            self.__config.server_port
        )

    def run(self, *args: Any, **kwargs: Any) -> None:
        """< function >

        Starts the bot and automatically gets the configured token.
        """

        super(Client, self).run(self.__config.auth_token)

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

        handler = logging.FileHandler(filename=f'{os.path.join(*path_list, "") or ""}discord.log', encoding='utf-8',
                                      mode='w')
        handler.setFormatter(logging.Formatter(fmt='[%(asctime)s] - %(levelname)s: %(name)s: %(message)s'))

        logger.addHandler(handler)
        return logger





if __name__ == '__main__':
    Client().run()
