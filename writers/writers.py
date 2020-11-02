import csv
import os
import time
from datetime import datetime
from typing import List

from config import Transaction


class BaseWriter:
    def write(self):
        raise NotImplementedError


class CsvWriter(BaseWriter):
    def __init__(self, output_dir_path):
        if not os.path.isdir(output_dir_path):
            raise ValueError(f'{output_dir_path} is not directory')
        self.dir_path = output_dir_path

    def build_file_path(self):
        file_name = int(time.mktime(datetime.now().timetuple()))
        return f'{self.dir_path}/{file_name}.csv'

    def write(self, transactions: List[Transaction]):
        file_path = self.build_file_path()
        print(f'{self} is writing transactions to file {file_path}')
        with open(file_path, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(Transaction._fields)
            for transaction in transactions:
                writer.writerow(tuple(transaction))

    def __str__(self):
        return "Basic CSV Writer"
