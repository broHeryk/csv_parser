from collections import namedtuple

transaction_fields = ['timestamp', 'type', 'amount', 'sender', 'recipient']
Transaction = namedtuple('Transaction', transaction_fields)
input_path = 'input_files/'
output_path = 'output_files'
