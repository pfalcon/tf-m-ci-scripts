#!/usr/bin/env python3

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2020-2021, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

"""
Script for waiting for LAVA jobs and parsing the results
"""

import os
import sys
import time
import yaml
import argparse
import csv
from jinja2 import Environment, FileSystemLoader
from lava_helper_configs import *
from lava_helper import test_lava_dispatch_credentials

try:
    from tfm_ci_pylib.utils import save_json, load_json, sort_dict,\
        load_yaml, test, print_test
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.utils import save_json, load_json, sort_dict,\
        load_yaml, test, print_test
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector

cfgs = ["Default", "CoreIPC", "CoreIPCTfmLevel2", "CoreIPCTfmLevel3",
        "Regression", "RegressionIPC",
        "RegressionIPCTfmLevel2", "RegressionIPCTfmLevel3",
        "DefaultProfileS", "RegressionProfileS",
        "DefaultProfileM", "RegressionProfileM", "RegressionProfileM PSOFF",
        "DefaultProfileL", "RegressionProfileL",
        "PsaApiTest (Attest)", "PsaApiTestIPC (Attest)",
        "PsaApiTestIPCTfmLevel2 (Attest)",
        "PsaApiTest (Crypto)", "PsaApiTestIPC (Crypto)",
        "PsaApiTestIPCTfmLevel2 (Crypto)",
        "PsaApiTest (PS)", "PsaApiTestIPC (PS)",
        "PsaApiTestIPCTfmLevel2 (PS)",
        "PsaApiTest (ITS)", "PsaApiTestIPC (ITS)",
        "PsaApiTestIPCTfmLevel2 (ITS)",
        "PsaApiTestIPC (FF)",
        "PsaApiTestIPCTfmLevel2 (FF)",
        "PsaApiTestIPCTfmLevel3 (ITS)", "PsaApiTestIPCTfmLevel3 (PS)",
        "PsaApiTestIPCTfmLevel3 (Crypto)", "PsaApiTestIPCTfmLevel3 (Attest)",
        "PsaApiTestIPCTfmLevel3 (FF)"]

def wait_for_jobs(user_args):
    job_list = user_args.job_ids.split(",")
    job_list = [int(x) for x in job_list if x != '']
    lava = test_lava_dispatch_credentials(user_args)
    finished_jobs = get_finished_jobs(job_list, user_args, lava)
    print_lava_urls(finished_jobs, user_args)
    job_links(finished_jobs, user_args)
    boot_report(finished_jobs, user_args)
    test_report(finished_jobs, user_args, lava)
    failure_report(finished_jobs, user_args)
    csv_report(finished_jobs)

def get_finished_jobs(job_list, user_args, lava):
    finished_jobs = lava.block_wait_for_jobs(job_list, user_args.dispatch_timeout, 0.5)
    unfinished_jobs = [item for item in job_list if item not in finished_jobs]
    for job in unfinished_jobs:
        info_print("Cancelling unfinished job: {}".format(job))
        lava.cancel_job(job)
    if user_args.artifacts_path:
        for job, info in finished_jobs.items():
            info['job_dir'] = os.path.join(user_args.artifacts_path, "{}_{}".format(str(job), info['description']))
            finished_jobs[job] = info
    finished_jobs = fetch_artifacts(finished_jobs, user_args, lava)
    return finished_jobs

def fetch_artifacts(jobs, user_args, lava):
    if not user_args.artifacts_path:
        return
    for job_id, info in jobs.items():
        job_dir = info['job_dir']
        info_print("Fetching artifacts for JOB: {} to {}".format(job_id, job_dir))
        os.makedirs(job_dir, exist_ok=True)
        def_path = os.path.join(job_dir, 'definition.yaml')
        target_log = os.path.join(job_dir, 'target_log.txt')
        config = os.path.join(job_dir, 'config.tar.bz2')
        results_file = os.path.join(job_dir, 'results.yaml')
        definition, metadata = lava.get_job_definition(job_id, def_path)
        jobs[job_id]['metadata'] = metadata
        time.sleep(0.2) # be friendly to LAVA
        lava.get_job_log(job_id, target_log)
        time.sleep(0.2)
        lava.get_job_config(job_id, config)
        time.sleep(0.2)
        lava.get_job_results(job_id, results_file)
    return(jobs)


def lava_id_to_url(id, user_args):
    return "{}/scheduler/job/{}".format(user_args.lava_url, id)

def generateTestResult(info):
    if info['health'] == "Complete" and info['state'] == "Finished":
        return "PASS"
    else:
        return "FAIL"

def job_links(jobs, user_args):
    job_links = ""
    for job, info in jobs.items():
        job_links += "Build Config: {}  ".format(info['metadata']['build_name'])
        job_links += "LAVA link: {}  ".format(lava_id_to_url(job, user_args))
        job_links += "Build link: {}\n".format(info['metadata']['build_job_url'])
    print(job_links)

