# coding: utf-8
from abc import ABCMeta, abstractmethod


class Bot:
    __metaclass__ = ABCMeta

    def __init__(self, queue, *args, **kwargs):
        self.stop = False
        self.queue = queue

    def worker(self):
        while not self.stop:
            msg = self.queue.get()
            if msg['event'] != 'stop':
                self.proceed(msg)

    @abstractmethod
    def proceed(self, msg):
        pass
