#!/usr/bin/env python3

""" builtin_configs.py:

    Default configuration files used as reference """

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


# Configure build manager to build several combinations
config_AN521 = {"platform": ["AN521"],
                "compiler": ["GNUARM"],
                "config": ["ConfigRegression",
                           "ConfigDefault"],
                "build": ["Debug"],
                "with_mcuboot": [True],
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

_builtin_configs = {"AN521_gnuarm_Config_DRC": config_AN521}

if __name__ == '__main__':
    import os
    import sys
    try:
        from tfm_ci_pylib.utils import export_config_map
    except ImportError:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(os.path.join(dir_path, "../"))
        from tfm_ci_pylib.utils import export_config_map

    if len(sys.argv) == 2:
        if sys.argv[1] == "--export":
            export_config_map(_builtin_configs)
    if len(sys.argv) == 3:
        if sys.argv[1] == "--export":
            export_config_map(_builtin_configs, sys.argv[2])
