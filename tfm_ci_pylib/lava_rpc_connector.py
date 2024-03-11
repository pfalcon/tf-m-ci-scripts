#!/usr/bin/env python3

""" lava_rpc_connector.py:

    class that extends xmlrpc in order to add LAVA specific functionality.
    Used in managing communication with the back-end. """

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

import xmlrpc.client
import os
import time
import json
import yaml
import requests
import shutil
import subprocess
import logging


_log = logging.getLogger("lavaci")


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
        self.server_api = "%s/api/v0.2/" % self.server_url
        self.server_results_prefix = "%s/results/%%s" % self.server_url
        self.token = token
        self.username = username
        super(LAVA_RPC_connector, self).__init__(server_addr)

    def _rpc_cmd_raw(self, cmd, params=None):
        """ Run a remote comand and return the result. There is no constrain
        check on the syntax of the command. """

        cmd = "self.%s(%s)" % (cmd, params if params else "")
        return eval(cmd)

    @staticmethod
    def is_tux_id(job_id):
        job_id = str(job_id)
        if job_id.isdigit() and len(job_id) < 22:
            return False
        else:
            return True

    def ls_cmd(self):
        """ Return a list of supported commands """

        print("\n".join(self.system.listMethods()))

    def fetch_file(self, url, out_file):
        auth_params = {
            'user': self.username,
            'token': self.token
        }
        with requests.get(url, stream=True, params=auth_params) as r:
            r.raise_for_status()
            with open(out_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return(out_file)

    def get_job_results(self, job_id, yaml_out_file):
        results_url = "{}/yaml".format(self.server_results_prefix % job_id)
        return(self.fetch_file(results_url, yaml_out_file))

    def get_job_definition(self, job_id, yaml_out_file=None):
        job_def = self.scheduler.jobs.definition(job_id)
        if yaml_out_file:
            with open(yaml_out_file, "w") as F:
                F.write(str(job_def))
        def_o = yaml.safe_load(job_def)
        return def_o

    def get_job_log(self, job_id, target_out_file):
        if self.is_tux_id(job_id):
            auth_headers = {}
            log_url = "https://storage.tuxsuite.com/public/tfc/ci/tests/{job_id}/lava-logs.yaml".format(
                job_id=job_id
            )
        else:
            auth_headers = {"Authorization": "Token %s" % self.token}
            log_url = "{server_url}/jobs/{job_id}/logs/".format(
                server_url=self.server_api, job_id=job_id
            )
        with requests.get(log_url, stream=True, headers=auth_headers) as r:
            r.raise_for_status()
            log_list = yaml.load(r.content, Loader=yaml.SafeLoader)
            with open(target_out_file, "w") as target_out:
                for line in log_list:
                    level = line["lvl"]
                    if (level == "target") or (level == "feedback"):
                        try:
                            target_out.write("{}\n".format(line["msg"]))
                        except UnicodeEncodeError:
                            msg = (
                                line["msg"]
                                .encode("ascii", errors="replace")
                                .decode("ascii")
                            )
                            target_out.write("{}\n".format(msg))

    def get_job_config(self, job_id, config_out_file):
        config_url = "{}/configuration".format(self.server_job_prefix % job_id)
        self.fetch_file(config_url, config_out_file)

    def get_job_info(self, job_id, yaml_out_file=None):
        if self.is_tux_id(job_id):
            assert yaml_out_file is None
            job_info = subprocess.check_output(
                "python3 -u -m tuxsuite test get --json %s" % job_id,
                shell=True,
            )
            _log.info("tuxsuite test get %s: %s", job_id, job_info.decode())
            job_info = json.loads(job_info.decode())
            # Convert a bit to match LAVA output, as expected by
            # the rest of code.
            job_info["state"] = job_info["state"].capitalize()
            job_info["health"] = {"pass": "Complete"}.get(job_info["result"], job_info["result"])
            return job_info

        job_info = self.scheduler.jobs.show(job_id)
        if yaml_out_file:
            with open(yaml_out_file, "w") as F:
                F.write(str(job_info))
        return job_info

    def get_error_reason(self, job_id):
        try:
            lava_res = self.results.get_testsuite_results_yaml(job_id, 'lava')
            results = yaml.safe_load(lava_res)
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

    def device_type_from_def(self, job_data):
        def_yaml = yaml.safe_load(job_data)
        return(def_yaml['device_type'])

    def has_device_type(self, job_data):
        d_type = self.device_type_from_def(job_data)
        all_d = self.scheduler.devices.list()
        for device in all_d:
            if device['type'] == d_type:
                if device['health'] in ['Good', 'Unknown']:
                    return(True)
        return(False)

    def submit_job(self, job_definition):
        """ Will submit a yaml definition pointed by job_definition after
        validating it againist the remote backend. Returns resulting job id,
        and server url for job"""

        try:
            if not self.validate_job_yaml(job_definition):
                _log.error("Server rejected job's syntax")
                raise Exception("Invalid job")
            with open(job_definition, "r") as F:
                job_data = F.read()
        except Exception as e:
            print("Cannot submit invalid job. Check %s's content" %
                  job_definition)
            print(e)
            return None, None

        device_type = self.device_type_from_def(job_data)

        if device_type == "fvp" and os.environ["USE_TUXSUITE_FVP"] == "1":
            output = subprocess.check_output(
                "python3 -u -m tuxsuite test submit --no-wait --device fvp-lava --job-definition %s" % job_definition,
                shell=True,
            )

            job_id = job_url = None
            for l in output.decode().split("\n"):
                _log.debug(l)
                if l.startswith("uid:"):
                    job_id = l.split(None, 1)[1].strip()
                    job_url = "https://tuxapi.tuxsuite.com/v1/groups/tfc/projects/ci/tests/" + job_id
            return (job_id, job_url)

        try:
            if self.has_device_type(job_data):
                job_id = self.scheduler.submit_job(job_data)
                job_url = self.server_job_prefix % job_id
                return(job_id, job_url)
            else:
                raise Exception("No devices online with required device_type")
        except Exception as e:
            _log.exception("Exception submitting job to LAVA", e)
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
                if job_id in finished_jobs:
                    continue
                # Check if the job is not running
                try:
                    cur_status = self.get_job_info(job_id)
                except (xmlrpc.client.ProtocolError, OSError) as e:
                    # There can be transient HTTP errors, e.g. "502 Proxy Error"
                    # or socket timeout.
                    # Just continue with the next job, the faulted one will be
                    # re-checked on next iteration.
                    _log.warning("block_wait_for_jobs: %r occurred, ignore and continue", e)
                    time.sleep(2)
                    continue
                # If in queue or running wait
                if cur_status['state'] in ["Canceling","Finished"]:
                    cur_status['error_reason'] = self.get_error_reason(job_id)
                    finished_jobs[job_id] = cur_status
                    _log.info(
                        "Job %s finished in %ds with state: %s, health: %s. Remaining: %d",
                        job_id, time.time() - start_t,
                        cur_status['state'],
                        cur_status['health'],
                        len(job_ids) - len(finished_jobs)
                    )
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
