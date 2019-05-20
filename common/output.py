# -*- coding: utf-8 -*-
import itertools


class DataSorter:
    tmp_file = None
    fh = None

    def get_ips_from_file(self):
        return (line.split(':')[0] for line in self.fh)

    @staticmethod
    def is_ip_in_slice(ip, genexpr, n):
        _, genexpr_cp = itertools.tee(genexpr)

        if ip in itertools.islice(genexpr_cp, 0, n):
            return True

        return False

    def get_uniq_ips(self):
        all_ips = self.get_ips_from_file()
        all_ips, all_ips_cp = itertools.tee(all_ips)

        return (
            ip for n, ip in enumerate(all_ips) if not self.is_ip_in_slice(ip, all_ips_cp, n)
        )

    def find_ports_for_each_ip(self):
        pass

    def sorted_data(self):
        self.fh = open(self.tmp_file, 'r')
        ips = self.get_uniq_ips()
        self.fh.close()


class Output(DataSorter):
    def __init__(self, *args, **kwargs):
        super(Output, self).__init__(*args, **kwargs)
        self._output_to = kwargs.get('output_to')
        self._data_writers = {
            'file': self.to_file,
        }

    def to_file(self):
        pass

    def output(self, tmp_file):
        print('tmp file - ', tmp_file)
        self.tmp_file = tmp_file
        sorted_data = self.sorted_data()
