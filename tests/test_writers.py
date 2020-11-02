import csv
import time
from datetime import datetime
from unittest import TestCase

from freezegun import freeze_time
from testfixtures import tempdir

from config import Transaction
from utils import get_csv_files
from writers.writers import CsvWriter


class TestCsvWriter(TestCase):

    def setUp(self):
        transaction_data = {field: f'{field}_value' for field in Transaction._fields}
        self.number_of_rows = 10
        self.valid_transactions = [Transaction(**transaction_data) for _ in range(self.number_of_rows)]

    @tempdir()
    def test_write_with_valid_data(self, temp_dir):
        # Given: Writer is initialized with existing dir
        writer = CsvWriter(temp_dir.path)
        # Given: the folder has no csv files
        assert not list(get_csv_files(temp_dir.path))
        # When: Write is called for the valid list of transactions
        writer.write(transactions=self.valid_transactions)
        # Then: One csv is created in the proper place
        files = list(get_csv_files(temp_dir.path))
        assert len(files) == 1
        with open(files[0], 'r') as f:
            reader = csv.reader(f)
            lines = [row for row in reader]
        # Then: Header is written correctly
        assert tuple(lines[0]) == Transaction._fields
        # Then: Number of rows in file is equal to number of data rows + header line
        assert len(lines) == self.number_of_rows + 1
        # Then: Row is written correctly to the file
        assert [f'{field}_value' for field in Transaction._fields] == lines[1]

    def test_initialize_with_non_existing_dir(self):
        # Given: Path to non existing directory
        path = 'no way'
        # When: Constructor is called for non existing dir
        self.assertRaises(ValueError, CsvWriter, path)

    @freeze_time('2012-01-14')
    @tempdir()
    def test_build_file_path(self, temp_dir):
        # Given: Current date time is frozen so we can track this value
        timestamp = int(time.mktime(datetime.strptime('2012-01-14', '%Y-%m-%d').timetuple()))
        # Given: writer instance
        writer = CsvWriter(temp_dir.path)
        # When: build_file_path is called
        path = writer.build_file_path()
        # Then: Path is built in the expected way using current time
        assert path == f'{temp_dir.path}/{timestamp}.csv'
