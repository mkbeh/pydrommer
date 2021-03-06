# -*- coding: utf-8 -*-
import os
import re
import math
import linecache
import asyncio
import itertools
import shutil

from dataclasses import dataclass, field

from netaddr import IPNetwork
from termcolor import colored

from src.extra import utils, exceptions, interface


@dataclass(repr=False, eq=False)
class ArgValueTypeDefiner:
    _hosts: str
    _ports: str

    _hosts_type_definers: dict = field(init=False)
    _ports_type_definers: dict = field(init=False)
    data_types: dict = field(init=False)

    def __post_init__(self):
        self._hosts_type_definers = {
            'spec': self._is_spec_file,
            'file': self._is_file,
            'single': self._is_single,
            'subnet': self._is_subnet,
            'url': self._is_url,
        }
        self._ports_type_definers = {
            'spec': self._is_spec_file,
            'range': self._is_range,
            'separated': self._is_separated,
            'combined': self._is_combined,
            'file': self._is_file,
            'service_file': self._is_service_file,
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
    def _is_spec_file(val):
        return val.endswith('.prm')

    @staticmethod
    def _is_service_file(val):
        return True if val == 'src-services1.lst' else False

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
        new_val = val.split(',')

        if len(new_val) > 1:
            pattern = re.compile(r'^\d+|(d+-\d+),(\d+|(d+-\d+),?)+$')
            return self._is_str_match(pattern, val)

        return False

    def _is_single(self, val):
        host_pattern = re.compile(r'^\d+.\d+.\d+.\d+$')
        port_pattern = re.compile(r'^\d+$')
        return self._is_str_match(host_pattern, val) or self._is_str_match(port_pattern, val)

    def _is_url(self, val):
        url_pattern = re.compile(r'\w+\.\w+')
        return self._is_str_match(url_pattern, val) or val.startswith('http')

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
class _BlocksCalculator(ArgValueTypeDefiner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._hosts_block_size = kwargs.get('hosts_block_size', 35)
        self._ports_block_size = kwargs.get('ports_block_size', 20)
        self.data_types = self.get_data_types()

        self._blocks_calculators = {
            'single': self._calc_single_block_num,
            'file': self._calc_file_blocks_num,
            'service_file': self._calc_service_file_blocks_num,
            'subnet': self._calc_subnet_blocks_num,
            'url': self._calc_single_block_num,

            'range': self._calc_range_blocks_num,
            'separated': self._calc_separated_blocks_num,
            'combined': self._calc_combined_blocks_num,
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

    def _calc_service_file_blocks_num(self, name, val):
        lines_num = 1001
        num_blocks = self._calc_blocks(name, lines_num)
        return num_blocks if val else num_blocks

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
                continue

        return sum(blocks_counts)

    def _check_on_spec_file(self):
        if self.data_types['hosts']['type'] != 'spec':
            raise exceptions.SpecialFileNotFound

        hosts_num_blocks = self._calc_file_blocks_num('hosts', self.data_types['hosts']['data'])
        return {'hosts': hosts_num_blocks}

    def get_num_blocks(self):
        num_blocks_data = {}

        try:
            return self._check_on_spec_file()
        except exceptions.SpecialFileNotFound:
            pass

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
class _DataPreparator(_BlocksCalculator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_blocks = self.get_num_blocks()
        self._data_getters = {
            'single': self._get_single_data,
            'file': self._get_data_from_file,
            'subnet': self._get_data_from_subnet,
            'url': self._get_single_data,

            'range': self._get_data_from_range,
            'separated': self._get_data_from_separated,
            'combined': self._get_data_from_combined,
            'service_file': self._get_data_from_service_file,
            'spec': self._get_data_from_spec_file,
        }

    def _calc_block_range(self, name, block_num):
        block_size = self.__dict__.get(f'_{name}_block_size')
        end = block_num * block_size
        start = end - block_size

        return start, end

    @staticmethod
    def _get_single_data(name, data, block_num):
        seq = (data,)
        return seq if block_num and name else seq

    def _get_data_from_file(self, name, file, block_num):
        start, end = self._calc_block_range(name, block_num)
        lines = (utils.clear_string(linecache.getline(file, line_num))
                 for line_num in range(start, end))

        linecache.clearcache()
        return filter(lambda x: x != '', lines)

    def _get_data_from_service_file(self, name, file, block_num):
        path_to_service_file = utils.get_path_to_services_file(file)
        start, end = self._calc_block_range(name, block_num)
        lines = (utils.clear_string(linecache.getline(path_to_service_file, line_num))
                 for line_num in range(start, end))

        def get_port_from_str(str_):
            return str_.split('\t')[1].split('/')[0]

        linecache.clearcache()
        return [get_port_from_str(line) for line in lines if line != '']

    def _get_data_from_subnet(self, name, data, block_num):
        start, end = self._calc_block_range(name, block_num)
        data_slice = IPNetwork(data)[start:end]

        return (el.format() for el in data_slice)

    def _get_data_from_range(self, name, range_, block_num):
        start_block, end_block = self._calc_block_range(name, block_num)
        start_range, end_range = utils.get_integers_from_str(range_, '-')

        start = start_range + start_block
        end = start_range + end_block if start_range + end_block < end_range else end_range + 1

        return (i for i in range(start, end))

    @staticmethod
    def _get_data_from_separated(name, data, block_num):
        nums = utils.get_integers_from_str(data, ',')
        return nums if name and block_num else nums

    def _get_data_from_combined(self, name, data, block_num):
        vals = utils.split_str_by_separator(data, ',')
        final_data = []

        if block_num == 1:
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
                    self._get_data_from_range(name, val, block_num)
                )

        return (i for i in final_data)

    @staticmethod
    def _prepare_data_from_spec_file(lines):
        return map(lambda x: (x[0], x[1].split(' ')),
                   map(lambda x: x.split(':'),
                       filter(lambda x: x != '', lines)))

    def _get_data_from_spec_file(self, name, file, block_num):
        start, end = self._calc_block_range(name, block_num)
        lines = (utils.clear_string(linecache.getline(file, line_num))
                 for line_num in range(start, end))

        linecache.clearcache()
        return self._prepare_data_from_spec_file(lines)

    def get_data_block(self, block_num, data_belong_to=None):
        data = self.data_types.get(data_belong_to)

        return self._data_getters.get(
           data.get('type')
        )(data.get('name'), data.get('data'), block_num)


@dataclass(repr=False, eq=False, init=False)
class AsyncPluginBase(_DataPreparator):
    _term_columns = shutil.get_terminal_size().columns

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_type_spec = None

    def _cli_verbose(self, hosts_block_num, ports_block_num):
        percent_per_host_iter = 100 / self.num_blocks['hosts']
        percent_per_port_iter = percent_per_host_iter / self.num_blocks['ports']

        current_progress = hosts_block_num * percent_per_host_iter + ports_block_num * percent_per_port_iter
        percent_progress = round(current_progress, 3)
        progressbar_progress = round((self._term_columns - 25) / 100 * current_progress)

        percent_out = f'[ {percent_progress}/100 (%) ]'
        progressbar_out = f'[ {"=" * progressbar_progress}> {" " * (self._term_columns - 25 - progressbar_progress)}]'

        os.system('clear')
        print(interface.LOGO, end='')
        print(interface.PLUGIN_START_MSG, end='')

        if hosts_block_num != self.num_blocks['hosts'] and ports_block_num != self.num_blocks['ports']:
            print(colored(progressbar_out, 'green') + colored(percent_out, 'yellow'))

    async def _plugin_handler(self, func, hosts_block, ports_block=None):
        if ports_block:
            genexpr = (func(host, ports_block) for host in hosts_block)
        elif self._data_type_spec:
            genexpr = (func(host, ports) for host, ports in hosts_block)
        else:
            genexpr = (func(host) for host in hosts_block)

        await asyncio.gather(*genexpr)

    def _is_data_type_spec(self):
        return True if self.data_types['hosts']['type'] == 'spec' else False

    async def run_plugin(self, func, require_ports=False):
        self._data_type_spec = self._is_data_type_spec()

        if self._data_type_spec:
            require_ports = False

        for host_block_num in range(self.num_blocks['hosts']):
            hosts_data_block = self.get_data_block(host_block_num + 1, data_belong_to='hosts')

            if require_ports:
                for port_block_num in range(self.num_blocks['ports']):
                    hosts_data_block, hosts_data_block_cp = itertools.tee(hosts_data_block)
                    ports_data_block = list(self.get_data_block(port_block_num + 1, data_belong_to='ports'))
                    await self._plugin_handler(func, hosts_data_block_cp, ports_data_block)
                    self._cli_verbose(host_block_num, port_block_num + 1)
            else:
                await self._plugin_handler(func, hosts_data_block)
