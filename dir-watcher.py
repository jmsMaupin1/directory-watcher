#!/usr/bin/env python
__author__ = 'jmsMaupin1'

import time
import argparse
import signal
import logging
import os
from datetime import datetime as dt

exit_flag = False
logger = logging.getLogger(__name__)

sig_dict = dict(
    (k, v) for v, k in reversed(sorted(signal.__dict__.items()))
    if v.startswith('SIG') and not v.startswith('SIG_')
)


def signal_watcher(sig_num, frame):
    logger.warn('Received OS process signal: ' + sig_dict[sig_num])
    global exit_flag
    exit_flag = True


def watch_dir(path, magic_string, ext, interval):
    while not exit_flag:
        print(os.listdir(path))
        time.sleep(interval)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', help='polling interval')
    parser.add_argument('-e', '--extension', help='extension to watch')
    parser.add_argument('dir', help='directory to watch')
    parser.add_argument('string', help='string to watch')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    signal.signal(signal.SIGINT, signal_watcher)
    signal.signal(signal.SIGTERM, signal_watcher)

    if not args:
        parser.print_usage()
        exit(1)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(process)d - %(levelname)s - %(message)s'
    )

    app_start_time = dt.now()

    logging.info(
        '\n'
        '--------------------------------------------------\n'
        '      Running: {}\n'
        '      started on: {}\n'
        '--------------------------------------------------\n'
        .format(__file__, app_start_time.isoformat())
    )

    watch_dir('./', 'test', '.txt', 5)

    uptime = dt.now() - app_start_time

    logging.info(
        '\n'
        '--------------------------------------------------\n'
        '      Running: {}\n'
        '      stopped on: {}\n'
        '--------------------------------------------------\n'
        .format(__file__, str(uptime))
    )
    logging.shutdown()
    return 0


if __name__ == '__main__':
    main()
