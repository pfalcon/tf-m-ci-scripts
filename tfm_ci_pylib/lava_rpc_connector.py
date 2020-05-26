#!/usr/bin/env python3

""" lava_rpc_connector.py:

    class that extends xmlrpc in order to add LAVA specific functionality.
    Used in managing communication with the back-end. """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2020, Arm Limited. All rights reserved.
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

import xmlrpc.client
import time
import yaml


class LAVA_RPC_connector(xmlrpc.client.ServerProxy, object):

    def __init__(self,
                 username,
                 token,
                 hostname,
                 rest_prefix="RPC2",
                 https=False):

        # If user provides hostname with http/s prefix
        if "://" in hostname:
            htp_pre, hostname = hostname.split("://")
            server_addr = "%s://%s:%s@%s/%s" % (htp_pre,
                                                username,
                                                token,
                                                hostname,
                                                rest_prefix)
            self.server_url = "%s://%s" % (htp_pre, hostname)
        else:
            server_addr = "%s://%s:%s@%s/%s" % ("https" if https else "http",
                                                username,
                                                token,
                                                hostname,
                                                rest_prefix)
            self.server_url = "%s://%s" % ("https" if https else "http",
                                           hostname)

        self.server_job_prefix = "%s/scheduler/job/%%s" % self.server_url
        super(LAVA_RPC_connector, self).__init__(server_addr)

    def _rpc_cmd_raw(self, cmd, params=None):
        """ Run a remote comand and return the result. There is no constrain
        check on the syntax of the command. """

        cmd = "self.%s(%s)" % (cmd, params if params else "")
        return eval(cmd)

    def ls_cmd(self):
        """ Return a list of supported commands """

        print("\n".join(self.system.listMethods()))

    def get_job_results(self, job_id, yaml_out_file=None):
        results = self.results.get_testjob_results_yaml(job_id)
        if yaml_out_file:
            with open(yaml_out_file, "w") as F:
                F.write(results)
        return results

    def get_job_definition(self, job_id, yaml_out_file=None):
        job_def = self.scheduler.jobs.definition(job_id)
        if yaml_out_file:
            with open(yaml_out_file, "w") as F:
                F.write(str(job_def))
        def_o = yaml.load(job_def)
        return job_def, def_o.get('metadata', [])

    def write_target_lines(self, target_out_file, log):
        log = yaml.load(log)
        with open(target_out_file, "w+") as F:
            for line in log:
                if line['lvl'] in ['target', 'feedback']:
                    F.write("{}\n".format(line['msg']))

    def get_job_log(self, job_id, yaml_out_file=None, target_out_file=None):
        job_res, job_log = self.scheduler.jobs.logs(job_id)
        job_log = job_log.data.decode('utf-8')
        if yaml_out_file:
            with open(yaml_out_file, "w") as F:
                F.write(job_log)
        if target_out_file:
            self.write_target_lines(target_out_file, job_log)
        return job_log

    def get_job_config(self, job_id, yaml_out_file=None):
        job_config = self.scheduler.jobs.configuration(job_id)
        if yaml_out_file:
            with open(yaml_out_file, "w") as F:
                for data in job_config:
                    if data:
                        line = data.data.decode('utf-8')
                        F.write(line)
        return job_config

    def get_job_info(self, job_id, yaml_out_file=None):
        job_info = self.scheduler.jobs.show(job_id)
        if yaml_out_file:
            with open(yaml_out_file, "w") as F:
                F.write(str(job_info))
        return job_info

    def get_error_reason(self, job_id):
        try:
            lava_res = self.results.get_testsuite_results_yaml(job_id, 'lava')
            results = yaml.load(lava_res)
            for test in results:
                if test['name'] == 'job':
                    return(test.get('metadata', {}).get('error_type', ''))
        except Exception:
            return("Unknown")

    def get_job_state(self, job_id):
        return self.scheduler.job_state(job_id)["job_state"]

    def cancel_job(self, job_id):
        """ Cancell job with id=job_id. Returns True if successfull """

        return self.scheduler.jobs.cancel(job_id)

    def validate_job_yaml(self, job_definition, print_err=False):
        """ Validate a job definition syntax. Returns true is server considers
        the syntax valid """

        try:
            with open(job_definition) as F:
                input_yaml = F.read()
            self.scheduler.validate_yaml(input_yaml)
            return True
        except Exception as E:
            if print_err:
                print(E)
            return False

    def submit_job(self, job_definition):
        """ Will submit a yaml definition pointed by job_definition after
        validating it againist the remote backend. Returns resulting job id,
        and server url for job"""

        try:
            if not self.validate_job_yaml(job_definition):
                print("Served rejected job's syntax")
                raise Exception("Invalid job")
            with open(job_definition, "r") as F:
                job_data = F.read()
        except Exception as e:
            print("Cannot submit invalid job. Check %s's content" %
                  job_definition)
            print(e)
            return None, None
        try:
            job_id = self.scheduler.submit_job(job_data)
            job_url = self.server_job_prefix % job_id
            return(job_id, job_url)
        except Exception as e:
            print(e)
            return(None, None)

    def resubmit_job(self, job_id):
        """ Re-submit job with provided id. Returns resulting job id,
        and server url for job"""

        job_id = self.scheduler.resubmit_job(job_id)
        job_url = self.server_job_prefix % job_id
        return(job_id, job_url)

    def block_wait_for_job(self, job_id, timeout, poll_freq=1):
        """ Will block code execution and wait for the job to submit.
        Returns job status on completion """

        start_t = int(time.time())
        while(True):
            cur_t = int(time.time())
            if cur_t - start_t >= timeout:
                print("Breaking because of timeout")
                break
            # Check if the job is not running
            cur_status = self.get_job_state(job_id)
            # If in queue or running wait
            if cur_status not in ["Canceling","Finished"]:
                time.sleep(poll_freq)
            else:
                break
        return self.scheduler.job_health(job_id)["job_health"]

    def block_wait_for_jobs(self, job_ids, timeout, poll_freq=10):
        """ Wait for multiple LAVA job ids to finish and return finished list """

        start_t = int(time.time())
        finished_jobs = {}
        while(True):
            cur_t = int(time.time())
            if cur_t - start_t >= timeout:
                print("Breaking because of timeout")
                break
            for job_id in job_ids:
                # Check if the job is not running
                cur_status = self.get_job_info(job_id)
                # If in queue or running wait
                if cur_status['state'] in ["Canceling","Finished"]:
                    cur_status['error_reason'] = self.get_error_reason(job_id)
                    finished_jobs[job_id] = cur_status
                if len(job_ids) == len(finished_jobs):
                    break
                else:
                    time.sleep(poll_freq)
            if len(job_ids) == len(finished_jobs):
                break
        return finished_jobs

    def test_credentials(self):
        """ Attempt to querry the back-end and verify that the user provided
        authentication is valid """

        try:
            self._rpc_cmd_raw("system.listMethods")
            return True
        except Exception as e:
            print(e)
            print("Credential validation failed")
            return False


if __name__ == "__main__":
    pass
