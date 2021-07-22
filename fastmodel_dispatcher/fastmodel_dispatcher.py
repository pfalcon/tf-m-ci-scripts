#!/usr/bin/env python3

""" fvp_dispatcher.py:

    Fastmodel dispatcher takes an build report input from build_helper and
    selects the appropriate tests, lauched in separate fastmodel Wrapper
    instances """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2020, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

__author__ = "tf-m@lists.trustedfirmware.org"
__project__ = "Trusted Firmware-M Open CI"
__version__ = "1.4.0"

import os
import sys
import argparse
from copy import deepcopy
from fastmodel_dispatcher_configs import fvp_config_map

try:
    from tfm_ci_pylib.utils import load_json, print_test, save_json, \
        show_progress
    from tfm_ci_pylib.fastmodel_wrapper import FastmodelWrapper
    from tfm_ci_pylib.tfm_build_manager import TFM_Build_Manager

except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.utils import load_json, print_test, save_json, \
        show_progress
    from tfm_ci_pylib.fastmodel_wrapper import FastmodelWrapper
    from tfm_ci_pylib.tfm_build_manager import TFM_Build_Manager


def cfilter(config_list, match):
    """Filter a list of items in _text1_text2_ format and only include
    results who contain the match term between two underscores """

    # Ensure the match has the format of _text_
    match = "_%s_" % match.strip("_")

    return [n for n in config_list if match in n]


def main(user_args):
    """ Main logic """

    test_config_list = None

    if user_args.list_cfg:
        print("Built-in configs:")
        print("\n".join(fvp_config_map.list()))
        sys.exit(0)
    elif user_args.single_cfg:
        try:
            # Try to fetch the config to validate it exists
            fvp_config_map.get_config(user_args.single_cfg)
            test_config_list = [user_args.single_cfg]
        except Exception as e:
            print("Error: %s" % e)
            sys.exit(1)
    elif user_args.build_all:
        test_config_list = fvp_config_map.list()
    # If a build report is provided parse it
    elif user_args.build_report:
        build_report = load_json(user_args.build_report)

        build_cfg = build_report["_metadata_"]["input_build_cfg"]

        # build and test configs share common key name enties
        config_list = list(map(str.lower,
                               (map(str, build_report["report"].keys()))))
        print("zss config_list %s" % config_list)

        # Only choose the tests that have been defined in the map
        test_config_list = [n for n in fvp_config_map.list()
                            if n in config_list]
        print("zss test_config_list original %s" % test_config_list)

        # Use the Build manager to calcuate the rejection list in the same
        # manner.
        rj = TFM_Build_Manager.generate_rejection_list(
            build_cfg["seed_params"],
            build_cfg["common_params"],
            fvp_config_map.get_invalid()).keys()

        # Remove every config that is included in the rejection.
        # Ignore generated rejection configs that have not been set in the
        # test map.
        for name in rj:
            name = name.lower()
            try:
                test_config_list.pop(test_config_list.index(name))
                print("Rejecting config %s" % name)
            except Exception as e:
                print("Rejection ignored with exception:", e)
    else:
        print("Noting to do. Please provide a report or a config name to test")
        sys.exit(1)

    # Apply filters if specified by user
    if user_args.build_armclang:
        test_config_list = cfilter(test_config_list, "armclang")
    elif user_args.build_gnuarm:
        test_config_list = cfilter(test_config_list, "gnuarm")
    elif user_args.filter:
        test_config_list = cfilter(test_config_list, user_args.filter)
    else:
        pass

#    print("Working on Test list: \n%s" % "\n".join(sorted(test_config_list)))
 
    if user_args.p_command:

        for test_cfg in test_config_list:

            test_cfg_obj = fvp_config_map.get_config_object(test_cfg)

            _tmp_cfg = FastmodelWrapper(fvp_cfg=test_cfg_obj.get_config())

            print("\nCommand line:")
            print("")
            _tmp_cfg.show_cmd()
            print("\n")
        sys.exit(0)

    # Run tests
    rep = []
    test_count = 0
#    print("zss print_list list")
#    fvp_config_map.print_list()
    print("zss test_config_list", test_config_list)
    for test_cfg in test_config_list:

        # Check if the config hardcoded binary path is same as the one
        # in the build report. If not update the config
        test_cfg_obj = fvp_config_map.get_config_object(test_cfg)
        print("+++test_cfg_obj %s\r\n %s\r\ntest_cfg %s" % (test_cfg_obj, test_cfg_obj.get_config(), test_cfg))

        print("---- test_cfg_obj.get_config()", test_cfg_obj.get_config())
        rep.append(FastmodelWrapper(
                   fvp_cfg=test_cfg_obj.get_config())
                   .start().block_wait().test().save_report().get_report())
        test_count += 1
        print("Testing progress:")
        show_progress(test_count, len(test_config_list))

    # Export the report in a file
    if user_args.report:
        f_report = {"report": {}, "_metadata_": {}}
        f_report["report"] = {k["name"]: deepcopy(k) for k in rep}
        save_json(user_args.report, f_report)

    sl = [x["name"] for x in rep if x["success"] is True]
    fl = [x["name"] for x in rep if x["success"] is False]

    print("\n")

    if sl:
        print_test(t_list=sl, status="passed", tname="Tests")
    if fl:
        print_test(t_list=fl, status="failed", tname="Tests")
        if user_args.eif:
            sys.exit(1)


def get_cmd_args():
    """ Parse command line arguments """

    # Parse command line arguments to override config
    parser = argparse.ArgumentParser(description="TFM Fastmodel wrapper.")
    parser.add_argument("-b", "--build_report",
                        dest="build_report",
                        action="store",
                        help="JSON file produced by build_helper (input)")
    parser.add_argument("-a", "--build_all",
                        dest="build_all",
                        action="store_true",
                        help="If set build every configuration combination")
    parser.add_argument("-e", "--error_if_failed",
                        dest="eif",
                        action="store_true",
                        help="If set will change the script exit code if one "
                              "or more tests fail")
    parser.add_argument("-r", "--report",
                        dest="report",
                        action="store",
                        help="JSON file containing fastmodel report (output)")
    parser.add_argument("-g", "--build_gnuarm",
                        dest="build_gnuarm",
                        action="store_true",
                        help="If set build every gnuarm configuration")
    parser.add_argument("-c", "--build_armclang",
                        dest="build_armclang",
                        action="store_true",
                        help="If set build every armclang configuration")
    parser.add_argument("-f", "--filter",
                        dest="filter",
                        action="store",
                        help="Only select configs that contain this string")
    parser.add_argument("-l", "--list-configs",
                        dest="list_cfg",
                        action="store_true",
                        help="Print a list of the built-in configurations and"
                             "exit")
    parser.add_argument("-s", "--single-config",
                        dest="single_cfg",
                        action="store",
                        help="Launch testing for a single built-in config,  "
                              "picked by name")
    parser.add_argument("-p", "--print-command",
                        dest="p_command",
                        action="store_true",
                        help="Print the FVP launch command to console & exit")
    return parser.parse_args()


if __name__ == "__main__":
    main(get_cmd_args())
