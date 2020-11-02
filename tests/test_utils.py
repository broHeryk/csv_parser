from unittest import TestCase, mock

from testfixtures import tempdir

from utils import *


class TestUtils(TestCase):
    @tempdir()
    def test_get_csv_files_for_empty_folder(self, temp_dir):
        # Given: Path to empty folder
        temp_dir.path
        # When: get csv is called for the path
        files = list(get_csv_files(temp_dir.path))
        # Then: no files is returned
        assert 0 == len(files)

    @tempdir()
    def test_get_csv_files_for_non_empty_folder_without_csv(self, temp_dir):
        # Given: Path to folder with no csv files
        temp_dir.write('test.txt', b'some thing')
        # When: get csv is called for the path
        files = list(get_csv_files(temp_dir.path))
        # Then: no files is returned
        assert 0 == len(files)

    @tempdir()
    def test_get_csv_files_for_folder_with_csvs(self, temp_dir):
        # Given: Path to folder with 2 csv
        temp_dir.write('test1.csv', b'some thing')
        temp_dir.write('test2.csv', b'some thing')
        # When: get csv is called for the path
        files = list(get_csv_files(temp_dir.path))
        # Then: 2 files are returned
        assert 2 == len(files)

    def test_get_csv_files_for_non_existing_folder(self):
        # Given: Path to folder with 2 csv
        path = 'fake/path'
        # When: get csv is called for the path
        # Then: File not found is raised by function
        self.assertRaises(FileNotFoundError, list, get_csv_files(path))

    def test_match_reader_for_unknown_set_of_columns(self):
        # Given: Unknown list of columns for existing readers
        mocked_csv_reader = (el for el in [('1', '2',)])
        # When: When match_reader is called fot the unknown columns
        self.assertRaises(KeyError, match_reader, mocked_csv_reader)

    def test_match_reader_for_valid_set_of_columns(self):
        # Given: Valid list of columns for existing readers
        header_line = ('col1', 'col2', 'col3',)
        # Given: Existing reader for the list of columns
        mocked_reader_class = mock.MagicMock()
        expected_reader_instance = 'test_something'
        mocked_reader_class.return_value = expected_reader_instance
        columns_to_class_map[header_line] = mocked_reader_class
        mocked_csv_reader = (el for el in [header_line])
        # When: When match_reader is called fot the valid columns
        instance = match_reader(mocked_csv_reader)
        # Then: Reader instance is initialized with expected header
        mocked_reader_class.assert_called_once_with(header=header_line)
        # Then: Expected instance is returned
        assert instance == expected_reader_instance

    # TODO: additional cases might be added here
    def test_get_transactions_from_file(self):
        # Given: Test file with valid data
        test_file_path = 'tests/fixtures/test.csv'
        # When: get_transactions_from_file is called for test file
        transactions = get_transactions_from_file(test_file_path)
        # Then: Two records is returned
        assert len(transactions) == 2

    def test_write_transactions_call_each_writer(self):
        # Given: A list or writers
        first_writer = mock.MagicMock()
        second_writer = mock.MagicMock()
        third_writer = mock.MagicMock()
        writers = [first_writer, second_writer, third_writer]
        # Given: A transactions to write
        transactions = [1, 2]
        # When: Write transactions is called
        write_transactions(transactions=transactions, writers=writers)
        # Than: Each writer is called with the same list of transactions
        for wr in writers:
            wr.write.asssert_called_once_with(transactions)

    def test_write_transactions_keep_writing_if_one_writer_is_failed(self):
        # Given: A list or writers
        first_writer = mock.MagicMock()
        first_writer.write.side_effect = [Exception('something went wrong')]
        second_writer = mock.MagicMock()
        writers = [first_writer, second_writer]
        # Given: A transactions to write
        transactions = [1, 2]
        # When: Write transactions is called
        write_transactions(transactions=transactions, writers=writers)
        # Than: Exception is handled and second writer is called despite error
        second_writer.write.assert_called_once_with(transactions)
