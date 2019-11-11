import json

import plyvel

from icondbtools.command.command import Command
from icondbtools.libs.block_database_raw_reader import BlockDatabaseRawReader


class CommandCopy(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'copy'
        desc = 'Copy Loopchain blocks from start height and end height to target DB path'

        parser_copy = sub_parser.add_parser(name, parents=[common_parser], help=desc)

        parser_copy.add_argument('-s', '--start', type=int, default=-1, help='start block height to be copied')
        parser_copy.add_argument('--end', type=int, default=-1, help='end block height to be copied, inclusive')
        parser_copy.add_argument('--count', type=int, default=-1, help='block count to be copied')
        parser_copy.add_argument('--new-db', type=str, default="", help='new DB path for blocks to be copied')
        parser_copy.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        start: int = args.start
        end: int = args.end
        count: int = args.count
        new_db_path: str = args.new_db

        if end > -1:
            if end < start:
                raise ValueError(f'end({end} < start({start})')
            count = max(count, end - start + 1)
        elif count == -1:
            count = 999999999

        block_reader = BlockDatabaseRawReader()
        block_reader.open(db_path)

        new_db = plyvel.DB(new_db_path, create_if_missing=True)

        with new_db.write_batch() as wb:
            for height in range(start, start + count):
                block_height_key: bytes = block_reader.get_block_height_key(height)
                block: bytes = block_reader.get_block_by_height(height)

                if block is None:
                    break

                block_hash: bytes = json.loads(block)["block_hash"].encode()
                wb.put(block_hash, block)
                wb.put(block_height_key, block_hash)

        block_reader.close()