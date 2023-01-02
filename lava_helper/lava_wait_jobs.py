#!/usr/bin/env python3

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2020-2022, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

"""
Script for waiting for LAVA jobs and parsing the results
"""

import os
import time
import yaml
import argparse
import shutil
import logging
from jinja2 import Environment, FileSystemLoader
from lava_helper import test_lava_dispatch_credentials
from lava_submit_jobs import submit_lava_jobs
import codecov_helper


_log = logging.getLogger("lavaci")


def wait_for_jobs(user_args):
    job_list = user_args.job_ids.split(",")
    job_list = [int(x) for x in job_list if x != '']
    lava = test_lava_dispatch_credentials(user_args)
    finished_jobs = get_finished_jobs(job_list, user_args, lava)
    resubmit_jobs = resubmit_failed_jobs(finished_jobs, user_args)
    if resubmit_jobs:
        _log.info("Waiting for resubmitted jobs: %s", resubmit_jobs)
        finished_resubmit_jobs = get_finished_jobs(resubmit_jobs, user_args, lava)
        finished_jobs.update(finished_resubmit_jobs)
    return finished_jobs

def process_finished_jobs(finished_jobs, user_args):
    print_lava_urls(finished_jobs, user_args)
    test_report(finished_jobs, user_args)
    job_links(finished_jobs, user_args)
    codecov_helper.coverage_reports(finished_jobs, user_args)

def get_finished_jobs(job_list, user_args, lava):
    _log.info("Waiting for %d LAVA jobs", len(job_list))
    finished_jobs = lava.block_wait_for_jobs(job_list, user_args.dispatch_timeout, 5)
    unfinished_jobs = [item for item in job_list if item not in finished_jobs]
    for job in unfinished_jobs:
        _log.info("Cancelling unfinished job %d", job)
        lava.cancel_job(job)
    if user_args.artifacts_path:
        for job, info in finished_jobs.items():
            info['job_dir'] = os.path.join(user_args.artifacts_path, "{}_{}".format(str(job), info['description']))
            finished_jobs[job] = info
    finished_jobs = fetch_artifacts(finished_jobs, user_args, lava)
    return finished_jobs

def resubmit_failed_jobs(jobs, user_args):
    if not jobs:
        return []
    time.sleep(2) # be friendly to LAVA
    failed_job = []
    os.makedirs('failed_jobs', exist_ok=True)
    for job_id, info in jobs.items():
        if not (info['health'] == "Complete" and info['state'] == "Finished"):
            _log.warning(
                "Will resubmit job %d because of its state: %s, health: %s",
                job_id, info["state"], info["health"]
            )
            job_dir = info['job_dir']
            def_path = os.path.join(job_dir, 'definition.yaml')
            os.rename(def_path, 'failed_jobs/{}_definition.yaml'.format(job_id))
            shutil.rmtree(job_dir)
            failed_job.append(job_id)
    for failed_job_id in failed_job:
        jobs.pop(failed_job_id)
    resubmitted_jobs = submit_lava_jobs(user_args, job_dir='failed_jobs')
    resubmitted_jobs = [int(x) for x in resubmitted_jobs if x != '']
    return resubmitted_jobs

def fetch_artifacts(jobs, user_args, lava):
    if not user_args.artifacts_path:
        return
    for job_id, info in jobs.items():
        job_dir = info['job_dir']
        t = time.time()
        _log.info("Fetching artifacts for job %d to %s", job_id, job_dir)
        os.makedirs(job_dir, exist_ok=True)
        def_path = os.path.join(job_dir, 'definition.yaml')
        target_log = os.path.join(job_dir, 'target_log.txt')
        config = os.path.join(job_dir, 'config.tar.bz2')
        results_file = os.path.join(job_dir, 'results.yaml')
        definition = lava.get_job_definition(job_id, def_path)
        jobs[job_id]['metadata'] = definition.get('metadata', [])
        time.sleep(0.2) # be friendly to LAVA
        lava.get_job_log(job_id, target_log)
        time.sleep(0.2)
        lava.get_job_config(job_id, config)
        time.sleep(0.2)
        lava.get_job_results(job_id, results_file)
        _log.info("Fetched artifacts in %ds", time.time() - t)
        codecov_helper.extract_trace_data(target_log, job_dir)
    return(jobs)


def lava_id_to_url(id, user_args):
    return "{}/scheduler/job/{}".format(user_args.lava_url, id)

def job_links(jobs, user_args):
    job_links = ""
    for job, info in jobs.items():
        job_links += "\nLAVA Test Config:\n"
        job_links += "Config Name: {}\n".format(info['metadata']['build_name'])
        job_links += "Test Result: {}\n".format(info['result'])
        job_links += "Device Type: {}\n".format(info['metadata']['device_type'])
        job_links += "Build link: {}\n".format(info['metadata']['build_job_url'])
        job_links += "LAVA link: {}\n".format(lava_id_to_url(job, user_args))
        job_links += "TFM LOG: {}artifact/{}/target_log.txt\n".format(os.getenv("BUILD_URL"), info['job_dir'])
    print(job_links)

def remove_lava_dupes(results):
    for result in results:
        if result['result'] != 'pass':
            if result['suite'] == "lava":
                for other in [x for x in results if x != result]:
                    if other['name'] == result['name']:
                        if other['result'] == 'pass':
                            results.remove(result)
    return(results)

def test_report(jobs, user_args):
    # parsing of test results is WIP
    fail_j = []
    jinja_data = []
    for job, info in jobs.items():
        info['result'] = 'SUCCESS'
        if info['health'] != 'Complete':
            info['result'] = 'FAILURE'
            fail_j.append(job)
            continue
        results_file = os.path.join(info['job_dir'], 'results.yaml')
        if not os.path.exists(results_file) or (os.path.getsize(results_file) == 0):
            info['result'] = 'FAILURE'
            fail_j.append(job)
            continue
        with open(results_file, "r") as F:
            res_data = F.read()
        results = yaml.safe_load(res_data)
        non_lava_results = [x for x in results if x['suite'] != 'lava' or x['name'] == 'lava-test-monitor']
        info['lava_url'] = lava_id_to_url(job, user_args)
        info['artifacts_dir'] = info['job_dir']
        jinja_data.append({job: [info, non_lava_results]})
        for result in non_lava_results:
            if result['result'] == 'fail':
                info['result'] = 'FAILURE'
                fail_j.append(job) if job not in fail_j else fail_j
        time.sleep(0.5) # be friendly to LAVA
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
    info_print("LAVA jobs triggered for this build: {}".format(output))


def info_print(line, silent=True):
    if not silent:
        print("INFO: {}".format(line))


# WARNING: Setting this to >1 is a last resort, temporary stop-gap measure,
# which will overload LAVA and jeopardize stability of the entire TF CI.
INEFFICIENT_RETRIES = 1


def main(user_args):
    """ Main logic """
    for try_time in range(INEFFICIENT_RETRIES):
        try:
            finished_jobs = wait_for_jobs(user_args)
            break
        except Exception as e:
            if try_time < INEFFICIENT_RETRIES - 1:
                _log.exception("Exception in wait_for_jobs")
                _log.info("Will try to get LAVA jobs again, this was try: %d", try_time)
            else:
                raise e
    process_finished_jobs(finished_jobs, user_args)

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
    logging.basicConfig(level=logging.INFO)
    main(get_cmd_args())
