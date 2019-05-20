# -*- coding: utf-8 -*-
import itertools

from datetime import datetime
from extra import utils


class DataSorter:
    tmp_file = None
    fh = None
    data_block_size = 2

    @staticmethod
    def is_contains_elements(genexpr):
        count = 0

        for _ in genexpr:
            count += 1
            break

        return True if count > 0 else False

    @staticmethod
    def is_ip_in_slice(ip, genexpr, n):
        _, genexpr_cp = itertools.tee(genexpr)

        if ip in itertools.islice(genexpr_cp, 0, n):
            return True

        return False

    @property
    def ips_from_file(self):
        return (line.split(':')[0] for line in self.fh)

    def get_uniq_ips(self):
        all_ips, all_ips_cp = itertools.tee(self.ips_from_file)

        return (
            ip for n, ip in enumerate(all_ips) if not self.is_ip_in_slice(ip, all_ips_cp, n)
        )


class Output(DataSorter):
    final_fh = open(
        utils.get_file_path('pydrommer', f'final-{datetime.now()}.lst'), 'a'
    )

    def __init__(self, *args, **kwargs):
        super(Output, self).__init__(*args, **kwargs)
        self._output_to = kwargs.get('output_to')
        self._output_writers = {
            'file': self.to_file,
        }

    def to_file(self, data):
        self.final_fh.write(data)

    def find_ports_for_each_ip(self, ip):
        ports = ''

        with open(self.tmp_file, 'r') as file:
            for line in file:
                if ip in line:
                    ports += line.split(':')[1].replace('\n', '').strip() + ','

        self.to_file(f'{ip}:{ports}\n')

    def get_ips_with_ports_for_ips_block(self, ips_block):
        [self.find_ports_for_each_ip(ip) for ip in ips_block]

    def output(self, tmp_file):
        self._output_to = self._output_to
        self.tmp_file = tmp_file
        self.fh = open(self.tmp_file, 'r+')
        ips = self.get_uniq_ips()
        block_num = 0

        while True:
            ips_slice, ips_slice_cp = itertools.tee(
                itertools.islice(ips, block_num, self.data_block_size)
            )

            if not self.is_contains_elements(ips_slice_cp):
                break

            self.get_ips_with_ports_for_ips_block(ips_slice)

        self.fh.close()
        self.final_fh.close()
