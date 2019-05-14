# -*- coding: utf-8 -*-
import time
import asyncio

from extra import utils

# TODO
#   1. Рассортировать функции по классам
#   2. Решить вопрос с исключением ConnectionRefusedError
#   3. Добавить поддержку
#   - одного хоста
#   - файла с хостами
#   - диапазона хостов
#   - маску подсети
#   - диапазон портов
#   - порты из файла
#   4. Разобраться как грабить баннеры
#   5. Предварительно чекать - жив ли хост
#   6. Добавить кли интерфейс (ключи)
#   - -v режим вербализации
#   - -p порты/диапазон портов
#   - -o вывод в файл
#   7. Сделать paused.conf


PORTS_NUM = 65536
HOSTS_BLOCK_SIZE = 5          # кол-во хостов из файла
PORTS_BLOCK_SIZE = 25     # кол-во портов которые будут одновременно браться 25
TIMEOUT = 20
READ_TIMEOUT = .1


"""
ConnectionRefusedError решить как обрабатывать
"""


class PortsChecker:
    pass


async def close_conn(sock):
    sock.close()
    await sock.wait_closed()


async def check_on_open_port(host, port):
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=.1
        )
    except asyncio.TimeoutError:
        return
    except ConnectionRefusedError:
        print('PORT', port)
        raise
        # return
    else:
        await close_conn(writer)
        return host, port


async def find_open_ports(host, ports_range):
    print('ports range', ports_range)
    open_ports = await asyncio.gather(
        *(check_on_open_port(host, port) for port in range(*ports_range))
    )
    print(
        tuple(
            filter(
                lambda x: x is not None, open_ports
            )
        )
    )

    return filter(
        lambda x: x is not None, open_ports
    )


async def calc_blocks_num():
    return utils.truncate(
        PORTS_NUM / PORTS_BLOCK_SIZE
    )


async def ports_checker_handler(host):
    blocks_num = await calc_blocks_num()
    last_block_size = PORTS_NUM - blocks_num * PORTS_BLOCK_SIZE

    rpcs = []

    for i in range(0, PORTS_NUM, PORTS_BLOCK_SIZE):
        time.sleep(.1)

        if i != blocks_num * PORTS_BLOCK_SIZE:
            rpcs.extend(
                await find_open_ports(host, (i, i + PORTS_BLOCK_SIZE))
            )
            # break
            continue

        rpcs.extend(
            await find_open_ports(host, (i, i + last_block_size))
        )

    return rpcs


async def prepare_basic_data(host, block_size):
    try:
        blocks_num = utils.calc_blocks_num(host, block_size)
    except FileNotFoundError:
        return
    else:
        allowable_lines_num = blocks_num * block_size
        return allowable_lines_num


async def ports_scanner(host):
    allowable_lines_num = await prepare_basic_data(host, HOSTS_BLOCK_SIZE)

    if not isinstance(allowable_lines_num, int):
        res = await ports_checker_handler(host)
        print(res)
        # return await RPCFinder(host).test_query()

    # rpc_addrs = []
    #
    # for i in range(1, allowable_lines_num, BLOCK_SIZE):
    #     hosts = _get_block(host, i, i + BLOCK_SIZE)
    #     hosts = await asyncio.gather(
    #         *(RPCFinder(addr).test_query() for addr in hosts)
    #     )
    #
    #     rpc_addrs.extend(hosts)
    #     time.sleep(TIMEOUT)
    #
    # rpc_addrs = filter(lambda x: x is not None, rpc_addrs)
    # return (addr for addr in rpc_addrs) if genexpr else tuple(rpc_addrs)


# asyncio.run(check_on_open_port('46.160.199.52', 18332))
ioloop = asyncio.get_event_loop()
ioloop.run_until_complete(ports_scanner('46.160.199.52'))
