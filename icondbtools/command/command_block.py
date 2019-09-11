from icondbtools.command.command import Command
from icondbtools.libs.block_database_reader import BlockDatabaseReader


class CommandBlock(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'block'
        desc = 'Print the block indicated by block height'

        # create the parser for block
        parser_block = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_block.add_argument('--height', type=int, default=0, help='start height to sync', required=False)
        parser_block.add_argument('--hash', type=str,
                                  help='blockHash without "0x"\n'
                                  "(ex: e9cad58aae99c1cae85c2545ad33ddb34e8dc4b5e5dd9f363a30cb55e809018e)",
                                  required=False)
        parser_block.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        height: int = args.height
        block_hash: str = args.hash

        block_reader = BlockDatabaseReader()
        block_reader.open(db_path)

        if block_hash is not None:
            block: dict = block_reader.get_block_by_block_hash(block_hash)
        else:
            block: dict = block_reader.get_block_by_block_height(height)
        block_reader.close()

        print(block)


