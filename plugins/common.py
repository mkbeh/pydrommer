# -*- coding: utf-8 -*-
import os
import re

from dataclasses import dataclass, field


@dataclass(repr=False, eq=False)
class _ArgValueTypeDefiner:
    _hosts: str
    _ports: str = None

    _hosts_type_definers: dict = field(init=False)
    _ports_type_definers: dict = field(init=False)

    def __post_init__(self):
        self._hosts_type_definers = {
            'file': self._is_file,
            'single': self._is_single,
            'subnet': self._is_subnet
        }
        self._ports_type_definers = {
            'file': self._is_file,
            'single': self._is_single,
            'range': self._is_range,
            'separated': self._is_separated,
            'combined': self._is_combined
        }

    @staticmethod
    def _define_data(seq, data):
        for arg_type, func in seq.items():
            if func(data):
                return {'type': arg_type, 'data': data}

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

    def define_data_type(self):
        hosts_type = self._define_data(self._hosts_type_definers, self._hosts)
        ports_type = None

        if self._ports:
            ports_type = self._define_data(self._ports_type_definers, self._ports)

        return hosts_type, ports_type


@dataclass(repr=False, eq=False, init=False)
class DataPreparator(_ArgValueTypeDefiner):
    def __init__(self, hosts, ports=None):
        super().__init__(hosts, ports)
        self._data_types = self.define_data_type()
