from icondbtools.command.command import Command
from icondbtools.libs.invalid_transaction_checker import InvalidTransactionChecker


class CommandInvalidTx(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'invalidtx'
        desc = 'Check whether invalid transaction are present or not'

        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument('--start', type=int, default=1, required=False)
        parser.add_argument('--end', type=int, default=-1, required=False)
        parser.set_defaults(func=self.run)

    def run(self, args):
        """Check whether invalid transaction are present or not
        for example transactions that are processed without any fees

        :param args:
        :return:
        """
        db_path: str = args.db
        start: int = args.start
        end: int = args.end

        checker = InvalidTransactionChecker()
        try:
            checker.open(db_path)
            checker.run(start, end)
        finally:
            checker.close()