# -*- coding: utf-8 -*-
import math


def count_lines(filename, chunk_size=1 << 13):
    with open(filename) as file:
        return sum(chunk.count('\n')
                   for chunk in iter(lambda: file.read(chunk_size), ''))


def truncate(num, decimals=0):
    multiplier = 10 ** decimals

    return int(
        int(num * multiplier) / multiplier
    )


# def calc_blocks_num(file, block_size):
#     lines_num = count_lines(file)
#     blocks_num = math.ceil(lines_num / block_size)
#
#     return 1 if blocks_num == 0 else truncate(blocks_num)


