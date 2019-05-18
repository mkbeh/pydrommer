# -*- coding: utf-8 -*-


class DataSorter:
    def sorted_data(self):
        # Тут может быть прикол , если файл получился огромный , то надо его как то блоками читать
        # И есть еще один минус , который заключается в том , что все собранные данные бахаются разом и целиком для
        # записи во временный файл , что не есть гуд.
        pass


class Output(DataSorter):
    def __init__(self, *args, **kwargs):
        super(Output, self).__init__(*args, **kwargs)
        self.output_to = kwargs.get('output_to')

    def to_file(self):
        pass

    def output(self, tmp_file):
        print('tmp file - ', tmp_file)
