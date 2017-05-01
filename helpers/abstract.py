# coding: utf-8
from abc import ABCMeta, abstractmethod


class BotFather:
    __metaclass__ = ABCMeta

    def __init__(self, token=None):
        self.token = token

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass