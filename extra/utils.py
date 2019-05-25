# -*- coding: utf-8 -*-
import os
import operator
import itertools
import tempfile


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
    return operator.sub(second, first) + 1


def clear_string(s):
    return s.strip(' \n')


def get_integers_from_str(str_, separator):
    return map(lambda x: int(x), str_.split(separator))


def split_str_by_separator(str_, separator):
    return str_.split(separator)


def get_abs_path(path_to):
    return os.path.abspath(path_to)


def get_path_to_services_file(path_to):
    path = get_abs_path(path_to)
    return path.replace('plugins/', 'common/')


def create_tmp_file(prefix='', suffix=''):
    return tempfile.mkstemp(prefix=prefix, suffix=suffix)[1]


def make_work_dir(dir_name):
    path = os.path.join(
        os.getenv('XDG_DATA_HOME', os.path.expanduser("~/.local/share")), dir_name
    )

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def get_file_path(dir_name, file_name):
    work_dir = make_work_dir(dir_name)

    return os.path.join(
        work_dir, file_name
    )


def remove_file(file):
    os.remove(file)
