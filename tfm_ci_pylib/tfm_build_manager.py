#!/usr/bin/env python3

""" tfm_build_manager.py:

    Controlling class managing multiple build configruations for tfm """

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
__version__ = "1.0"

import os
import sys
from pprint import pprint
from copy import deepcopy
from .utils import gen_cfg_combinations, list_chunks, load_json,\
    save_json, print_test
from .structured_task import structuredTask
from .tfm_builder import TFM_Builder


class TFM_Build_Manager(structuredTask):
    """ Class that will load a configuration out of a json file, schedule
    the builds, and produce a report """

    def __init__(self,
                 tfm_dir,   # TFM root directory
                 work_dir,  # Current working directory(ie logs)
                 cfg_dict,  # Input config dictionary of the following form
                            # input_dict = {"PROJ_CONFIG": "ConfigRegression",
                            #               "TARGET_PLATFORM": "MUSCA_A",
                            #               "COMPILER": "ARMCLANG",
                            #               "CMAKE_BUILD_TYPE": "Debug"}
                 report=None,        # File to produce report
                 parallel_builds=3,  # Number of builds to run in parallel
                 build_threads=4,    # Number of threads used per build
                 markdown=True,      # Create markdown report
                 html=True,          # Create html report
                 ret_code=True,      # Set ret_code of script if build failed
                 install=False):     # Install libraries after build

        self._tbm_build_threads = build_threads
        self._tbm_conc_builds = parallel_builds
        self._tbm_install = install
        self._tbm_markdown = markdown
        self._tbm_html = html
        self._tbm_ret_code = ret_code

        # Required by other methods, always set working directory first
        self._tbm_work_dir = os.path.abspath(os.path.expanduser(work_dir))

        self._tbm_tfm_dir = os.path.abspath(os.path.expanduser(tfm_dir))

        # Entries will be filled after sanity test on cfg_dict dring pre_exec
        self._tbm_build_dir = None
        self._tbm_report = report

        # TODO move them to pre_eval
        self._tbm_cfg = self.load_config(cfg_dict, self._tbm_work_dir)
        self._tbm_build_cfg_list = self.parse_config(self._tbm_cfg)

        super(TFM_Build_Manager, self).__init__(name="TFM_Build_Manager")

    def pre_eval(self):
        """ Tests that need to be run in set-up state """
        return True

    def pre_exec(self, eval_ret):
        """ """

    def task_exec(self):
        """ Create a build pool and execute them in parallel """

        build_pool = []
        for i in self._tbm_build_cfg_list:

            name = "%s_%s_%s_%s_%s" % (i.TARGET_PLATFORM,
                                       i.COMPILER,
                                       i.PROJ_CONFIG,
                                       i.CMAKE_BUILD_TYPE,
                                       "BL2" if i.WITH_MCUBOOT else "NOBL2")
            print("Loading config %s" % name)
            build_pool.append(TFM_Builder(name,
                              self._tbm_tfm_dir,
                              self._tbm_work_dir,
                              dict(i._asdict()),
                              self._tbm_install,
                              self._tbm_build_threads))

        status_rep = {}
        full_rep = {}
        print("Build: Running %d parallel build jobs" % self._tbm_conc_builds)
        for build_pool_slice in list_chunks(build_pool, self._tbm_conc_builds):

            # Start the builds
            for build in build_pool_slice:
                # Only produce output for the first build
                if build_pool_slice.index(build) != 0:
                    build.mute()
                print("Build: Starting %s" % build.get_name())
                build.start()

            # Wait for the builds to complete
            for build in build_pool_slice:
                # Wait for build to finish
                build.join()
                # Similarly print the logs of the other builds as they complete
                if build_pool_slice.index(build) != 0:
                    build.log()
                print("Build: Finished %s" % build.get_name())

                # Store status in report
                status_rep[build.get_name()] = build.get_status()
                full_rep[build.get_name()] = build.report()
        # Store the report
        self.stash("Build Status", status_rep)
        self.stash("Build Report", full_rep)

        if self._tbm_report:
            print("Exported build report to file:", self._tbm_report)
            save_json(self._tbm_report, full_rep)

    def post_eval(self):
        """ If a single build failed fail the test """
        try:
            retcode_sum = sum(self.unstash("Build Status").values())
            if retcode_sum != 0:
                raise Exception()
            return True
        except Exception as e:
            return False

    def post_exec(self, eval_ret):
        """ Generate a report and fail the script if build == unsuccessfull"""

        self.print_summary()
        if not eval_ret:
            print("ERROR: ====> Build Failed! %s" % self.get_name())
            self.set_status(1)
        else:
            print("SUCCESS: ====> Build Complete!")
            self.set_status(0)

    def get_report(self):
        """ Expose the internal report to a new object for external classes """
        return deepcopy(self.unstash("Build Report"))

    def print_summary(self):
        """ Print an comprehensive list of the build jobs with their status """

        full_rep = self.unstash("Build Report")

        # Filter out build jobs based on status
        fl = ([k for k, v in full_rep.items() if v['status'] == 'Failed'])
        ps = ([k for k, v in full_rep.items() if v['status'] == 'Success'])

        print_test(t_list=fl, status="failed", tname="Builds")
        print_test(t_list=ps, status="passed", tname="Builds")

    def gen_cfg_comb(self, platform_l, compiler_l, config_l, build_l, boot_l):
        """ Generate all possible configuration combinations from a group of
        lists of compiler options"""
        return gen_cfg_combinations("TFM_Build_CFG",
                                    ("TARGET_PLATFORM COMPILER PROJ_CONFIG"
                                     " CMAKE_BUILD_TYPE WITH_MCUBOOT"),
                                    platform_l,
                                    compiler_l,
                                    config_l,
                                    build_l,
                                    boot_l)

    def load_config(self, config, work_dir):
        try:
            # passing config_name param supersseeds fileparam
            if isinstance(config, dict):
                ret_cfg = deepcopy(config)
            elif isinstance(config, str):
                # If the string does not descrive a file try to look for it in
                # work directory
                if not os.path.isfile(config):
                    # remove path from file
                    config_2 = os.path.split(config)[-1]
                    # look in the current working directory
                    config_2 = os.path.join(work_dir, config_2)
                    if not os.path.isfile(config_2):
                        m = "Could not find cfg in %s or %s " % (config,
                                                                 config_2)
                        raise Exception(m)
                    # If fille exists in working directory
                    else:
                        config = config_2
                ret_cfg = load_json(config)

            else:
                raise Exception("Need to provide a valid config name or file."
                                "Please use --config/--config-file parameter.")
        except Exception as e:
            print("Error:%s \nCould not load a valid config" % e)
            sys.exit(1)

        pprint(ret_cfg)
        return ret_cfg

    def parse_config(self, cfg):
        """ Parse a valid configuration file into a set of build dicts """

        # Generate a list of all possible confugration combinations
        full_cfg = self.gen_cfg_comb(cfg["platform"],
                                     cfg["compiler"],
                                     cfg["config"],
                                     cfg["build"],
                                     cfg["with_mcuboot"])

        # Generate a list of all invalid combinations
        rejection_cfg = []

        for k in cfg["invalid"]:
            # Pad the omitted values with wildcard char *
            res_list = list(k) + ["*"] * (5 - len(k))

            print("Working on rejection input: %s" % (res_list))

            # Key order matters. Use index to retrieve default values When
            # wildcard * char is present
            _cfg_keys = ["platform",
                         "compiler",
                         "config",
                         "build",
                         "with_mcuboot"]

            # Replace wildcard ( "*") entries with every inluded in cfg variant
            for n in range(len(res_list)):
                res_list[n] = [res_list[n]] if res_list[n] != "*" \
                    else cfg[_cfg_keys[n]]

            rejection_cfg += self.gen_cfg_comb(*res_list)

        # Notfy the user for the rejected configuations
        for i in rejection_cfg:

            name = "%s_%s_%s_%s_%s" % (i.TARGET_PLATFORM,
                                       i.COMPILER,
                                       i.PROJ_CONFIG,
                                       i.CMAKE_BUILD_TYPE,
                                       "BL2" if i.WITH_MCUBOOT else "NOBL2")
            print("Rejecting config %s" % name)

        # Subtract the two lists and convert to dictionary
        return list(set(full_cfg) - set(rejection_cfg))
