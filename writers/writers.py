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

    def write(self, transactions: List[Transaction]):
        file_name = int(time.mktime(datetime.now().timetuple()))
        target_file_path = f'{self.dir_path}/{file_name}.csv'
        print(f'{self} is writing transactions to file {target_file_path}')
        with open(target_file_path, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(Transaction._fields)
            for transaction in transactions:
                writer.writerow(tuple(transaction))

    def __str__(self):
        return "Basic CSV Writer"
