import csv
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from itertools import zip_longest


# Открытие файлов разных форматов
class OpenFile:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def open_file(self):
        pass


class OpenCsvFile(OpenFile):
    def open_file(self):
        with open(self.file_name, newline='') as File:
            reader = csv.reader(File)
            headers = next(reader, None)
            column = {}
            for h in headers:
                column[h] = []
            for row in reader:
                for h, v in zip(headers, row):
                    column[h].append(v)
            return column, list(column.keys())


class OpenJsonFile(OpenFile):
    def open_file(self):
        with open(self.file_name) as File:
            reader = json.load(File)['fields']
            column = {}
            for row in reader:
                for k, v in row.items():
                    column.setdefault(k, []).append(v)
            return column, list(column.keys())


class OpenXmlFile(OpenFile):
    def open_file(self):
        reader = ET.parse(self.file_name).getroot()
        column = defaultdict(list)
        for tag in reader.findall('objects/object'):
            name = tag.attrib['name']
            for val in tag:
                column[name].append(val.text)
        return dict(column), list(dict(column).keys())


class Task:
    def __init__(self, dictionary: dict):
        self.dictionary = dictionary
        self.orderBy = 'D1'
        self.groupBy = 'D'

    def get_tsv(self):
        pass

    @staticmethod
    def transpose(d: dict):
        h = list(d.keys())
        v = list(d.values())
        # Транспонирование двумерного списка.
        # Вид до транспонирования: [[D1, a, b, c], [M1, 1, 2, 3]].
        # Вид после транспонирования: [[D1, M1], [a, 1], [b, 2], [c, 3]].
        v_transposed = list(map(list, zip(*v)))
        return h, v_transposed

    # Запись в tsv файл
    @staticmethod
    def write_tsv(headers: list, rows: list, file: str):
        with open(file, 'wt', newline='') as out_file:
            tsv_writer = csv.writer(out_file, delimiter='\t')
            tsv_writer.writerow(headers)
            for row in rows:
                tsv_writer.writerow(row)


# Решение базовой задачи
class BasicTask(Task):
    def get_tsv(self):
        # Поставить в словаре на первую позицию столбец,
        # по которому будет производиться сортировка.
        sort_dictionary = dict()
        sort_dictionary[self.orderBy] = self.dictionary.pop(self.orderBy)
        sort_dictionary.update(self.dictionary)
        # Получение заголовков и строк
        headers, values = Task.transpose(sort_dictionary)
        # Сортировка списка по первому столбцу
        values = sorted(values, key=lambda x: x[0])
        # Запись в файл
        Task.write_tsv(headers, values, 'basic_results.tsv')


def get_unique_headers(headers: list, values: list):
    # Получение заголовков, которые встречаются во всех файлах.
    unique_headers = sorted(set.intersection(*map(set, headers)), key=lambda x: headers[0].index(x))
    dd = defaultdict(list)
    for k in unique_headers:
        for v in values:
            dd[k] += (v[k])
    # Выполнения задач
    tasks = [BasicTask(dict(dd))]
    for t in tasks:
        t.get_tsv()


def read_file(f: list):
    headers = []
    values = []
    for file in f:
        v, h = file.open_file()
        headers.append(h)
        values.append(v)
    get_unique_headers(headers, values)


if __name__ == '__main__':
    # Список файлов
    files = [
        OpenCsvFile('csv_data_1.csv'),
        OpenCsvFile('csv_data_2.csv'),
        OpenJsonFile('json_data.json'),
        OpenXmlFile('xml_data.xml')
    ]
    read_file(files)
