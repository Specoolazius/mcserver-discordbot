import os.path
from abc import ABC
from typing import Any

from mcstatus import JavaServer

import discord
from discord.commands import slash_command

TOKEN = ""


class ServerBot(discord.Bot, ABC):

    def __init__(self):
        super(ServerBot, self).__init__(
            # general config
            owner_id=448814943857410058,

            # starting presence
            activity=discord.Game('Beep Boop! Loading...'),
            # activity=discord.Game('with 10 people on sfs.ddnss.org'),
            status=discord.Status.idle,

            # debug
            debug_guilds=[848137923101982741, 958692739065720832],
        )

        # loading extensions
        from extensions.executer import Executer
        self.add_cog(Executer(self))
        from extensions.developer import Developer
        self.add_cog(Developer(self))

        self.admin_ids = [448814943857410058]

    def run(self, *args: Any, **kwargs: Any) -> None:
        super(ServerBot, self).run(TOKEN, *args, **kwargs)

    async def on_ready(self) -> None:
        print('online')



