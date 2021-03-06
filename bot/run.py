"""
Project is under GNU GENERAL PUBLIC LICENSE 3.0

2022, created by Specoolazius
"""

import sys
from aiohttp import ClientConnectorError

from libs import Client


if __name__ == '__main__':
    try:
        Client().run()

    except ClientConnectorError as e:
        sys.exit(-59)

    sys.exit(0)
