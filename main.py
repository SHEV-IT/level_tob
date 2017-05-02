# coding: utf-8
import commands
import os
import sys
import logging
import signal
from single_process import single_process
from helpers.vk.bot import VkBot
import constants as c

# debug
if c.DEBUG:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
    )


def run_bots():
    for bot in bots:
        logging.info('running %s...' % bot.__class__.__name__)
        bot.run()


def stop_bots():
    logging.info('stopping bots...')
    for bot in bots:
        logging.info('stopping %s...' % bot.__class__.__name__)
        bot.stop()


def signal_handler(signal, frame):
    logging.info('exiting...')
    stop_bots()
    os._exit(0)


bots = []
logging.info('start process')


@single_process
def main():
    signal.signal(signal.SIGINT, signal_handler)
    bots.append(VkBot())
    run_bots()

    logging.info(bots)

    if c.DEBUG:
        print('press ctrl+c to exit...')

    signal.pause()


if __name__ == '__main__':
    main()
