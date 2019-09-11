from abc import ABC, abstractmethod


class Command(ABC):

    @abstractmethod
    def add_parser(self, sub_parser, common_parser):
        pass

    @abstractmethod
    def run(self, args):
        pass
