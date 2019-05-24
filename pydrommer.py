# -*- coding: utf-8 -*-
import os
import sys
import argparse
import asyncio
import uvloop

from datetime import datetime

from extra.interface import *

from plugins.httpheadersgetter import HTTPHeadersGetter
from plugins.portsscanner import PortsChecker


available_plugins = {
    'ports_scanner': PortsChecker,
    'http_headers_getter': HTTPHeadersGetter,
}
default_ports = {
    'ports_scanner': '1-65535',
    'http_headers_getter': '80',
}


def get_formatted_plugin_start_msg():
    date_now = datetime.now().strftime('%d-%m-%y %H-%M-%S')
    return PLUGIN_START_MSG.format(date_now, 1, 2)


def start_plugin(plugin, data):
    uvloop.install()
    hosts, ports = data.pop('hosts'), data.pop('ports')

    os.system('clear')
    print(get_formatted_plugin_start_msg())

    asyncio.run(plugin(hosts, ports, **data).run())


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


def get_valid_args_data(args):
    rename_options(args)

    if not args['ports']:
        args['ports'] = default_ports.get(args['plugins'])

    args.pop('plugins')


def call_specific_module(args):
    plugin = available_plugins.get(args['plugins'])
    get_valid_args_data(args)
    start_plugin(plugin, args)


def args_checker():
    try:
        sys.argv[1]
    except IndexError:
        print(MODULES)
        sys.exit(0)


def parser_base_options(parser):
    output_to = ['file']

    parser.add_argument('-iH', required=True, help='Single host or from available input.')
    parser.add_argument('-iP', required=False, help='Single port or from available input.')
    parser.add_argument('-cT', metavar='SECS', type=float, default=.1, help=CYCLE_TIMEOUT_HELP)
    parser.add_argument('-rT', metavar='SECS', type=float, default=.1, help=READ_TIMEOUT_HELP)
    parser.add_argument('-o', choices=output_to, default='file', help=OUTPUT_HELP)
    parser.add_argument('-hS', metavar='NUM', type=int, default=35, help=HOSTS_BLOCK_SIZE_HELP)
    parser.add_argument('-pS', metavar='NUM', type=int, default=20, help=PORTS_BLOCK_SIZE_HELP)


def http_headers_getter_parser(parser):
    parser_base_options(parser)
    parser.add_argument('--only-jsonrpc', required=False, type=bool, default=False, help='Will discover only JSON RPC.')


def ports_scanner_parser(parser):
    parser_base_options(parser)


def cli():
    # args_checker()

    parser = argparse.ArgumentParser(prog='pydrommer', description='SMTH DESC')
    subparsers = parser.add_subparsers(dest='plugins')

    ports_scanner = subparsers.add_parser(name='ports_scanner')
    ports_scanner_parser(ports_scanner)

    http_headers_getter = subparsers.add_parser(name='http_headers_getter')
    http_headers_getter_parser(http_headers_getter)

    args = parser.parse_args(
        # ['http_headers_getter', '-iH', '46.160.199.52', '-iP', '0-65535', '--only-jsonrpc', 'True']
    )
    call_specific_module(vars(args))


if __name__ == '__main__':
    cli()
