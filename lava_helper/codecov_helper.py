__copyright__ = """
/*
 * Copyright (c) 2018-2021, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

"""
Module with helper functions for code coverage reports.
"""

import os
import subprocess

from lava_helper import test_lava_dispatch_credentials


def run(cmd, cwd=None):
    print("+ %s" % cmd, flush=True)
    subprocess.check_call(cmd, shell=True, cwd=cwd)


def extract_trace_data(lava_log_fname, job_dir):
    last_fname = None
    f_out = None
    with open(lava_log_fname) as f_in:
        for l in f_in:
            if l.startswith("covtrace-"):
                fname, l = l.split(" ", 1)
                if fname != last_fname:
                    if f_out:
                        f_out.close()
                    f_out = open(job_dir + "/" + fname, "w")
                    last_fname = fname
                f_out.write(l)


def coverage_reports(jobs, user_args):
    lava = test_lava_dispatch_credentials(user_args)
    for job_id, info in jobs.items():
        job_dir = info["job_dir"]
        metadata = info["metadata"]

        if os.getenv("CODE_COVERAGE_EN") == "TRUE" and info["device_type"] == "fvp":

            def dl_artifact(fname):
                lava.fetch_file(
                    metadata["build_job_url"] + "artifact/trusted-firmware-m/build/bin/" + fname,
                    os.path.join(job_dir, fname)
                )

            dl_artifact("bl2.axf")
            dl_artifact("tfm_s.axf")
            dl_artifact("tfm_ns.axf")
            run("python3 $SHARE_FOLDER/qa-tools/coverage-tool/coverage-reporting/intermediate_layer.py --config-json $SHARE_FOLDER/tf-m-ci-scripts/lava_helper/trace2covjson.json --local-workspace $SHARE_FOLDER", cwd=job_dir)
            run("python3 $SHARE_FOLDER/qa-tools/coverage-tool/coverage-reporting/generate_info_file.py --workspace $SHARE_FOLDER --json covjson.json", cwd=job_dir)
            run("lcov -rc lcov_branch_coverage=1 -r coverage.info '*/trusted-firmware-m/platform/*' -o coverage.info.tmp", cwd=job_dir)
            run("mv coverage.info.tmp coverage.info", cwd=job_dir)
            run("genhtml --branch-coverage coverage.info --output-directory trace_report | grep -v -E '^Processing file '", cwd=job_dir)
