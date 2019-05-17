# -*- coding: utf-8 -*-
import time
import asyncio


class BaseTCP:
    @staticmethod
    async def close_conn(sock):
        sock.close()
        await sock.wait_closed()

    async def check_on_open_port(self, host, port):
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=.1
            )
        except asyncio.TimeoutError:
            return
        except ConnectionRefusedError:
            # эта ошибка вылетает когда слишком много одновременных соединений открыто
            pass
            # raise
        else:
            await self.close_conn(writer)
            return host, port

    async def find_open_ports(self, host, ports):
        time.sleep(.1)
        open_ports = await asyncio.gather(
            *(self.check_on_open_port(host, port) for port in ports)
        )
        print(open_ports)
