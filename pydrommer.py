# -*- coding: utf-8 -*-
import os
import sys
import re
import argparse
import asyncio
import uvloop

import netaddr

from datetime import datetime

from extra.interface import *
from extra import utils

from common.pluginbase import ArgValueTypeDefiner

from plugins.httpheadersgetter import HTTPHeadersGetter
from plugins.portsscanner import PortsChecker


class DataCalculator(ArgValueTypeDefiner):
    def __init__(self, *args):
        super().__init__(*args)
        self.data = args

        self._data_calculators = {
            'spec': self._is_spec_file,
            'single': self._calc_single_data,
            'file': self._calc_file_data,
            'subnet': self._calc_subnet_data,
            'url': self._calc_single_url_data,

            'range': self._calc_range_data,
            'separated': self._calc_separated_data,
            'combined': self._calc_combined_data,
        }

    def _calc_spec_file_data(self, file):
        return self._calc_file_data(file)

    @staticmethod
    def _calc_single_data(val):
        return 1 if val else 1

    @staticmethod
    def _calc_file_data(file):
        return utils.count_lines(file)

    @staticmethod
    def _calc_subnet_data(subnet):
        return len(netaddr.IPNetwork(subnet))

    @staticmethod
    def _calc_single_url_data(val):
        return 1 if val else 1

    @staticmethod
    def _calc_range_data(rng):
        return utils.sub_nums_in_seq(*utils.range_to_int_nums(rng))

    @staticmethod
    def _calc_separated_data(val):
        return len(val.split(','))

    @staticmethod
    def _calc_combined_data(val):
        pattern = re.compile(r'-')
        vals = val.split(',')
        calculated_data = []

        for val in vals:
            if re.search(pattern, val):
                calculated_data.append(
                    utils.sub_nums_in_seq(*utils.range_to_int_nums(val))
                )
                continue

            calculated_data.append(1)

        return sum(calculated_data)

    @property
    def calc_data(self):
        calculated_data = {}

        for name, val in self.get_data_types().items():
            result = self._data_calculators.get(val['type'])(val['data'])
            calculated_data.update({name: result})

        return calculated_data.values()


class Cli:
    data_calculator = None
    available_plugins = {
        'ports_scanner': PortsChecker,
        'http_headers_getter': HTTPHeadersGetter,
    }
    default_ports = {
        'ports_scanner': '1-65535',
        'http_headers_getter': '80',
    }

    def print_formatted_plugin_start_msg(self):
        date_now = datetime.now().strftime('%d-%m-%y %H-%M-%S')
        print(PLUGIN_START_MSG.format(date_now, *self.data_calculator.calc_data))

    def start_plugin(self, plugin, data):
        hosts, ports = data.pop('hosts'), data.pop('ports')
        self.data_calculator = DataCalculator(hosts, ports)

        os.system('clear')
        self.print_formatted_plugin_start_msg()

        uvloop.install()
        asyncio.run(plugin(hosts, ports, **data).run())

    @staticmethod
    def rename_options(args):
        cp = args.copy()
        valid_keys = {
            'iH': 'hosts',
            'iP': 'ports',
            'cT': 'timeout',
            'rT': 'read_timeout',
            'o': 'output_to',
            'hS': 'hosts_block_size',
            'pS': 'ports_block_size',
            'plugins': 'plugins',
            'only_jsonrpc': 'only_jsonrpc',
        }

        for key in cp.keys():
            args[valid_keys.get(key)] = args.pop(key)

    def get_valid_args_data(self, args):
        self.rename_options(args)

        if not args['ports']:
            args['ports'] = self.default_ports.get(args['plugins'])

        args.pop('plugins')

    def call_specific_module(self, args):
        plugin = self.available_plugins.get(args['plugins'])
        self.get_valid_args_data(args)
        self.start_plugin(plugin, args)

    @staticmethod
    def args_checker():
        try:
            sys.argv[1]
        except IndexError:
            print(MODULES)
            sys.exit(0)

    @staticmethod
    def parser_base_options(parser):
        output_to = ['file']

        parser.add_argument('-iH', required=True, help='Single host or from available input.')
        parser.add_argument('-iP', required=False, help='Single port or from available input.')
        parser.add_argument('-cT', metavar='SECS', type=float, default=.1, help=CYCLE_TIMEOUT_HELP)
        parser.add_argument('-rT', metavar='SECS', type=float, default=.1, help=READ_TIMEOUT_HELP)
        parser.add_argument('-o', choices=output_to, default='file', help=OUTPUT_HELP)
        parser.add_argument('-hS', metavar='NUM', type=int, default=35, help=HOSTS_BLOCK_SIZE_HELP)
        parser.add_argument('-pS', metavar='NUM', type=int, default=20, help=PORTS_BLOCK_SIZE_HELP)

    def http_headers_getter_parser(self, parser):
        self.parser_base_options(parser)
        parser.add_argument('--only-jsonrpc', required=False, type=bool, default=False,
                            help='Will discover only JSON RPC.')

    def ports_scanner_parser(self, parser):
        self.parser_base_options(parser)

    def cli(self):
        self.args_checker()

        parser = argparse.ArgumentParser(prog='pydrommer', description='SMTH DESC')
        subparsers = parser.add_subparsers(dest='plugins')

        ports_scanner = subparsers.add_parser(name='ports_scanner')
        self.ports_scanner_parser(ports_scanner)

        http_headers_getter = subparsers.add_parser(name='http_headers_getter')
        self.http_headers_getter_parser(http_headers_getter)

        args = parser.parse_args()
        self.call_specific_module(vars(args))


if __name__ == '__main__':
    Cli().cli()
