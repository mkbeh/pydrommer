# -*- coding: utf-8 -*-


def count_lines(filename, chunk_size=1 << 13):
    with open(filename) as file:
        return sum(chunk.count('\n')
                   for chunk in iter(lambda: file.read(chunk_size), ''))


def truncate(num, decimals=0):
    multiplier = 10 ** decimals

    return int(
        int(num * multiplier) / multiplier
    )
