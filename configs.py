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
from build_helper.build_helper_configs import _builtin_configs


__copyright__ = """
/*
 * Copyright (c) 2020-2022, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """


def get_build_manager(group=None):
    """Get a TFM_Build_Manager instance, silencing stdout"""
    if not group:
        print("No config group selected!")
        return
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
    return build_manager.get_config()


def print_build_configs(config, group=None, silence_stderr=False):
    """Prints particular configuration environment variables"""
    build_manager = get_build_manager(group)
    params = build_manager.get_build_configs(config, silence_stderr=silence_stderr)
    for name in params:
        print("{}={}".format(name, params[name]))


def print_build_commands(config, cmd_type, group=None, jobs=None):
    """Prints particular commands to be run"""
    build_manager = get_build_manager(group)
    cmd = build_manager.get_build_commands(config, silence_stderr=True, jobs=jobs)
    print(cmd[cmd_type])


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
        "-b",
        "--build_commands",
        default=None,
        choices=['set_compiler', 'spe_cmake_config', 'nspe_cmake_config', 'spe_cmake_build', 'nspe_cmake_build', 'post_build'],
        help="Print selected type of build commands to be run for current configuration."
    )
    PARSER.add_argument(
        "--config_params",
        default=None,
        action='store_true',
        help="List config parameters of current configuration."
    )
    PARSER.add_argument(
        "-g",
        "--group",
        default=[],
        action="append",
        help="Only list configurations under a certain group. "
        "'all' will look through all configurations. "
        "Leaving blank will just look at config 'all'.",
        choices=list(_builtin_configs.keys())+['all'],
    )
    PARSER.add_argument(
        "-j",
        "--jobs",
        help="Pass -j option down to the build system (# of parallel jobs)."
    )
    ARGS = PARSER.parse_args()
    if not ARGS.group or ARGS.group == ['all']:
        ARGS.group = list(_builtin_configs.keys())

    all_configs = set()
    for group in ARGS.group:
        # By default print available configs
        if not ARGS.config:
            all_configs.update(list_configs(group))
        else:
            try:
                if ARGS.config_params:
                    print_build_configs(ARGS.config, group=group, silence_stderr=True)
                    break
                if ARGS.build_commands:
                    print_build_commands(ARGS.config, ARGS.build_commands, group=group, jobs=ARGS.jobs)
                    break
            except (SystemExit, KeyError):
                if group == ARGS.group[-1] or ARGS.group == []:
                    print(
                        "Could not find configuration {} in groups {}".format(
                            ARGS.config, ARGS.group
                        )
                    )

    for config in all_configs:
        print(config)
