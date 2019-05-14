# -*- coding: utf-8 -*-
import sys

from plugins.pinger import PingTCP, PingICMP


"""
keys:
-h hosts
-p ports
-pI icmp ping
-pT tcp ping
"""


CLI_KEYS = [
    '-h',
    '-p',
]

CLI_OPTIONS = {
    '-pI': PingICMP,
    '-PT': PingTCP,
}


def cli_args_handler(options, keys):
    print(options)
    print(keys)


def cli_args_parser():
    args = sys.argv[1:]
    options = []
    keys = {}

    for arg in args:
        if arg in CLI_KEYS:
            arg_index = args.index(arg)
            arg_val = args[arg_index + 1]
            keys.update({arg: arg_val})
        elif arg in CLI_OPTIONS.keys():
            options.append(arg)

    cli_args_handler(options, keys)


def cli():
    cli_args_parser()


if __name__ == '__main__':
    cli()
