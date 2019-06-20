#!/usr/bin/env python3

""" tfm_builder.py:

    Build wrapping class that builds a specific tfm configuration """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2019, Arm Limited. All rights reserved.
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

import os
import re
import shutil
from .utils import *
from .structured_task import structuredTask


class TFM_Builder(structuredTask):
    """ Wrap around tfm cmake system and spawn a thread to build the project.
    """
    def __init__(self,
                 name,      # Proccess name
                 work_dir,  # Current working directory(ie logs)
                 cfg_dict,  # Input config dictionary of the following form
                            # input_dict = {"PROJ_CONFIG": "ConfigRegression",
                            #               "TARGET_PLATFORM": "MUSCA_A",
                            #               "COMPILER": "ARMCLANG",
                            #               "CMAKE_BUILD_TYPE": "Debug"}
                 build_threads=4,   # Number of CPU thrads used in build
                 silent=False,      # Silence stdout ouptut
                 img_sizes=False,   # Use arm-none-eabi-size for size info
                 relative_paths=False):  # Store relative paths in report

        self._tfb_cfg = cfg_dict
        self._tfb_build_threads = build_threads
        self._tfb_silent = silent
        self._tfb_img_sizes = img_sizes
        self._tfb_relative_paths = relative_paths
        self._tfb_binaries = []

        # Required by other methods, always set working directory first
        self._tfb_work_dir = os.path.abspath(os.path.expanduser(work_dir))

        # Override code_base_dir with abspath
        _code_dir = self._tfb_cfg["codebase_root_dir"]
        self._tfb_code_dir = os.path.abspath(os.path.expanduser(_code_dir))
        # Entries will be filled after sanity test on cfg_dict dring pre_exec
        self._tfb_build_dir = None
        self._tfb_log_f = None

        super(TFM_Builder, self).__init__(name=name)

    def mute(self):
        self._tfb_silent = True

    def log(self):
        """ Print and return the contents of log file """
        try:
            with open(self._tfb_log_f, "r") as F:
                log = F.read()
            print(log)
            return log
        except FileNotFoundError:
            print("Log %s not found" % self._tfb_log_f)
            return ""

    def report(self):
        """Return the report on the job """
        return self.unstash("Build Report")

    def pre_eval(self):
        """ Tests that need to be run in set-up state """

        if not os.path.isdir(self._tfb_code_dir):
            print("Missing code-base directory:", self._tfb_code_dir)
            return False

        return True

    def pre_exec(self, eval_ret):
        """ Create all required directories, files if they do not exist """

        self._tfb_build_dir = os.path.join(self._tfb_work_dir,
                                           self.get_name())
        # Ensure we have a clean build directory
        shutil.rmtree(self._tfb_build_dir, ignore_errors=True)

        # Log will be placed in work directory, named as the build dir
        self._tfb_log_f = "%s.log" % self._tfb_build_dir

        # Confirm that the work/build directory exists
        for p in [self._tfb_work_dir, self._tfb_build_dir]:
            if not os.path.exists(p):
                os.makedirs(p)

    def task_exec(self):
        """ Main tasks """

        # Mark proccess running as status
        self.set_status(-1)
        # Go to build directory
        os.chdir(self._tfb_build_dir)

        build_cmds = self._tfb_cfg["build_cmds"]

        threads_no_rex = re.compile(r'.*(-j\s?(\d+))')

        # Pass the report to later stages
        rep = {"build_cmd": "%s" % ",".join(build_cmds)}
        self.stash("Build Report", rep)

        # Calll cmake to configure the project
        for build_cmd in build_cmds:
            # if a -j parameter is passed as user argument
            user_set_threads_match = threads_no_rex.findall(build_cmd)

            if user_set_threads_match:
                # Unpack the regex groups (fullmatch, decimal match)
                user_jtxt, user_set_threads = user_set_threads_match[0]
                if int(user_set_threads) > self._tfb_build_threads:
                    print("Ignoring user requested n=%s threads because it"
                          " exceeds the maximum thread set ( %d )" %
                          (user_set_threads, self._tfb_build_threads))
                    thread_no = self._tfb_build_threads
                else:
                    print("Using %s build threads" % user_set_threads)
                    thread_no = user_set_threads
                build_cmd = build_cmd.replace(user_jtxt,
                                              "-j %s " % thread_no)

            # Build it
            if subprocess_log(build_cmd,
                              self._tfb_log_f,
                              append=True,
                              prefix=build_cmd,
                              silent=self._tfb_silent):

                raise Exception("Build Failed please check log: %s" %
                                self._tfb_log_f)

        self._t_stop()

    def post_eval(self):
        """ Verify that the artefacts exist """
        print("%s Post eval" % self.get_name())

        ret_eval = False
        rep = self.unstash("Build Report")

        artefacts = list_filtered_tree(self._tfb_work_dir, r'%s' %
                                       self._tfb_cfg["artifact_capture_rex"])

        # Add artefact related information to report
        rep["log"] = self._tfb_log_f

        if not len(artefacts):
            print("ERROR: Could not capture any binaries:")

            # TODO update self._tfb_binaries
            ret_eval = False
        else:
            print("SUCCESS: Produced the following binaries:")
            print("\n\t".join(artefacts))
            ret_eval = True

        rep["artefacts"] = artefacts

        # Proccess the artifacts into file structures
        art_files = {}
        for art_item in artefacts:
            art_f = {"pl_source": 1,
                     "resource": art_item if not self._tfb_relative_paths
                     else resolve_rel_path(art_item),
                     "size": {"bytes": str(os.path.getsize(art_item))}
                     }
            if self._tfb_img_sizes and ".axf" in art_item:
                eabi_size, _ = arm_non_eabi_size(art_item)
                art_f["size"]["text"] = eabi_size["text"]
                art_f["size"]["data"] = eabi_size["data"]
                art_f["size"]["bss"] = eabi_size["bss"]
            # filename is used as key for artfacts
            art_files[os.path.split(art_item)[-1]] = art_f
        rep["artefacts"] = art_files

        if "required_artefacts" in self._tfb_cfg.keys():
            if len(self._tfb_cfg["required_artefacts"]):
                print("Searching for required binaries")
                missing_binaries = list(filter(lambda x: not os.path.isfile(x),
                                        self._tfb_cfg["required_artefacts"]))
                if len(missing_binaries):
                    rep["missing_artefacts"] = missing_binaries
                    print("ERROR: Missing required artefacts:")
                    print("\n".join(missing_binaries))
                    ret_eval = False
                else:
                    ret_eval = True

        rep["status"] = "Success" if ret_eval else "Failed"
        self.stash("Build Report", rep)
        return ret_eval

    def post_exec(self, eval_ret):
        """ """

        if eval_ret:
            print("TFM Builder %s was Successful" % self.get_name())
        else:
            print("TFM Builder %s was UnSuccessful" % self.get_name())


if __name__ == "__main__":
    pass
