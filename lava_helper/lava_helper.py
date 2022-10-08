#!/usr/bin/env python3 -u

""" lava_helper.py:

    Provide function to validate LAVA token/credentials. """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2022, Arm Limited. All rights reserved.
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

try:
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector


def test_lava_dispatch_credentials(user_args):
    """ Will validate if provided token/credentials are valid. It will return
    a valid connection or exit program if not"""

    # Collect the authentication tokens
    try:
        if user_args.token_from_env:
            usr = os.environ['LAVA_USER']
            secret = os.environ['LAVA_TOKEN']
        elif user_args.lava_user and user_args.lava_token:
            usr = user_args.lava_user
            secret = user_args.lava_token

        # Do not submit job without complete credentials
        if not len(usr) or not len(secret):
            raise Exception("Credentials not set")

        lava = LAVA_RPC_connector(usr,
                                  secret,
                                  user_args.lava_url)

        # Test the credentials againist the backend
        if not lava.test_credentials():
            raise Exception("Server rejected user authentication")
    except Exception as e:
        print("Credential validation failed with : %s" % e)
        print("Did you set set --lava_user, --lava_token?")
        sys.exit(1)
    return lava
