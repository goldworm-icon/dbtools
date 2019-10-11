import os
import re
from time import sleep
from concurrent.futures import ThreadPoolExecutor


class WordDetector:

    def __init__(self, filename, block_word, release_word):

        self.filename = filename
        self.block_word = re.compile(block_word)
        self.release_word = re.compile(release_word)
        self.hold = False
        self.thread = ThreadPoolExecutor(1)

    def _find_word_from_latest_offset(self):

        offset = 0
        while True:
            with open(self.filename, mode='r', encoding='utf-8') as f:
                if offset == 0:
                    f.seek(0, os.SEEK_END)
                    start_offset = max(0, f.tell() - 500)

                    f.seek(start_offset, os.SEEK_SET)

                else:
                    f.seek(offset)

                sentences = f.readlines()
                for sentence in sentences:
                    if len(self.block_word.findall(sentence)) > 0:
                        self.hold = True
                    elif len(self.release_word.findall(sentence)) > 0:
                        self.hold = False
                        self.stop()

                offset = f.tell()

            sleep(0.4)

    def get_hold(self):
        return self.hold

    def start(self):
        self.thread.submit(self._find_word_from_latest_offset)

    def stop(self):
        self.thread.shutdown()
