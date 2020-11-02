import time
from datetime import datetime
from decimal import Decimal
from typing import List

from config import Transaction, transaction_fields


class BaseCsvReader:
    known_columns = tuple()
    timestamp_format = '%b %d %Y'
    timestamp_col_name = 'timestamp'

    def __init__(self, header):
        self.column_index_map = {col: header.index(col) for col in self.known_columns}

    def timestamp(self, record):
        return self.make_timestamp(self.get_value_from_record(record, self.timestamp_col_name), self.timestamp_format)

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
        """
        Transaction is unified output for all csv formats. Csv parser class should have implemented
        getter functions with the same names as attributes in Transaction class. Particular csv parser has
        it's own implementation for getter functions if there is some specific logic for it like
        datetime format or column names or amount calculation.
        """
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
    timestamp_format = '%b %d %Y'
    timestamp_col_name = 'timestamp'

    def __init__(self, header):
        super().__init__(header)

    def amount(self, record):
        return self.get_value_from_record(record, 'amount')


class Bank2Reader(BaseCsvReader):
    known_columns = tuple(sorted(['amounts', 'date', 'from', 'to', 'transaction']))
    timestamp_format = '%d-%m-%Y'
    timestamp_col_name = 'date'

    def __init__(self, header):
        super().__init__(header)

    def type(self, record):
        return self.get_value_from_record(record, 'transaction')

    def amount(self, record):
        return self.get_value_from_record(record, 'amounts')


class Bank3Reader(BaseCsvReader):
    known_columns = tuple(sorted(['cents', 'date_readable', 'euro', 'from', 'to', 'type']))
    timestamp_format = '%d %b %Y'
    timestamp_col_name = 'date_readable'

    def __init__(self, header):
        super().__init__(header)

    def amount(self, record):
        euro = Decimal(self.get_value_from_record(record, 'euro'))
        cents = Decimal(self.get_value_from_record(record, 'cents')) / 100
        value = euro + cents
        return value
