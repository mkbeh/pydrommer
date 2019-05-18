# -*- coding: utf-8 -*-
import functools

from common.pluginbase import AsyncPluginBase
from common.tcpbase import TCPBase
from common.output import Output


class PortsChecker(AsyncPluginBase, TCPBase, Output):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timeout = kwargs.get('timeout')
        self._read_timeout = kwargs.get('read_timeout')
        self._output_to = kwargs.get('output_to')

    async def scanner(self):
        await self.run_plugin(
            functools.partial(self.find_open_ports, timeout=self._timeout, read_timeout=self._read_timeout),
            require_ports=True
        )
        self.output(self._output_to, self.tmp_file)
