# -*- coding: utf-8 -*-
import os
import re
import math
import linecache

from dataclasses import dataclass, field

from netaddr import IPNetwork

from extra import utils
from extra import exceptions


@dataclass(repr=False, eq=False)
class _ArgValueTypeDefiner:
    _hosts: str
    _ports: str

    _hosts_type_definers: dict = field(init=False)
    _ports_type_definers: dict = field(init=False)
    data_types: dict = field(init=False)

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

    def get_data_types(self):
        hosts_type = self._define_data('hosts', self._hosts_type_definers, self._hosts)
        ports_type = self._define_data('ports', self._ports_type_definers, self._ports)

        if not hosts_type:
            raise exceptions.IncorrectHosts(self._hosts)

        return {'hosts': hosts_type, 'ports': ports_type}


@dataclass(repr=False, eq=False, init=False)
class BlocksCalculator(_ArgValueTypeDefiner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._hosts_block_size = kwargs.get('hosts_block_size')
        self._ports_block_size = kwargs.get('ports_block_size')
        self.data_types = self.get_data_types()

        self._blocks_calculators = {
            'single': self._calc_single_block_num,
            'file': self._calc_file_blocks_num,
            'subnet': self._calc_subnet_blocks_num,

            'range': self._calc_range_blocks_num,
            'separated': self._calc_separated_blocks_num,
            'combined': self._calc_combined_blocks_num
        }

    def _calc_blocks(self, name, num):
        block_size = self.__dict__.get(f'_{name}_block_size')
        blocks_num = math.ceil(num / block_size)

        return 1 if blocks_num == 0 else utils.truncate(blocks_num)

    @staticmethod
    def _calc_single_block_num():
        pass

    def _calc_file_blocks_num(self, name, val):
        lines_num = utils.count_lines(val) + 1
        return self._calc_blocks(name, lines_num)

    def _calc_subnet_blocks_num(self, name, val):
        addrs_num = len(IPNetwork(val))
        return self._calc_blocks(name, addrs_num)

    def _calc_range_blocks_num(self, name, val):
        nums, valid_range = utils.range_to_int_nums(val, check_valid=True)

        if valid_range:
            range_len = utils.sub_nums_in_seq(*nums)
            return self._calc_blocks(name, range_len + 1)

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
                continue

        return sum(blocks_counts)

    def get_num_blocks(self):
        num_blocks_data = {}

        for data in self.data_types.values():
            try:
                num_blocks = self._blocks_calculators.get(data['type'])(
                    data['name'], data['data']
                )
            except TypeError:
                num_blocks_data.update({data['name']: 1})
            else:
                num_blocks_data.update({data['name']: num_blocks})

        return num_blocks_data


@dataclass(repr=False, eq=False, init=False)
class DataPreparator(BlocksCalculator):
    def __init__(self, hosts, ports='1-65535', hosts_block_size=10, ports_block_size=20):
        super().__init__(hosts, ports, hosts_block_size=hosts_block_size, ports_block_size=ports_block_size)
        self.hosts_data, self.ports_data = self.data_types
        self.num_blocks = self.get_num_blocks()
        self.data_getters = {
            'single': self.get_single_data,
            'file': self.get_data_from_file,
            'subnet': self.get_data_from_subnet,

            'range': self.get_data_from_range,
            'separated': self.get_data_from_separated,
            'combined': self.get_data_from_combined
        }

    def calc_block_range(self, name, block_num):
        block_size = self.__dict__.get(f'_{name}_block_size')
        end = block_num * block_size
        start = end - block_size

        return start, end

    @staticmethod
    def get_single_data(name, data, block_num):
        seq = (data,)
        return seq if block_num and name else seq

    def get_data_from_file(self, name, file, block_num):
        start, end = self.calc_block_range(name, block_num)
        lines = (utils.clear_string(linecache.getline(file, line_num))
                 for line_num in range(start, end))

        linecache.clearcache()
        return filter(lambda x: x != '', lines)

    def get_data_from_subnet(self, name, data, block_num):
        start, end = self.calc_block_range(name, block_num)
        data_slice = IPNetwork(data)[start:end]

        return (el.format() for el in data_slice)

    def get_data_from_range(self, name, range_, block_num):
        start_block, end_block = self.calc_block_range(name, block_num)
        start_range, end_range = utils.get_integers_from_str(range_, '-')

        start = start_range + start_block
        end = start_range + end_block if start_range + end_block < end_range else end_range + 1

        return (i for i in range(start, end))

    @staticmethod
    def get_data_from_separated(name, data, block_num):
        nums = utils.get_integers_from_str(data, ',')
        return nums if name and block_num else nums

    def get_data_from_combined(self, name, data, block_num):
        vals = utils.split_str_by_separator(data, ',')
        final_data = []

        for val in vals:
            try:
                final_data.append(int(val))
            except ValueError:
                continue

        for val in vals:
            try:
                int(val)
            except ValueError:
                final_data.extend(
                    self.get_data_from_range(name, val, block_num)
                )

        return (i for i in final_data)

    def get_data_block(self, block_num, data_belong_to=None):
        data = self.data_types.get(data_belong_to)

        return self.data_getters.get(
           data.get('type')
        )(data.get('name'), data.get('data'), block_num)


@dataclass(repr=False, eq=False, init=False)
class AsyncPluginBase:
    pass
