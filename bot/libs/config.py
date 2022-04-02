from datetime import datetime
from configparser import ConfigParser
import re
import os
import logging

import discord

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

        self.service_name = config.get('systemd', 'service_name', fallback='mc-status-bot')

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
