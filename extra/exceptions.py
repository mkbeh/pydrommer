# -*- coding: utf-8 -*-


class CommonExceptions(Exception):
    def __init__(self, error_msg=''):
        Exception.__init__(self, f'{error_msg}')


class InvalidPortsRange(CommonExceptions):
    def __init__(self, ports_range):
        super().__init__(error_msg=f'Invalid ports range {ports_range}.')
