# -*- coding: utf-8 -*-
import aiofiles
from functools import wraps


async def write_to_file(file, blocks):
    async with aiofiles.open(file, mode='a') as f:
        for block in blocks:
            for data in block:
                await f.write('{}:{}\n'.format(*data))


def async_log(file):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            data = await func(*args, **kwargs)
            await write_to_file(file, data)

        return wrapper
    return decorator
