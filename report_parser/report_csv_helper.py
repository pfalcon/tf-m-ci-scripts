#!/usr/bin/env python3

__copyright__ = """
/*
 * Copyright (c) 2022, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

"""
Script to create report summary CSV file.
"""

import csv
import argparse


def get_extra_config_name(extra_param):
    return extra_param.replace(', ', '_') if extra_param != 'N.A' else ' Default'


def generate_headers(config_results):

    # Keys: [CONFIG_NAME, TFM_PLATFORM, COMPILER, LIB_MODEL, ISOLATION_LEVEL, TEST_REGRESSION,
    # TEST_PSA_API, CMAKE_BUILD_TYPE, BL2, PROFILE, EXTRA_PARAMS, RESULT]

    common_params = list(config_results[0].keys())[1:-2]
    extra_params = set()

    for config in config_results:
        extra_params.add(get_extra_config_name(config['EXTRA_PARAMS']))

    csv_headers = common_params + sorted(list(extra_params))
    return csv_headers


def generate_result_rows(config_results):
    for config in config_results:
        config[get_extra_config_name(config['EXTRA_PARAMS'])] = config['RESULT']
    return sorted(config_results, key = lambda x: x['TFM_PLATFORM'])


def main(user_args):
    with open(user_args.input_file, newline='') as csvfile:
        config_results = csv.DictReader(csvfile)
        config_results = [dict(config) for config in config_results]
    csv_headers = generate_headers(config_results)
    with open(user_args.output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers, restval='', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(generate_result_rows(config_results))


def get_cmd_args():
    """Parse command line arguments"""

    # Parse command line arguments to override config
    parser = argparse.ArgumentParser(description="Create CSV report file")
    cmdargs = parser.add_argument_group("Create CSV file")

    # Configuration control
    cmdargs.add_argument(
        "--input-file",
        dest="input_file",
        action="store",
        help="Build or test result of the config",
    )
    cmdargs.add_argument(
        "--output-file",
        dest="output_file",
        action="store",
        help="File name of CSV report",
    )

    return parser.parse_args()

if __name__ == "__main__":
    main(get_cmd_args())
