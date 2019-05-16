# -*- coding: utf-8 -*-


class ArgValueTypeDefinerExc(Exception):
    def __init__(self, error_msg=''):
        Exception.__init__(self, f'{error_msg}')


class IncorrectHosts(ArgValueTypeDefinerExc):
    def __init__(self, hosts):
        super().__init__(error_msg=f'Incorrect hosts {hosts}.')


class BlocksCalculatorExc(Exception):
    def __init__(self, error_msg=''):
        Exception.__init__(self, f'{error_msg}')


class InvalidPortsRange(BlocksCalculatorExc):
    def __init__(self, ports_range):
        super().__init__(error_msg=f'Invalid ports range {ports_range}.')



