from icondbtools.command.command import Command
from icondbtools.libs.state_database_reader import StateDatabaseReader, StateHash


class CommandStateHash(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'statehash'
        desc = 'Generate the sha3_256 hash value from key and value data of leveldb'

        # create the parser for statehash
        parser_state_hash = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_state_hash.add_argument('--prefix', type=str, default=None,
                                       help='Generate a state hash using data of which keys start with a given prefix')
        parser_state_hash.set_defaults(func=self.run)

    def run(self, args):
        """Create hash from state db

        :param args:
        :return:
        """
        db_path: str = args.db
        prefix: str = args.prefix

        reader = StateDatabaseReader()
        reader.open(db_path)

        # convert hex string to bytes
        if prefix is not None:
            if prefix.startswith('0x'):
                prefix = prefix[2:]

            prefix: bytes = bytes.fromhex(prefix)

        state_hash: 'StateHash' = reader.create_state_hash(prefix)
        reader.close()

        print(state_hash)
