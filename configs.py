#!/usr/bin/env python
"""
Script for querying specific build configurations of TF-M.
Can list available build configurations, and can give environment
variables to build a specific build configuration using run-build.sh
"""

import argparse
import os
import sys

from tfm_ci_pylib.tfm_build_manager import TFM_Build_Manager
from build_helper.build_helper_configs import config_full
from build_helper.build_helper_configs import _builtin_configs


__copyright__ = """
/*
 * Copyright (c) 2020, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """


def get_build_manager(group=None):
    """Get a TFM_Build_Manager instance, silencing stdout"""
    config = config_full
    if group:
        config = _builtin_configs[group]
    _dir = os.getcwd()
    # Block default stdout from __init__
    sys.stdout = open(os.devnull, "w")
    build_manager = TFM_Build_Manager(_dir, _dir, config)
    # Allow stdout again
    sys.stdout = sys.__stdout__
    return build_manager


def list_configs(group):
    """Lists available configurations"""
    build_manager = get_build_manager(group)
    build_manager.print_config()


def print_config_environment(config, group=None):
    """Prints particular configuration environment variables"""
    build_manager = get_build_manager(group)
    build_manager.print_config_environment(config)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Extract build configurations.")
    PARSER.add_argument(
        "config",
        default=None,
        nargs="?",
        help="Configuration to print environment variables for. "
        "Then run-build.sh can be run directly with these set. "
        "If not specified, the available configurations are printed",
    )
    PARSER.add_argument(
        "-g",
        "--group",
        default=None,
        help="Only list configurations under a certain group. ",
        choices=list(_builtin_configs.keys()),
    )
    ARGS = PARSER.parse_args()

    # By default print available configs
    if not ARGS.config:
        list_configs(ARGS.group)
    else:
        print_config_environment(ARGS.config, group=ARGS.group)
