# -*- coding: utf-8 -*-
import os
import re
import math

from dataclasses import dataclass, field

from netaddr import IPNetwork

from extra import utils
from extra import exceptions


@dataclass(repr=False, eq=False)
class _ArgValueTypeDefiner:
    _hosts: str
    _ports: str = '1-65535'

    _hosts_type_definers: dict = field(init=False)
    _ports_type_definers: dict = field(init=False)

    def __post_init__(self):
        self._hosts_type_definers = {
            'file': self._is_file,
            'single': self._is_single,
            'subnet': self._is_subnet
        }
        self._ports_type_definers = {
            'range': self._is_range,
            'separated': self._is_separated,
            'combined': self._is_combined,
            'file': self._is_file,
            'single': self._is_single,
        }

    @staticmethod
    def _define_data(name, seq, data):
        for arg_type, func in seq.items():
            if func(data):
                return {'name': name, 'type': arg_type, 'data': data}

    @staticmethod
    def _is_str_match(pattern, s):
        try:
            re.match(pattern, s).group()
        except AttributeError:
            return False
        else:
            return True

    @staticmethod
    def _is_file(val):
        return os.path.isfile(val)

    def _is_range(self, val):
        pattern = re.compile(r'^\d+-\d+$')
        return self._is_str_match(pattern, val)

    def _is_separated(self, val):
        pattern = re.compile(r'^\d+,(\d+,?)+$')
        return self._is_str_match(pattern, val)

    def _is_combined(self, val):
        pattern = re.compile(r'^\d+|(d+-\d+),(\d+|(d+-\d+),?)+$')
        return self._is_str_match(pattern, val)

    def _is_single(self, val):
        host_pattern = re.compile(r'^\d+.\d+.\d+.\d+$')
        port_pattern = re.compile(r'^\d+$')
        return self._is_str_match(host_pattern, val) or self._is_str_match(port_pattern, val)

    def _is_subnet(self, val):
        pattern = re.compile(r'^\d+.\d+.\d+.\d+/\d{1,2}$')
        return self._is_str_match(pattern, val)

    @property
    def data_types(self):
        hosts_type = self._define_data('hosts', self._hosts_type_definers, self._hosts)
        ports_type = self._define_data('ports', self._ports_type_definers, self._ports)

        return hosts_type, ports_type


@dataclass(repr=False, eq=False, init=False)
class BlocksCalculator:
    def __init__(self, *args, hosts_block_size=3, ports_block_size=2):
        self._hosts_block_size = hosts_block_size
        self._ports_block_size = ports_block_size
        self._definer = _ArgValueTypeDefiner(*args)

        self._blocks_calculators = {
            'single': self._calc_single_block_num,
            'file': self._calc_file_blocks_num,
            'subnet': self._calc_subnet_blocks_num,

            'range': self._calc_range_blocks_num,
            'separated': self._calc_separated_blocks_num,
            'combined': self._calc_combined_blocks_num
        }

    def _calc_blocks(self, name, num):
        block_size = self.__dict__.get(name + '_block_size')
        blocks_num = math.ceil(num / block_size)

        return 1 if blocks_num == 0 else utils.truncate(blocks_num)

    @staticmethod
    def _calc_single_block_num():
        pass

    def _calc_file_blocks_num(self, name, val):
        lines_num = utils.count_lines(val)
        return self._calc_blocks(name, lines_num)

    def _calc_subnet_blocks_num(self, name, val):
        addrs_num = len(IPNetwork(val))
        return self._calc_blocks(name, addrs_num)

    def _calc_range_blocks_num(self, name, val):
        nums, valid_range = utils.range_to_int_nums(val, check_valid=True)

        if valid_range:
            range_len = utils.sub_nums_in_seq(*nums)
            return self._calc_blocks(name, range_len)

        raise exceptions.InvalidPortsRange(val)

    def _calc_separated_blocks_num(self, name, val):
        els_num = len(val.split(','))
        return self._calc_blocks(name, els_num)

    def _calc_combined_blocks_num(self, name, val):
        vals = val.split(',')
        blocks_counts = []

        for el in vals:
            try:
                blocks_counts.append(self._calc_range_blocks_num(name, el))
            except TypeError:
                blocks_counts.append(1)

        return sum(blocks_counts)

    @property
    def blocks_num(self):
        blocks_num = {}

        for data in self._definer.data_types:
            try:
                num_blocks = self._blocks_calculators.get(data['type'])(
                    data['name'], data['data']
                )
            except TypeError:
                blocks_num.update({data['name']: 1})
            else:
                blocks_num.update({data['name']: num_blocks})

        return blocks_num


@dataclass(repr=False, eq=False, init=False)
class DataPreparator(BlocksCalculator):
    def __init__(self, hosts, ports=None, hosts_block_size=10, ports_block_size=20):
        super().__init__(hosts, ports, hosts_block_size, ports_block_size)
        self.data_getters = {
            'single': self.data_single,
            'file': self.data_from_file,
            'subnet': self.data_from_subnet,

            'range': self.data_from_range,
            'separated': self.data_from_separated,
            'combined': self.data_from_combined
        }

    @property
    def data_single(self):
        yield

    @property
    def data_from_file(self):
        yield

    @property
    def data_from_subnet(self):
        yield

    @property
    def data_from_range(self):
        yield

    @property
    def data_from_separated(self):
        yield

    @property
    def data_from_combined(self):
        yield

    @property
    def data_block(self):
        yield

    def get_data(self):
        hosts_data, ports_data = self._definer.data_types
        hosts_getter = self.data_getters.get(hosts_data['type'])
        ports_getter = self.data_getters.get(ports_data['type'])


class Test(DataPreparator):
    def test(self):
        # TODO
        #   1. получить кол-во блоков для хостов и портов
        #   2. запустить бесконечный цикл
        #   3. в бесконечном цикле вызывать получение блоков данных хостов и портов
        #   4. запускать корутины для блока хостов и портов для чека.
        #   5.* сделать флаг: например получить только блок хостов , потому что в icmp пинге не нужны порты.
        print()


"""
В каждом плагине должен быть вызов блока данных хостов и портов в бесконечном цикле
Предварительно в каждом плагине получить расчет кол-ва блоков

** получать блоки данных отдельно по флагам хост или порт
"""


# obj = DataPreparator('1.1.1.1', '80')
# obj.get_data()
