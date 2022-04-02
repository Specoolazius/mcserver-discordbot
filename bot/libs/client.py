"""
Project is under GNU GENERAL PUBLIC LICENSE 3.0

2022, created by Specoolazius
"""

from abc import ABC
import asyncio
from typing import Any
import re
import os
import random
import time
import logging

import discord
from mcstatus import JavaServer

from libs import Configs, Presence

SHELL_SCRIPT_PATH = 'scripts'


class Client(discord.Bot, ABC):
    """< discord.Bot >

    The bot class
    """

    def __init__(self):
        self.__config = Configs()
        self.logger = self.__setup_logger(self.__config.log_level)

        super(Client, self).__init__(
            # default presence
            activity=discord.Game('Beep Boop! Loading...'),
            status=discord.Status.idle,

            # debug
            debug_guilds=self.config.debug_guilds,
        )

        self.is_server_starting = False
        self.last_start = time.time()

        self.mc_server = JavaServer(
            self.__config.server_address,
            self.__config.server_port
        )
        self.presence_manager = Presence(self)

        # extensions
        from extensions import Admin, StartStop, Status

        for module in [Admin, StartStop, Status]:
            self.add_cog(module(self))

    def run(self, *args: Any, **kwargs: Any) -> None:
        """< function >

        Starts the bot and automatically gets the configured token.
        """

        super(Client, self).run(self.__config.auth_token)

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

    async def execute_shell(self, file_name: str, retry=True) -> int:
        """< coroutine >

        Runs a bash script in executer and returns the process code.
        Logs errors if process returncode isn't 0.

        :param file_name: file name
        :param retry: recursion stopper in case granting permissions fails.
        :return: process returncode
        """

        async def __grant_permission() -> int:
            self.logger.info(f'Granting permissions to {file_name}...')

            process_chmod = await asyncio.create_subprocess_shell(
                cmd=f'chmod +x {os.path.join(os.getcwd(), SHELL_SCRIPT_PATH, file_name)}'
            )

            await process_chmod.communicate()
            return process_chmod.returncode

        process = await asyncio.create_subprocess_exec(
            program=os.path.join(os.getcwd(), SHELL_SCRIPT_PATH, file_name),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        self.logger.info(f'Executed script {file_name} with exit code {process.returncode}')

        if process.returncode == 0:
            self.logger.info(f'stdout:\n{stdout.decode()}')

        # bash returncode 126: permission error
        elif process.returncode == 126 and retry:
            # retrying once
            self.logger.warning(f'Missing permissions for {file_name}')
            return await self.execute_shell(file_name, retry=False)

        else:
            self.logger.error(f'stderr:\n{stderr.decode()}')

        return process.returncode
