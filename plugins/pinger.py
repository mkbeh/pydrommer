# -*- coding: utf-8 -*-
import asyncio

from common.pluginbase import AsyncPluginBase
from common.basetcp import BaseTCP


class ICMPPing:
    def __init__(self):
        pass


class TCPPing(AsyncPluginBase, BaseTCP):
    def __init__(self, hosts, ports='pydrommer-services.lst', hosts_block_size=10, ports_block_size=20):
        super().__init__(hosts, ports, hosts_block_size=hosts_block_size, ports_block_size=ports_block_size)

    async def tcp_ping(self):
        await self.run_plugin(self.find_open_ports, require_ports=True)


asyncio.get_event_loop().run_until_complete(TCPPing('192.0.2.16/28').tcp_ping())