def csv_report(jobs):
    lava_jobs = []
    for job, info in jobs.items():
        exist = False
        for record in lava_jobs:
            if info['metadata']['platform']   == record["Platform"] and \
               info['metadata']['compiler']   == record["Compiler"] and \
               info['metadata']['build_type'] == record["Build Type"]:
                if record[info['metadata']['name']] != "FAIL":
                    record[info['metadata']['name']] = generateTestResult(info)
                exist = True
                break
        if not exist:
            record = {}
            record["Platform"] = info['metadata']['platform']
            record["Compiler"] = info['metadata']['compiler']
            record["Build Type"] = info['metadata']['build_type']
            record["Config Name"] = info['metadata']['name']
            for cfg in cfgs:
                record[cfg] = "N.A."
            record[info['metadata']['name']] = generateTestResult(info)
            lava_jobs.append(record)
    lava_jobs.sort(key=lambda x: x["Platform"] + x["Compiler"] + x["Build Type"])
    with open("test_results.csv", "w", newline="") as csvfile:
        fieldnames = ["Platform", "Compiler", "Build Type"] + cfgs
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

        writer.writeheader()
        writer.writerows(lava_jobs)

def boot_report(jobs, user_args):
    incomplete_jobs = []
    for job, info in jobs.items():
        if info['health'] != 'Complete':
            if info['error_reason'] == 'Infrastructure':
                info_print("Job {} failed with Infrastructure error".format(job))
            incomplete_jobs.append(job)
    incomplete_output = [lava_id_to_url(x, user_args) for x in incomplete_jobs];
    if len(incomplete_jobs) > 0:
        print("BOOT_RESULT: -1 Failed: {}".format(incomplete_output))
    else:
        print("BOOT_RESULT: +1")

def failure_report(jobs, user_args):
    failed_report = "FAILURE_TESTS:"
    for job, info in jobs.items():
        if info['health'] != "Complete" or info['state'] != "Finished":
            failed_report += " {}:{}".format(info['metadata']['build_name'],
                                             lava_id_to_url(job, user_args))
    print(failed_report)

def remove_lava_dupes(results):
    for result in results:
        if result['result'] != 'pass':
            if result['suite'] == "lava":
                for other in [x for x in results if x != result]:
                    if other['name'] == result['name']:
                        if other['result'] == 'pass':
                            results.remove(result)
    return(results)

def test_report(jobs, user_args, lava):
    # parsing of test results is WIP
    fail_j = []
    jinja_data = []
    for job, info in jobs.items():
        results_file = os.path.join(info['job_dir'], 'results.yaml')
        if not os.path.exists(results_file) or (os.path.getsize(results_file) == 0):
            fail_j.append(job)
            continue
        with open(results_file, "r") as F:
            res_data = F.read()
        results = yaml.load(res_data)
        non_lava_results = [x for x in results if x['suite'] != 'lava']
        info['lava_url'] = lava_id_to_url(job, user_args)
        info['artifacts_dir'] = "tf-m-ci-scripts/{}".format(info['job_dir'])
        jinja_data.append({job: [info, non_lava_results]})
        for result in non_lava_results:
            if result['result'] != 'pass':
                fail_j.append(job) if job not in fail_j else fail_j
        time.sleep(0.5) # be friendly to LAVA
    fail_output = [lava_id_to_url(x, user_args) for x in fail_j]
    if len(fail_j) > 0:
        print("TEST_RESULT: -1 Failed: {}".format(fail_output))
    else:
        print("TEST_RESULT: +1")
    data = {}
    data['jobs'] = jinja_data
    render_jinja(data)

def render_jinja(data):
    work_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "jinja2_templates")
    template_loader = FileSystemLoader(searchpath=work_dir)
    template_env = Environment(loader=template_loader)
    html = template_env.get_template("test_summary.jinja2").render(data)
    csv = template_env.get_template("test_summary_csv.jinja2").render(data)
    with open('test_summary.html', "w") as F:
        F.write(html)
    with open('test_summary.csv', "w") as F:
        F.write(csv)

def print_lava_urls(jobs, user_args):
    output = [lava_id_to_url(x, user_args) for x in jobs]
    print("LAVA jobs triggered for this build: {}".format(output))


def info_print(line):
    print("INFO: {}".format(line))

def main(user_args):
    """ Main logic """
    user_args.lava_rpc = "RPC2"
    for try_time in range(3):
        try:
            wait_for_jobs(user_args)
            break
        except Exception as e:
            print(e)
            if try_time < 2:
                print("Try to get LAVA jobs again...")
            else:
                raise e

def get_cmd_args():
    """ Parse command line arguments """

    # Parse command line arguments to override config
    parser = argparse.ArgumentParser(description="Lava Wait Jobs")
    cmdargs = parser.add_argument_group("Lava Wait Jobs")

    # Configuration control
    cmdargs.add_argument(
        "--lava-url", dest="lava_url", action="store", help="LAVA lab URL (without RPC2)"
    )
    cmdargs.add_argument(
        "--job-ids", dest="job_ids", action="store", required=True, help="Comma separated list of job IDS"
    )
    cmdargs.add_argument(
        "--lava-token", dest="lava_token", action="store", help="LAVA auth token"
    )
    cmdargs.add_argument(
        "--lava-user", dest="lava_user", action="store", help="LAVA username"
    )
    cmdargs.add_argument(
        "--use-env", dest="token_from_env", action="store_true", default=False, help="Use LAVA auth info from environment"
    )
    cmdargs.add_argument(
        "--lava-timeout", dest="dispatch_timeout", action="store", type=int, default=3600, help="Time in seconds to wait for all jobs"
    )
    cmdargs.add_argument(
        "--artifacts-path", dest="artifacts_path", action="store", help="Download LAVA artifacts to this directory"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(get_cmd_args())
