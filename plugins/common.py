# -*- coding: utf-8 -*-
import os
import re
import math

from dataclasses import dataclass, field

from netaddr import IPNetwork

from extra import utils


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
            'file': self._is_file,
            'single': self._is_single,
            'separated': self._is_separated,
            'combined': self._is_combined,
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
        pattern = re.compile(r'^\d+|(d+-\d+),(\d+|(d+-\d+),?)+')
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
    def __init__(self, *args, hosts_block_size=3, ports_block_size=20):
        self.hosts_block_size = hosts_block_size
        self.ports_block_size = ports_block_size
        self.definer = _ArgValueTypeDefiner(*args)

        self.blocks_calculators = {
            'single': self.calc_single_block_num,
            'file': self.calc_file_blocks_num,
            'subnet': self.calc_subnet_blocks_num,

            'range': self.calc_range_blocks_num,
            'separated': self.calc_separated_blocks_num,
            'combined': self.calc_combined_blocks_num
        }

    def calc_blocks(self, name, num):
        block_size = self.__dict__.get(name + '_block_size')
        blocks_num = math.ceil(num / block_size)

        return 1 if blocks_num == 0 else utils.truncate(blocks_num)

    @staticmethod
    def calc_single_block_num():
        pass

    def calc_file_blocks_num(self, name, val):
        lines_num = utils.count_lines(val)
        return self.calc_blocks(name, lines_num)

    def calc_subnet_blocks_num(self, name, val):
        addrs_num = len(IPNetwork(val))
        return self.calc_blocks(name, addrs_num)

    def calc_range_blocks_num(self, val):
        pass

    def calc_separated_blocks_num(self, val):
        pass

    def calc_combined_blocks_num(self, val):
        pass

    def calc_blocks_num(self):
        blocks_num = {}

        for data in self.definer.data_types:
            try:
                num_blocks = self.blocks_calculators.get(data['type'])(
                    data['name'], data['data']
                )
            except TypeError:
                blocks_num.update({data['name']: 1})
            else:
                blocks_num.update({data['name']: num_blocks})

        print(self.definer.data_types)
        print(blocks_num)

        return blocks_num


obj = BlocksCalculator('192.0.2.16/29', '80').calc_blocks_num()


@dataclass(repr=False, eq=False, init=False)
class DataPreparator(_ArgValueTypeDefiner):
    def __init__(self, hosts, ports=None, hosts_block_size=10, ports_block_size=20):
        super().__init__(hosts, ports)
        self.hosts_block_size = hosts_block_size
        self.ports_block_size = ports_block_size
        self.data_getters = {
            'single': self.data_single,
            'file': self.data_from_file,
            'subnet': self.data_from_subnet,

            'range': self._is_range,
            'separated': self._is_separated,
            'combined': self._is_combined
        }

    @property
    def data_single(self):
        for i in range(10):
            yield i

    @property
    def data_from_file(self):
        pass

    @property
    def data_from_subnet(self):
        pass

    @property
    def data_from_range(self):
        pass

    @property
    def data_from_separated(self):
        pass

    @property
    def data_from_combined(self):
        pass

    @property
    def data_block(self):
        pass

    def get_data(self):
        hosts_data, ports_data = self.data_types
        hosts_getter = self.data_getters.get(hosts_data['type'])
        ports_getter = self.data_getters.get(ports_data['type'])

        s = hosts_getter

        for i in s:
            print(i)


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
