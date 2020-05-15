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
__version__ = "1.1"

import os
import sys
import time
import argparse
import datetime
from build_helper_configs import _builtin_configs

try:
    from tfm_ci_pylib.utils import get_cmd_args
    from tfm_ci_pylib.tfm_build_manager import TFM_Build_Manager
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.utils import get_cmd_args, load_json
    from tfm_ci_pylib.tfm_build_manager import TFM_Build_Manager


def build(tfm_dir,
          build_dir,
          buid_report_f,
          build_config,
          parallel_builds=3,
          build_threads=3,
          build_install=True,
          image_sizes=False,
          relative_paths=False):
    """ Instantiate a build manager class and build all configurations """

    start_time = time.time()
    print("relative_paths %s done \r\n" % relative_paths)

    bm = TFM_Build_Manager(tfm_dir=tfm_dir,
                           work_dir=build_dir,
                           cfg_dict=build_config,
                           report=buid_report_f,
                           parallel_builds=parallel_builds,
                           build_threads=build_threads,
                           install=build_install,
                           img_sizes=image_sizes,
                           relative_paths=relative_paths)
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
    elif user_args.config:
        if user_args.config in _builtin_configs.keys():
            build_config = _builtin_configs[user_args.config.lower()]
            print("main %s done \r\n" % build_config)
        else:
            print("Configuration %s is not defined in built-in configs" %
                  user_args.config)
            sys.exit(1)
    else:
        print("Error: Configuration not specificed")
        sys.exit(1)

    # Build everything
    build_status, build_report = build(user_args.tfm_dir,
                                       user_args.build_dir,
                                       #user_args.report,
                                       "summary_" + user_args.config.lower() + ".json",
                                       build_config,
                                       os.cpu_count(),
                                       user_args.thread_no,
                                       user_args.install,
                                       user_args.image_sizes,
                                       user_args.relative_paths)

    if not build_report:
        print("Build Report Empty, check build status")
        sys.exit(1)

    if build_status:
        print("Build Failed")
        if user_args.eif:
            sys.exit(1)
    # pprint(build_report)
    print("Build Helper Quitting!")
    sys.exit(0)


if __name__ == "__main__":

    # Calculate the workspace root directory relative to the script location
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
    parser.add_argument("-c", "--config",
                        dest="config",
                        action="store",
                        help="Which of the built-in configs to run."
                             "(%s)" % "/ ".join(_builtin_configs.keys()))
    parser.add_argument("-e", "--error_if_failed",
                        dest="eif",
                        action="store_true",
                        help="If set will change the script exit code if one "
                              "or more builds fail")
    parser.add_argument("-f", "--config_file",
                        dest="config_f",
                        action="store",
                        help="Manual configuration override file (JSON)")
    parser.add_argument("-r", "--report",
                        dest="report",
                        action="store",
                        help="JSON file containing build report")
    parser.add_argument("-i", "--install",
                        dest="install",
                        action="store_true",
                        help="Run make install after building config")
    parser.add_argument("-t", "--tfm_dir",
                        dest="tfm_dir",
                        action="store",
                        default=os.path.join(root_path, "tf-m"),
                        help="TFM directory")
    parser.add_argument("-s", "--image-sizes",
                        dest="image_sizes",
                        action="store_true",
                        help="Run arm-none-eabi-size to axf files "
                             "generated by build")
    parser.add_argument("-l", "--relative-paths",
                        dest="relative_paths",
                        action="store_true",
                        help="When set paths stored in report will be stored"
                             "in a relative path to the execution directory."
                             "Recommended for Jenkins Builds.")
    parser.add_argument("-p", "--parallel-builds",
                        type=int,
                        dest="parallel_builds",
                        action="store",
                        default=3,
                        help="Number of builds jobs to run in parallel.")
    parser.add_argument("-n", "--number-of-threads",
                        type=int,
                        dest="thread_no",
                        action="store",
                        default=3,
                        help="Number of threads to use per build job.")
    main(get_cmd_args(parser=parser))
