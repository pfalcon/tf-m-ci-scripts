#!/usr/bin/env python3

from __future__ import print_function

"""
Script for submitting multiple LAVA definitions
"""

__copyright__ = """
/*
 * Copyright (c) 2020-2022, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

import glob
import argparse
import logging
from lava_helper import test_lava_dispatch_credentials


_log = logging.getLogger("lavaci")


def list_files_from_dir(user_args, job_dir=""):
    if job_dir == "":
        job_dir = user_args.job_dir
    file_list = []
    resubmit_log = ""
    if job_dir == "failed_jobs":
        resubmit_log = "Resubmit for double check."
    for filename in glob.iglob(job_dir + '**/*.yaml', recursive=True):
        file_list.append(filename)
        _log.info("Found job {file}. {extra_log}".format(file=filename, extra_log=resubmit_log))
    return file_list


def submit_lava_jobs(user_args, job_dir=""):
    """ Submit a job to LAVA backend, block untill it is completed, and
    fetch the results files if successful. If not, calls sys exit with 1
    return code """

    if job_dir == "":
        job_dir = user_args.job_dir

    lava = test_lava_dispatch_credentials(user_args)
    file_list = list_files_from_dir(user_args, job_dir)
    job_id_list = []
    for job_file in file_list:
        job_id, job_url = lava.submit_job(job_file)

        # The reason of failure will be reported to user by LAVA_RPC_connector
        if job_id is None and job_url is None:
            _log.info("Job failed")
        else:
            _log.info("Job submitted at: " + job_url)
            job_id_list.append(job_id)

    return job_id_list


def main(user_args):
    job_id_list = submit_lava_jobs(user_args)
    print("JOBS: {}".format(",".join(str(x) for x in job_id_list)))


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
