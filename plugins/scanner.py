# -*- coding: utf-8 -*-
import asyncio
import functools

from common.pluginbase import AsyncPluginBase
from common.basetcp import BaseTCP


# TODO
#   2. Решить вопрос с исключением ConnectionRefusedError // N-20-5-1-stop
#   4. Разобраться как грабить баннеры
#   6. Добавить кли интерфейс (ключи)
#   - -v режим вербализации
#   - -p порты/диапазон портов
#   - -o вывод в файл
#   - -Pn: Treat all hosts as online -- skip host discovery
#   7. Сделать paused.conf
#   8. нужен какой то общий хэндлер , который в зависимости от ключей будет сам вызывать нужные методы.


class PortsChecker(AsyncPluginBase, BaseTCP):
    def __init__(self, hosts, ports='1-65535', hosts_block_size=10,
                 ports_block_size=20, timeout=.1, read_timeout=.1):
        super().__init__(hosts, ports, hosts_block_size=hosts_block_size, ports_block_size=ports_block_size)
        self._timeout = timeout
        self._read_timeout = read_timeout

    async def tcp_ping(self):
        await self.run_plugin(
            functools.partial(self.find_open_ports, timeout=self._timeout, read_timeout=self._read_timeout),
            require_ports=True
        )


from test_data import secret
asyncio.get_event_loop().run_until_complete(PortsChecker(secret.node).tcp_ping())

