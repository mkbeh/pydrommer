# -*- coding: utf-8 -*-
import asyncio
import functools

from common.pluginbase import AsyncPluginBase
from common.tcpbase import TCPBase


class PortsChecker(AsyncPluginBase, TCPBase):
    def __init__(self, hosts, ports='1-65535', hosts_block_size=10,
                 ports_block_size=20, timeout=.1, read_timeout=.1):
        super().__init__(hosts, ports, hosts_block_size=hosts_block_size, ports_block_size=ports_block_size)
        self._timeout = timeout
        self._read_timeout = read_timeout

    async def scanner(self):
        await self.run_plugin(
            functools.partial(self.find_open_ports, timeout=self._timeout, read_timeout=self._read_timeout),
            require_ports=True
        )


from test_data import secret
asyncio.get_event_loop().run_until_complete(PortsChecker(secret.subnet).scanner())

