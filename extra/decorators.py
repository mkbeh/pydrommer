# -*- coding: utf-8 -*-
import aiofiles
from functools import wraps


async def write_to_file(file, block):
    async with aiofiles.open(file, mode='a') as f:
        for data in block:
            await f.write('{}:{}\n'.format(*data))


def async_log(file):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            block = await func(*args, **kwargs)
            await write_to_file(file, block)

        return wrapper
    return decorator
