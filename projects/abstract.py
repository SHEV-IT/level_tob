# coding: utf-8
from abc import ABCMeta, abstractmethod
from Queue import Empty


class Bot:
    __metaclass__ = ABCMeta

    def __init__(self, queue, *args, **kwargs):
        self.stop = False
        self.queue = queue

    def worker(self):
        while not self.stop:
            try:
                msg = self.queue.get(False, 1)
                self.proceed(msg)
            except Empty:
                pass

    @abstractmethod
    def proceed(self, msg):
        pass


def load_module(module_name, globals_):
    level = 0
    for ch in module_name:
        if ch != ".":
            break
        level += 1
    return __import__(module_name[level:], globals_, locals(), ["*"], level)
