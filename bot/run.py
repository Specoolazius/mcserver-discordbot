import sys
from aiohttp import ClientConnectorError

from libs.bot import ServerBot


if __name__ == '__main__':
    bot = ServerBot()

    try:
        bot.run()

    except ClientConnectorError as e:
        sys.exit(-59)

    sys.exit(0)
