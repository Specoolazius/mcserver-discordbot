import discord

from libs import ServerBot


class Developer(discord.Cog):

    def __init__(self, bot: ServerBot):
        self.bot = bot




def setup(bot: ServerBot):
    bot.add_cog(Developer(bot))