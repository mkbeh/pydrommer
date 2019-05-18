# -*- coding: utf-8 -*-
import time
import asyncio


class BaseTCP:
    @staticmethod
    async def close_conn(sock):
        sock.close()
        await sock.wait_closed()

    async def check_on_open_port(self, host, port, read_timeout):
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=read_timeout
            )
        except asyncio.TimeoutError:
            return
        except ConnectionRefusedError:
            # эта ошибка вылетает когда слишком много одновременных соединений открыто
            raise
        else:
            await self.close_conn(writer)
            return host, port

    async def find_open_ports(self, host, ports, timeout=.1, read_timeout=.1):
        time.sleep(timeout)
        open_ports = await asyncio.gather(
            *(self.check_on_open_port(host, port, read_timeout) for port in ports)
        )
        print(open_ports)
