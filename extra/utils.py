# -*- coding: utf-8 -*-
import operator
import itertools


def count_lines(filename, chunk_size=1 << 13):
    with open(filename) as file:
        return sum(chunk.count('\n')
                   for chunk in iter(lambda: file.read(chunk_size), ''))


def truncate(num, decimals=0):
    multiplier = 10 ** decimals

    return int(
        int(num * multiplier) / multiplier
    )


def is_range_valid(first, second):
    return operator.lt(first, second)


def range_to_int_nums(rng, check_valid=False):
    nums, nums_cp = itertools.tee(map(lambda x: int(x), rng.split('-')))

    if check_valid:
        return nums_cp, is_range_valid(*nums)

    return nums


def sub_nums_in_seq(first, second):
    return operator.sub(second, first)

