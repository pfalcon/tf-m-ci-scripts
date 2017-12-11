#!/usr/bin/env python3

""" build_helper.py:

    Build helper instantiates a build manager with user provided arguments,
    or default ones.
     """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2019, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """
__author__ = "Minos Galanakis"
__email__ = "minos.galanakis@linaro.org"
__project__ = "Trusted Firmware-M Open CI"
__status__ = "stable"
__version__ = "1.0"

import os
import sys
import time
import argparse
import datetime
from build_helper_configs import config_AN521

try:
    from tfm_ci_pylib.utils import get_cmd_args, load_json
    from tfm_ci_pylib.tfm_build_manager import TFM_Build_Manager
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.utils import get_cmd_args, load_json
    from tfm_ci_pylib.tfm_build_manager import TFM_Build_Manager


def build(tfm_dir, build_dir, buid_report_f, build_config):
    """ Instantiate a build manager class and build all configurations """

    start_time = time.time()

    bm = TFM_Build_Manager(tfm_dir=tfm_dir,
                           work_dir=build_dir,
                           cfg_dict=build_config,
                           report=buid_report_f,
                           install=True)
    bm.start()
    bm.join()
    build_report = bm.get_report()
    elapsed = time.time() - start_time
    elapsed = str(datetime.timedelta(seconds=elapsed))
    print("=============== Time Elapsed: %s ===================" % elapsed)
    return bm.get_status(), build_report


def main(user_args):
    """ Main logic """

    if user_args.config_f:
        try:
            build_config = load_json(user_args.config_f)
        except Exception as e:
            print("Failed to load config %s. Exception: %s" % (build_config,
                                                               e.msg))
            sys.exit(1)
    else:
        build_config = config_AN521
    # Build everything
    build_status, build_report = build(user_args.tfm_dir,
                                       user_args.build_dir,
                                       user_args.report,
                                       build_config)

    if not build_report:
        print("Build Report Empty, check build status")
        sys.exit(1)

    if build_status:
        print("Build Failed")
        sys.exit(1)
    # pprint(build_report)
    print("Build Complete!")
    sys.exit(0)


if __name__ == "__main__":

    # Calcuate the workspace root directory relative to the script location
    # Equivalent to realpath $(dirname ./build_helper/build_helper.py)/../../
    root_path = os.path.dirname(os.path.realpath(__file__))
    for i in range(2):
        root_path = os.path.split(root_path)[0]

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-b", "--build_dir",
                        dest="build_dir",
                        action="store",
                        default="./builds",
                        help="Where to generate the artifacts")
    parser.add_argument("-c", "--config_file",
                        dest="config_f",
                        action="store",
                        help="Manual configuration override file (JSON)")
    parser.add_argument("-r", "--report",
                        dest="report",
                        action="store",
                        help="JSON file containing build report")
    parser.add_argument("-t", "--tfm_dir",
                        dest="tfm_dir",
                        action="store",
                        default=os.path.join(root_path, "tf-m"),
                        help="TFM directory")

    main(get_cmd_args(parser=parser))
