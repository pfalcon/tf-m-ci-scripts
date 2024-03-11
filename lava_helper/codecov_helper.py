__copyright__ = """
/*
 * Copyright (c) 2018-2022, Arm Limited. All rights reserved.
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
import logging

from lava_helper import test_lava_dispatch_credentials


_log = logging.getLogger(__name__)


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
                    metadata["build_job_url"] + "artifact/ci_build/" + fname,
                    os.path.join(job_dir, os.path.basename(fname))
                )

            _log.info("Producing coverage report for job %s", job_id)
            dl_artifact("spe/bin/bl2.axf")
            dl_artifact("spe/bin/tfm_s.axf")
            dl_artifact("nspe/bin/tfm_ns.axf")

            script_dir = os.path.dirname(__file__)
            run("python3 $SHARE_FOLDER/qa-tools/coverage-tool/coverage-reporting/intermediate_layer.py --config-json %s/trace2covjson.json --local-workspace $SHARE_FOLDER" % script_dir, cwd=job_dir)
            run("python3 $SHARE_FOLDER/qa-tools/coverage-tool/coverage-reporting/generate_info_file.py --workspace $SHARE_FOLDER --json covjson.json", cwd=job_dir)
            # Remove sources, coverage of which we're not interested in (e.g.
            # 3rd party code).
            run(
                "lcov %s -rc lcov_branch_coverage=1 -r coverage.info "
                "'*/trusted-firmware-m/platform/*' '*/trusted-firmware-m/lib/ext/*' "
                "'*/tf-m-tests/*' '*/mbedtls/*' '*/mcuboot/*' '*/psa-arch-tests/*' "
                "'*/QCBOR/*' -o coverage.info.tmp" % os.getenv("LCOV_FLAGS", ""),
                cwd=job_dir
            )
            run("mv coverage.info.tmp coverage.info", cwd=job_dir)
            run("genhtml --branch-coverage coverage.info --output-directory trace_report | grep -v -E '^Processing file '", cwd=job_dir)
