from icondbtools.command.command import Command
from icondbtools.libs.block_database_reader import BlockDatabaseReader


class CommandTxResult(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'txresult'
        desc = 'Extract the transaction result indicated by transaction hash from block db and print it'

        # create the parser for txresult
        parser_block = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_block.add_argument(
            '--hash', dest='tx_hash', help='tx hash without "0x" prefix', required=True)
        parser_block.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        tx_hash: str = args.tx_hash

        block_reader = BlockDatabaseReader()
        block_reader.open(db_path)
        tx_result: dict = block_reader.get_transaction_result_by_hash(tx_hash)
        block_reader.close()

        print(tx_result)
