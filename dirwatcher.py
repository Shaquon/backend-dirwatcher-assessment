#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
- This is a program that watches a chosen directory and searches
 the text for a "magic" word.
- Log when magic word is found.
"""

__author__ = "Shaquon with help from Piero"

import time
import argparse
import signal
import logging
import os

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)
exit_flag = False
logger = logging.getLogger(__file__)
tracking_dict = {}


def watch_directory(dir_to_watch, file_ext, search_text):
    dir_files = os.listdir(dir_to_watch)
    for file in dir_files:
        if file.endswith(file_ext) and file not in tracking_dict:
            tracking_dict[file] = 0
            logger.info("Now tracking {}".format(file))

    for file in list(tracking_dict):
        if file not in dir_files:
            logger.info("{} removed from watchlist.".format(file))
            del tracking_dict[file]

    for file in tracking_dict:
        tracking_dict[file] = find_magic(
            os.path.join(dir_to_watch, file),
            tracking_dict[file],
            search_text
        )


def find_magic(file, start_pos, magic_word):
    line_number = 0
    with open(file) as f:
        for line_number, line in enumerate(f):
            if line_number >= start_pos:
                if magic_word in line:
                    new_line = line_number + 1
                    logger.info(
                        "{}: found '{}' on line {}".format(
                            file, magic_word, new_line)
                    )
    return line_number+1


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    logger.warn('Received ' + signal.Signals(sig_num).name)
    # log the signal name (the python2 way)
    signames = dict((k, v) for v, k in reversed(
                    sorted(signal.__dict__.items()))
                    if v.startswith('SIG') and not v.startswith('SIG_'))
    logger.warn('Received ' + signames[sig_num])
    global exit_flag
    exit_flag = True


def create_parser():
    """Creates parser and setup cmd line options"""
    parser = argparse.ArgumentParser(
                        description='Watch directory for file changes')
    parser.add_argument("-i", "--interval", default=1,
                        help="polling interval, defaults to 1 second")
    parser.add_argument("-d", "--dir", default=".",
                        help="directory to be watched, defaults to '.'")
    parser.add_argument("-e", "--ext", default='.txt',
                        help="extension to be watched, defaults to .txt")
    parser.add_argument("magic", help="magic word to be found")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start_time = time.time()

    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        '    Running {0}\n'
        '    Started on {1}\n'
        '-------------------------------------------------------------------\n'
        .format(__file__, start_time)
    )
    logger.info(
        'Scanning path: {}, '
        'for files with extension: {},'
        'that contain the magic word: {}'
        .format(args.dir, args.ext, args.magic)
                )

    while not exit_flag:
        try:
            watch_directory(args.dir, args.ext, args.magic)
        except OSError:
            logger.error("Dir not found:".format(watch_directory))
            time.sleep(5.0)
        except Exception as e:
            logger.error('{} Unhandled Exception'.format(str(e)))

        time.sleep(int(args.interval))

    end_time = time.time()

    logger.info(
                '\n'
                '----------------------------------------------------\n'
                'Stopped watching\n'
                'Uptime was ' + str(int(end_time-start_time)) + ' seconds\n'
                '----------------------------------------------------\n'
                )

    logging.shutdown()


if __name__ == '__main__':
    print('file is being run directly')
    main()
else:
    print('file is being imported')
