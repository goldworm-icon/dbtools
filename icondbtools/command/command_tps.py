from icondbtools.command.command import Command
from icondbtools.libs.tps_calculator import TPSCalculator


class CommandTps(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'tps'
        desc = 'Calculate tps based on confirmed transactions that a specific range of blocks contain.'

        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument('--start', type=int, default=0, required=False)
        parser.add_argument('--end', type=int, default=-1, required=False)
        parser.add_argument('--span', type=int, default=-1, required=False, help="unit: second")
        parser.set_defaults(func=self.run)

    def run(self, args):
        """Calculate tps for confirmed transactions in blockchain
        TPS = # of confirmed txs between start block and end block / (end block timestamp - start block timestamp)

        :param args:
        :return:
        """
        db_path: str = args.db
        start: int = args.start
        end: int = args.end
        span_us: int = args.span * 10 ** 6

        calculator = TPSCalculator()
        try:
            calculator.open(db_path)
            calculator.run(start, end, span_us)
        finally:
            calculator.close()

