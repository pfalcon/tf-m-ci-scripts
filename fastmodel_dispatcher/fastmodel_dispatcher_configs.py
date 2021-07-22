#!/usr/bin/env python3

""" run_fvp_configs.py:

    Using Python clas inheritance model to generate modular and easily to scale
    configuration models for the run_fpv module. Configuration data is also
    combined with helper methods. If the file is run as a standalone file,
    it can save json configuration files to disk if requested by --export
    directive """

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

import sys
from AN521 import AN521
from AN519 import AN519

fvp_config_map = AN521 + AN519

if __name__ == "__main__":
    # Create Json configuration files on user request

    if len(sys.argv) >= 2:
        if sys.argv[1] == "--export":

            for platform in fvp_config_map.get_object_map().values():
                for config in platform.values():
                    config.json_to_file()
