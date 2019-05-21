# -*- coding: utf-8 -*-
import time
import asyncio

from extra import utils, decorators


class TCPBase:
    tmp_file = utils.create_tmp_file(prefix='pydrommer_')

    def __init__(self, *args, **kwargs):
        super(TCPBase, self).__init__(*args, **kwargs)
        self._timeout = kwargs.get('timeout', .1)
        self._read_timeout = kwargs.get('read_timeout', .1)

    @staticmethod
    async def close_conn(sock):
        sock.close()
        await sock.wait_closed()

    async def check_on_open_port(self, host, port):
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=self._read_timeout
            )
        except asyncio.TimeoutError:
            return
        except ConnectionRefusedError:
            # эта ошибка вылетает когда слишком много одновременных соединений открыто
            raise
        else:
            await self.close_conn(writer)
            return host, port

    @decorators.async_writer(tmp_file)
    async def find_open_ports(self, host, ports):
        time.sleep(self._timeout)
        open_ports = await asyncio.gather(
            *(self.check_on_open_port(host, port) for port in ports)
        )

        return filter(lambda x: isinstance(x, tuple), open_ports)
