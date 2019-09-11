import shutil

from icondbtools.command.command import Command


class CommandClear(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'clear'
        desc = 'Remove .score and .statedb'

        # create the parser for clear
        parser_clear = sub_parser.add_parser(name, help= desc)
        parser_clear.set_defaults(func=self.run)

    def run(self, args):
        """Clear .score and .statedb

        :param args:
        :return:
        """
        paths = ['.score', '.statedb']
        for path in paths:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass

