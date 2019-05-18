# -*- coding: utf-8 -*-


class DataSorter:
    pass


class Output(DataSorter):
    def __init__(self):
        super(Output, self).__init__()

    def to_file(self):
        pass

    def output(self, output_to, tmp_file):
        print('output_to - ', output_to)
        print('tmp file - ', tmp_file)
