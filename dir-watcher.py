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
    logger.warn(
        'Received OS process signal: {}'
        .format(sig_dict[sig_num])
    )
    global exit_flag
    exit_flag = True


def find_magic_string(file_name, starting_line, lines, magic_string):
    last_line = starting_line
    for line_num, line in enumerate(lines, starting_line):
        if magic_string in line:
            logger.info(
                'Magic string found in file: {} on line: {}'
                .format(file_name, line_num)
            )
            last_line = line_num

    return last_line


def watch_dir(path, magic_string, ext, interval):
    abs_path = os.path.abspath(path)
    files = {}

    while not exit_flag:
        time.sleep(interval)
        if not os.path.exists(abs_path):
            logger.error('Path {} does not exist'.format(abs_path))
            continue

        for f in os.listdir(abs_path):
            if f not in files and f.endswith(ext):
                logger.info('Now watching file: {}'.format(f))
                files[f] = (0, None)

        for f in files.keys():
            if f not in os.listdir(abs_path):
                logger.info('File {} was removed'.format(f))
                files.pop(f)

        for f in files.keys():
            last_modified = files[f][1]
            start_line = files[f][0]
            file_with_path = abs_path + "/" + f
            if last_modified != os.stat(file_with_path).st_mtime:
                with open(file_with_path) as sf:
                    lines = sf.readlines()
                    if start_line < len(lines):
                        last_line = find_magic_string(
                            file_with_path,
                            start_line + 1,
                            lines[start_line:],
                            magic_string
                        )
                        files[f] = (
                            last_line,
                            os.stat(file_with_path).st_mtime
                        )


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', help='polling interval')
    parser.add_argument('-e', '--extension', help='extension to watch')
    parser.add_argument('dir', help='directory to watch')
    parser.add_argument('magic_string', help='string to watch')
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
        format='%(process)d - %(asctime)s - %(levelname)s - %(message)s',
        datefmt='%y-%m-%d %H:%M:%S'
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

    try:
        watch_dir(
            args.dir,
            args.magic_string,
            args.extension,
            float(args.interval)
        )
    except Exception as e:
        logger.error('Unhandled Exception: {}'.format(e))

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
