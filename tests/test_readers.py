from unittest import TestCase
from unittest import mock
from readers.readers import Bank1Reader, Bank3Reader
from config import transaction_fields, Transaction
from decimal import Decimal


class TestCsvReaders(TestCase):

    def setUp(self):
        self.reader = Bank1Reader(header=['timestamp', 'type', 'amount', 'from', 'to'])
        self.valid_record = ['Oct 1 2019', 'remove', '99.20', '198', '182']

    def test_unify_records_for_empty_csv_reader(self):
        # Given: Csv reader with no records inside
        empty_csv_reader = (r for r in [])
        # When: unify_records is called for empty reader
        records = self.reader.unify_records(empty_csv_reader)
        # Then: Empty list is returned
        assert [] == records

    def test_unify_records_for_valid_csv_reader(self):
        # Given: Csv reader with valid rows inside
        number_of_rows = 3
        empty_csv_reader = (self.valid_record for _ in range(number_of_rows))
        # When: unify_records is called for empty reader
        records = self.reader.unify_records(empty_csv_reader)
        # Then: Expected number of rows is returned
        assert len(records) == number_of_rows

    def test_unify_records_parsing_records_with_mismatching_date_format(self):
        # Given: Csv reader with valid broken
        number_of_rows = 3
        empty_csv_reader = (['invalid_date', 'remove', '99.20', '198', '182'] for _ in range(number_of_rows))
        # When: unify_records is called for empty reader
        records = self.reader.unify_records(empty_csv_reader)
        # Then: Expected number of rows is returned
        assert len(records) == number_of_rows

    def test_timestamp_for_valid_date(self):
        # Given: timestamp value equal to date value
        expected_timestamp = 1569902400
        # When: timestamp function is called for the valid record
        ts = self.reader.timestamp(self.valid_record)
        # Then: Expected timestamp is returned
        assert ts == expected_timestamp

    def test_make_timestamp_for_invalid_date(self):
        # Given: Record with invalid date inside
        record = ['invalid_date', 'remove', '99.20', '198', '182']
        # When: timestamp function is called for the valid record
        ts = self.reader.timestamp(record)
        # Then: -1 is returned as invalid timestamp was passed
        assert ts == -1

    def test_get_transaction_type_parsed_correctly(self):
        # Given: A valid record with specific type
        tr_type = 'some_specific_type'
        record = ['Oct 1 2019', tr_type, '99.20', '198', '182']
        # When: get_transaction is called for the record
        transaction = self.reader.get_transaction(record)
        # Then: Transaction type is parsed correctly into transaction object
        assert transaction.type == tr_type

    def test_get_sender_parsed_correctly(self):
        # Given: A valid record with specific sender
        sender = '1001'
        record = ['Oct 1 2019', 'add', '99.20', sender, '182']
        # When: get_transaction is called for the record
        transaction = self.reader.get_transaction(record)
        # Then: Sender is parsed correctly into transaction object
        assert transaction.sender == sender

    def test_get_recipient_parsed_correctly(self):
        # Given: A valid record with specific recipient
        recipient = '1001'
        record = ['Oct 1 2019', 'add', '99.20', '111', recipient]
        # When: get_transaction is called for the record
        transaction = self.reader.get_transaction(record)
        # Then: Recipient is parsed correctly into transaction object
        assert transaction.recipient == recipient

    def test_get_value_from_record(self):
        # Given: A header with mixed order and Reader instance built on this header
        mixed_header = ['type', 'from', 'timestamp', 'to', 'amount']
        reader = Bank1Reader(header=mixed_header)
        # Given: A record with the same order as header
        tr_type = 'Aaddd'
        recipient = '123'
        sender = '321'
        amount = '300.41'
        timestamp = 'Oct 1 2019'
        expected_timestamp = 1569902400
        # When: Get transaction is called for the record
        transaction = reader.get_transaction([tr_type, sender, timestamp, recipient, amount])
        # Then: values are parsed properly into transaction object despite mixed order
        assert transaction.type == tr_type
        assert transaction.timestamp == expected_timestamp
        assert transaction.amount == amount
        assert transaction.sender == sender
        assert transaction.recipient == recipient

    def test_get_transaction(self):
        # Given: An instance of csv reader
        reader = Bank1Reader(header=['timestamp', 'type', 'amount', 'from', 'to'])
        # Given: Each transaction field function is mocked
        mocks = []
        for field in transaction_fields:
            mocked_func = mock.MagicMock()
            mocked_func.return_value = 1
            setattr(reader, field, mocked_func)
            mocks.append(mocked_func)
        test_record = [1, 2, 3, 4, 5]
        # When: get_transaction is called for the row
        transaction = reader.get_transaction(test_record)
        # Then: Transaction is build of expected values
        assert transaction == Transaction(1, 1, 1, 1, 1)
        # Then: All mock functions is called wit expected input
        for mock_f in mocks:
            mock_f.assert_called_once_with(test_record)

    def test_calculate_specific_amount(self):
        # Given: Bank3 reader with its own header
        reader = Bank3Reader(header=['cents', 'date_readable', 'euro', 'from', 'to', 'type'])
        # Given: record with scattered amount value
        euro = 111
        cents = 50
        expected_amount = Decimal(euro + cents/100)
        record = [cents, 'no_matter', euro, 'no_matter', 'no_matter', 'no_matter']
        # When: amount getter is called for the record
        amount = reader.amount(record=record)
        # Then: amount is calculated correctly
        assert expected_amount == amount
