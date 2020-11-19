#!/usr/bin/env python3

from __future__ import print_function

"""
Script for submitting multiple LAVA definitions
"""

__copyright__ = """
/*
 * Copyright (c) 2020, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

import os
import glob
import sys
import argparse
from lava_helper_configs import *

try:
    from tfm_ci_pylib.utils import (
        save_json,
        load_json,
        sort_dict,
        load_yaml,
        test,
        print_test,
    )
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.utils import (
        save_json,
        load_json,
        sort_dict,
        load_yaml,
        test,
        print_test,
    )
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector


def test_lava_dispatch_credentials(user_args):
    """ Will validate if provided token/credentials are valid. It will return
    a valid connection or exit program if not"""

    # Collect the authentication tokens
    try:
        if user_args.token_from_env:
            usr = os.environ['LAVA_USER']
            secret = os.environ['LAVA_TOKEN']
        elif user_args.lava_token and user_args.lava_user:
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
        print("Did you set set --lava-token, --lava-user?")
        sys.exit(1)
    return lava

def list_files_from_dir(user_args):
    file_list = []
    for filename in glob.iglob(user_args.job_dir + '**/*.yaml', recursive=True):
        file_list.append(filename)
        print("Found job {}".format(filename))
    return file_list

def lava_dispatch(user_args):
    """ Submit a job to LAVA backend, block untill it is completed, and
    fetch the results files if successful. If not, calls sys exit with 1
    return code """

    lava = test_lava_dispatch_credentials(user_args)
    file_list = list_files_from_dir(user_args)
    job_id_list = []
    for job_file in file_list:
        job_id, job_url = lava.submit_job(job_file)

        # The reason of failure will be reported to user by LAVA_RPC_connector
        if job_id is None and job_url is None:
            print("Job failed")
        else:
            print("Job submitted at: " + job_url)
            job_id_list.append(job_id)

    print("JOBS: {}".format(",".join(str(x) for x in job_id_list)))

def main(user_args):
    lava_dispatch(user_args)


def get_cmd_args():
    """ Parse command line arguments """

    # Parse command line arguments to override config
    parser = argparse.ArgumentParser(description="Lava Create Jobs")
    cmdargs = parser.add_argument_group("Create LAVA Jobs")

    # Configuration control
    cmdargs.add_argument(
        "--lava-url", dest="lava_url", action="store", help="LAVA lab URL (without RPC2)"
    )
    cmdargs.add_argument(
        "--job-dir", dest="job_dir", action="store", help="LAVA jobs directory"
    )
    cmdargs.add_argument(
        "--lava-token", dest="lava_token", action="store", help="LAVA auth token"
    )
    cmdargs.add_argument(
        "--lava-user", dest="lava_user", action="store", help="LAVA username"
    )
    cmdargs.add_argument(
        "--use-env", dest="token_from_env", action="store_true", default=False, help="LAVA username"
    )
    cmdargs.add_argument(
        "--lava-timeout", dest="dispatch_timeout", action="store", default=3600, help="LAVA username"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(get_cmd_args())
