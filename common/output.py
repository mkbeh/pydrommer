# -*- coding: utf-8 -*-


class DataSorter:
    def sorted_data(self):
        pass


class Output(DataSorter):
    def __init__(self, *args, **kwargs):
        super(Output, self).__init__(*args, **kwargs)
        self.output_to = kwargs.get('output_to')

    def to_file(self):
        pass

    def output(self, tmp_file):
        print('tmp file - ', tmp_file)
