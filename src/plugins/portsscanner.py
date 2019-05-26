# -*- coding: utf-8 -*-
from src.common.pluginbase import AsyncPluginBase
from src.common.tcpbase import TCPBase
from src.common.output import Output


class PortsChecker(Output, TCPBase, AsyncPluginBase):
    def __init__(self, *args, **kwargs):
        kwargs.update({'final_file': 'ports_checker'})
        super(PortsChecker, self).__init__(*args, **kwargs)

    async def run(self):
        await self.run_plugin(self.find_open_ports, require_ports=True)
        self.output(self.tmp_file)
