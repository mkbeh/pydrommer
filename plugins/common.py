# -*- coding: utf-8 -*-
import os
import re


class ArgValueTypeDefiner:
    flag = None

    def __init__(self, hosts, ports=None):
        self.hosts = hosts
        self.ports = ports

        self.hosts_type_definers = {
            'file': self.is_file,
            'single': self.is_single,
            'subnet': self.is_subnet
        }
        self.ports_type_definers = {
            'file': self.is_file,
            'single': self.is_single,
            'range': self.is_range,
            'separated': self.is_separated,
            'combined': self.is_combined
        }

    @staticmethod
    def define_data(seq, data):
        for arg_type, func in seq.items():
            if func(data):
                return {'type': arg_type, 'data': data}

    @staticmethod
    def is_str_match(pattern, s):
        try:
            re.match(pattern, s).group()
        except AttributeError:
            return False
        else:
            return True

    @staticmethod
    def is_file(val):
        return os.path.isfile(val)

    def is_range(self, val):
        pattern = re.compile(r'^\d+-\d+$')
        return self.is_str_match(pattern, val)

    def is_separated(self, val):
        pattern = re.compile(r'^\d+,(\d+,?)+$')
        return self.is_str_match(pattern, val)

    def is_combined(self, val):
        pattern = re.compile(r'^\d+|(d+-\d+),(\d+|(d+-\d+),?)+')
        return self.is_str_match(pattern, val)

    def is_single(self, val):
        host_pattern = re.compile(r'^\d+.\d+.\d+.\d+$')
        port_pattern = re.compile(r'^\d+$')
        return self.is_str_match(host_pattern, val) or self.is_str_match(port_pattern, val)

    def is_subnet(self, val):
        pattern = re.compile(r'^\d+.\d+.\d+.\d+/\d{1,2}$')
        return self.is_str_match(pattern, val)

    def define_data_type(self):
        hosts_type = self.define_data(self.hosts_type_definers, self.hosts)
        ports_type = None

        if self.ports:
            ports_type = self.define_data(self.ports_type_definers, self.ports)

        return hosts_type, ports_type
