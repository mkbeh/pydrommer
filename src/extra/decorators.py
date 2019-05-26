# -*- coding: utf-8 -*-
import aiofiles
from functools import wraps


async def async_write_to_file(file, block):
    async with aiofiles.open(file, mode='a') as f:
        for data in block:
            await f.write(data)


def async_writer(file):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            block = await func(*args, **kwargs)
            await async_write_to_file(file, block)

        return wrapper
    return decorator


def write_to_file(file, data):
    with open(file, mode='a') as f:
        f.write(data)


def writer(file):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            single_str = func(*args, **kwargs)
            write_to_file(file, single_str)

        return wrapper
    return decorator
