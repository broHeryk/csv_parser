import csv
import os
from typing import List

from config import Transaction
from readers.readers import (Bank1Reader, Bank2Reader, Bank3Reader,
                             BaseCsvReader)
from writers.writers import BaseWriter

reader_classes = [Bank1Reader, Bank2Reader, Bank3Reader]
columns_to_class_map = {reader.known_columns: reader for reader in reader_classes}


def get_csv_files(path: str) -> str:
    for f_name in os.listdir(path):
        if f_name.endswith('.csv'):
            yield f'{path}/{f_name}'


def match_reader(csv_reader: '_csv.reader') -> BaseCsvReader:
    """
    Function matches reader class by the first line of csv file.
    :raises:
        KeyError - once no reader for that set of column is found
    """
    header = next(csv_reader)
    reader_class = columns_to_class_map[tuple(sorted(header))]
    return reader_class(header=header)


def get_transactions_from_file(file_path: str) -> List[Transaction]:
    try:
        with open(file_path, 'r') as f:
            csv_file = csv.reader(f)
            reader = match_reader(csv_file)
            return reader.unify_records(csv_file)
    except KeyError as ke:
        print('No reader for this set of fields:', ke)
        return []


def write_transactions(transactions: List[Transaction], writers: List[BaseWriter]) -> None:
    print('Start writing transactions')
    for writer in writers:
        try:
            writer.write(transactions)
        except Exception as e:
            print(f'Writing transactions is failed for writer {writer}. Error details({str(e)})')
