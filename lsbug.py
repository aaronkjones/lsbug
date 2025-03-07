#!/usr/bin/env python3

# Copyright (c) 2022, Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from src import meta, data, utils


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='lsbug')
    parser.add_argument('-l', '--list', action='store_true', help='List all test cases and their descriptions.')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on the debugging output.')
    parser.add_argument('-x', '--exclude', action='append',
                        help='Exclude test cases by a number or range. It can be specified multiple times.')
    parser.add_argument('-t', '--timeout', help='number of seconds before killing the test run.')
    parser.add_argument('test_cases', nargs='*', default=0,
                        help=('Trigger test cases by numbers. They can be specified multiple times and used as a range,'
                              ' e.g., 0-3'))

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list:
        data.Mapping.show_all()
        return

    watchdog = meta.Watchdog()
    test_run = meta.TestRun()
    if args.timeout:
        watchdog.register(test_run)

    tc_allow = []
    if args.test_cases:
        tc_allow = args.test_cases

    tc_deny = []
    if args.exclude:
        tc_deny = args.exclude

    test_list = utils.merge_ranges(deny=tc_deny, allow=tc_allow)
    test_run.run()
    for test_num in test_list:
        # We will need Python 3.8+ here.
        if not (test_case := data.Mapping.get_test_case(test_num)):
            continue

        print(f'- Start test case: {test_case.name}.')
        tc_watchdog = meta.Watchdog()
        tc_watchdog.register(test_case)
        test_case.setup(tc_watchdog)
        test_case.run(tc_watchdog)
        test_case.cleanup(tc_watchdog)
        tc_watchdog.unregister(test_case)
        print(f'- Finish test case: {test_case.name}')

    if args.timeout:
        watchdog.unregister(test_run)


if __name__ == '__main__':
    main()
