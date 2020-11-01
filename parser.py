from config import input_path, output_path
from utils import get_csv_files, get_transactions_from_file, write_transactions
from writers.writers import CsvWriter


def parse_csv_files():
    transactions = []
    for file_path in get_csv_files(input_path):
        print(f'Reading file: {file_path}')
        transactions += get_transactions_from_file(file_path)
    print(f'{len(transactions)} transactions have been parsed')
    return transactions


def process_files():
    print('Processing is started')
    transactions = parse_csv_files()
    write_transactions(transactions=transactions, writers=[CsvWriter(output_dir_path=output_path)])
    print('Processing is finished')


if __name__ == '__main__':
    process_files()
