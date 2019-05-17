# -*- coding: utf-8 -*-
import asyncio
from common.pluginbase import AsyncPluginBase
"""
2 вида пинга:
1) через утилиту ping
2) через сканирование дефолтных портов

"""


class PingICMP:
    def __init__(self):
        pass


class PingTCP(AsyncPluginBase):
    def __init__(self, hosts, ports='1-65535', hosts_block_size=10, ports_block_size=20):
        super().__init__(hosts, ports, hosts_block_size=hosts_block_size, ports_block_size=ports_block_size)

    async def test(self):
        print(self.data_types)
        print(self.num_blocks)


asyncio.get_event_loop().run_until_complete(PingTCP('192.0.2.16/28', '20,21,22,23,30-35').test())

