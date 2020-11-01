import time
from datetime import datetime
from decimal import Decimal
from typing import List

from config import Transaction, transaction_fields


class BaseCsvReader:
    known_columns = tuple()

    def __init__(self, header):
        self.column_index_map = {col: header.index(col) for col in self.known_columns}

    def unify_records(self, csv_reader: '_csv.reader') -> List[Transaction]:
        unified_records = []
        for record in csv_reader:
            unified_records.append(self.get_transaction(record))
        return unified_records

    def type(self, record):
        return self.get_value_from_record(record, 'type')

    def sender(self, record):
        return self.get_value_from_record(record, 'from')

    def recipient(self, record):
        return self.get_value_from_record(record, 'to')

    def get_value_from_record(self, record, known_field_name):
        try:
            target_index = self.column_index_map[known_field_name]
            return record[target_index]
        except KeyError as ke:
            print(f'Key {ke} is not included to field mapping. Empty string will be returned')
            return ''

    def get_transaction(self, record: List[str]) -> Transaction:
        transaction = {field: getattr(self, field)(record) for field in transaction_fields}
        return Transaction(**transaction)

    @staticmethod
    def make_timestamp(date: str, date_format: str) -> float:
        try:
            date_value = datetime.strptime(date, date_format)
        except ValueError:
            print(f'Could not format the date {date} with format {date_format}. "-1" will be returned')
            return -1
        return int(time.mktime(date_value.timetuple()))


class Bank1Reader(BaseCsvReader):
    known_columns = tuple(sorted(['timestamp', 'type', 'amount', 'from', 'to']))

    def __init__(self, header):
        super().__init__(header)

    def timestamp(self, record):
        return self.make_timestamp(self.get_value_from_record(record, 'timestamp'), '%b %d %Y')

    def amount(self, record):
        return self.get_value_from_record(record, 'amount')


class Bank2Reader(BaseCsvReader):
    known_columns = tuple(sorted(['amounts', 'date', 'from', 'to', 'transaction']))

    def __init__(self, header):
        super().__init__(header)

    def type(self, record):
        return self.get_value_from_record(record, 'transaction')

    def timestamp(self, record):
        return self.make_timestamp(self.get_value_from_record(record, 'date'), '%d-%m-%Y')

    def amount(self, record):
        return self.get_value_from_record(record, 'amounts')


class Bank3Reader(BaseCsvReader):
    known_columns = tuple(sorted(['cents', 'date_readable', 'euro', 'from', 'to', 'type']))

    def __init__(self, header):
        super().__init__(header)

    def timestamp(self, record):
        return self.make_timestamp(self.get_value_from_record(record, 'date_readable'), '%d %b %Y')

    def amount(self, record):
        euro = Decimal(self.get_value_from_record(record, 'euro'))
        cents = Decimal(self.get_value_from_record(record, 'cents')) / 100
        value = euro + cents
        return str(value)
