# -*- coding: utf-8 -*-
import asyncio

from common.pluginbase import AsyncPluginBase
from common.basetcp import BaseTCP
from extra import utils

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


PORTS_NUM = 65535
HOSTS_BLOCK_SIZE = 5          # кол-во хостов из файла
PORTS_BLOCK_SIZE = 25         # кол-во портов которые будут одновременно браться 25
TIMEOUT = 20
READ_TIMEOUT = .1


class PortsChecker(AsyncPluginBase, BaseTCP):
    def __init__(self, hosts, ports='pydrommer-services.lst', hosts_block_size=10, ports_block_size=20):
        super().__init__(hosts, ports, hosts_block_size=hosts_block_size, ports_block_size=ports_block_size)

    async def tcp_ping(self):
        await self.run_plugin(self.find_open_ports, require_ports=True)


# 192.0.2.16/28
asyncio.get_event_loop().run_until_complete(PortsChecker('').tcp_ping())

