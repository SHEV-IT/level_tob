# coding: utf-8
import commands
import os
import sys
import logging
import signal
from helpers.vk.bot import VkBot
import constants as c

# debug
if c.DEBUG:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
    )


def stop_if_already_running():
    script_name = __file__
    l = commands.getstatusoutput(
        "ps aux | grep -e '%s' | grep -v grep | awk '{print $2}'| awk '{print $2}'" % script_name)
    if l[1].strip():
        logging.info('init: already running')
        os._exit(0)


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


def main():
    stop_if_already_running()

    signal.signal(signal.SIGINT, signal_handler)
    bots.append(VkBot())
    run_bots()

    logging.info(bots)

    if c.DEBUG:
        print('press ctrl+c to exit...')

    signal.pause()


if __name__ == '__main__':
    main()
