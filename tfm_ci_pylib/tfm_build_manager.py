#!/usr/bin/env python3

""" tfm_build_manager.py:

    Controlling class managing multiple build configruations for tfm """

from __future__ import print_function
from json import tool

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

import os
import sys
from .utils import *
from time import time
from copy import deepcopy
from .structured_task import structuredTask
from .tfm_builder import TFM_Builder
from build_helper.build_helper_config_maps import *

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
                 build_threads=3,    # Number of threads used per build
                 install=False,      # Install libraries after build
                 img_sizes=False,    # Use arm-none-eabi-size for size info
                 relative_paths=False):     # Store relative paths in report
        self._tbm_build_threads = build_threads
        self._tbm_conc_builds = parallel_builds
        self._tbm_install = install
        self._tbm_img_sizes = img_sizes
        self._tbm_relative_paths = relative_paths

        # Required by other methods, always set working directory first
        self._tbm_work_dir = os.path.abspath(os.path.expanduser(work_dir))

        self._tbm_tfm_dir = os.path.abspath(os.path.expanduser(tfm_dir))

        print("bm param tfm_dir %s" % tfm_dir)
        print("bm %s %s %s" % (work_dir, cfg_dict, self._tbm_work_dir))
        # Internal flag to tag simple (non combination formatted configs)
        self.simple_config = False
        self._tbm_report = report

        self._tbm_cfg = self.load_config(cfg_dict, self._tbm_work_dir)
        self._tbm_build_cfg, \
            self.tbm_common_cfg = self.parse_config(self._tbm_cfg)
        self._tfb_code_base_updated = False
        self._tfb_log_f = "CodeBasePrepare.log"

        super(TFM_Build_Manager, self).__init__(name="TFM_Build_Manager")

    def choose_toolchain(self, compiler, s_build):
        toolchain = ""
        if s_build:
            if "GCC"in compiler:
                toolchain = "toolchain_GNUARM.cmake"
            elif "ARMCLANG" in compiler:
                toolchain = "toolchain_ARMCLANG.cmake"
        else:
            if "GCC"in compiler:
                toolchain = "toolchain_ns_GNUARM.cmake"
            elif "ARMCLANG" in compiler:
                toolchain = "toolchain_ns_ARMCLANG.cmake"

        return toolchain

    def get_compiler_name(self, compiler):
        compiler_name = ""
        if "GCC"in compiler:
            compiler_name = "arm-none-eabi-gcc"
        elif "ARMCLANG" in compiler:
            compiler_name = "armclang"

        return compiler_name

    def map_params(self, params, maps):
        build_configs = ""
        param_list = params.split(", ")
        for param in param_list:
            build_configs += maps[param]
        return build_configs

    def get_config(self):
            return list(self._tbm_build_cfg.keys())

    def get_build_configs(self, config, silence_stderr=False):
        """
        Return build config variables needed by the input config.
        """
        if config not in self._tbm_build_cfg:
            if not silence_stderr:
                print("Error: no such config {}".format(config), file=sys.stderr)
            sys.exit(1)
        config_details = self._tbm_build_cfg[config]
        config_params = {
            "CONFIG_NAME":      config,
            "TFM_PLATFORM":     config_details.tfm_platform,
            "COMPILER":         config_details.compiler,
            "ISOLATION_LEVEL":  config_details.isolation_level,
            "TEST_REGRESSION":  config_details.test_regression,
            "TEST_PSA_API":     config_details.test_psa_api,
            "CMAKE_BUILD_TYPE": config_details.cmake_build_type,
            "BL2":              config_details.with_bl2,
            "PROFILE":          "N.A" if not config_details.profile else config_details.profile,
            "EXTRA_PARAMS":     "N.A" if not config_details.extra_params else config_details.extra_params,
        }
        return config_params

    def get_build_commands(self, config, silence_stderr=False, jobs=None):
        """
        Return selected type of commands to be run to build the input config.
        """
        config_details = self._tbm_build_cfg[config]
        codebase_dir = os.path.join(os.getcwd(),"trusted-firmware-m")
        build_config = self.get_build_config(config_details, config, \
                                             silence=silence_stderr, \
                                             codebase_dir=codebase_dir, \
                                             jobs=jobs)
        build_commands = {
            'set_compiler':      build_config['set_compiler_path'],
            'spe_cmake_config':  build_config['spe_config_template'],
            'nspe_cmake_config': build_config['nspe_config_template'],
            'spe_cmake_build':   build_config['spe_cmake_build'],
            'nspe_cmake_build':  build_config['nspe_cmake_build'],
            'post_build':        build_config['post_build']
        }
        return build_commands

    def pre_eval(self):
        """ Tests that need to be run in set-up state """
        return True

    def pre_exec(self, eval_ret):
        """ """

    def override_tbm_cfg_params(self, config, override_keys, **params):
        """ Using a dictionay as input, for each key defined in
        override_keys it will replace the config[key] entries with
        the key=value parameters provided """

        for key in override_keys:
            if isinstance(config[key], list):
                config[key] = [n % params for n in config[key]]
            elif isinstance(config[key], str):
                config[key] = config[key] % params
            else:
                raise Exception("Config does not contain key %s "
                                "of type %s" % (key, config[key]))
        return config

    def pre_build(self, build_cfg):
        print("pre_build start %s \r\nself._tfb_cfg %s\r\n" %
                (self, build_cfg))

        try:
            if self._tfb_code_base_updated:
                print("Code base has been updated")
                return True

            self._tfb_code_base_updated = True

            if "build_psa_api" in build_cfg:
                # FF IPC build needs repo manifest update for TFM and PSA arch test
                if "build_ff_ipc" in build_cfg:
                    print("Checkout to FF IPC code base")
                    os.chdir(build_cfg["codebase_root_dir"] + "/../psa-arch-tests/api-tests")
                    _api_test_manifest = "git checkout . ; python3 tools/scripts/manifest_update.py"
                    if subprocess_log(_api_test_manifest,
                                      self._tfb_log_f,
                                      append=True,
                                      prefix=_api_test_manifest):

                        raise Exception("Python Failed please check log: %s" %
                                        self._tfb_log_f)

                    _api_test_manifest_tfm = "python3 tools/tfm_parse_manifest_list.py -m tools/tfm_psa_ff_test_manifest_list.yaml append"
                    os.chdir(build_cfg["codebase_root_dir"])
                    if subprocess_log(_api_test_manifest_tfm,
                                      self._tfb_log_f,
                                      append=True,
                                      prefix=_api_test_manifest_tfm):

                        raise Exception("Python TFM Failed please check log: %s" %
                                        self._tfb_log_f)
                    return True

            print("Checkout to default code base")
            os.chdir(build_cfg["codebase_root_dir"] + "/../psa-arch-tests/api-tests")
            _api_test_manifest = "git checkout ."
            if subprocess_log(_api_test_manifest,
                              self._tfb_log_f,
                              append=True,
                              prefix=_api_test_manifest):

                raise Exception("Python Failed please check log: %s" %
                                self._tfb_log_f)

            _api_test_manifest_tfm = "python3 tools/tfm_parse_manifest_list.py"
            os.chdir(build_cfg["codebase_root_dir"])
            if subprocess_log(_api_test_manifest_tfm,
                              self._tfb_log_f,
                              append=True,
                              prefix=_api_test_manifest_tfm):

                raise Exception("Python TFM Failed please check log: %s" %
                                self._tfb_log_f)
        finally:
            print("python pass after builder prepare")
            os.chdir(build_cfg["codebase_root_dir"] + "/../")

    def task_exec(self):
        """ Create a build pool and execute them in parallel """

        build_pool = []

        # When a config is flagged as a single build config.
        # Name is evaluated by config type
        if self.simple_config:

            build_cfg = deepcopy(self.tbm_common_cfg)

            # Extract the common for all elements of config
            try:
                build_cfg["required_artefacts"] = build_cfg["required_artefacts"]["all"]
            except KeyError:
                build_cfg["required_artefacts"] = []
            name = build_cfg["config_type"]

            # Override _tbm_xxx paths in commands
            # plafrom in not guaranteed without seeds so _tbm_target_platform
            # is ignored
            over_dict = {"_tbm_build_dir_": os.path.join(self._tbm_work_dir,
                                                         name),
                         "_tbm_code_dir_": build_cfg["codebase_root_dir"]}

            build_cfg = self.override_tbm_cfg_params(build_cfg,
                                                     ["post_build",
                                                      "artifact_capture_rex"],
                                                     **over_dict)

            # Overrides path in expected artefacts
            print("Loading config %s" % name)

            build_pool.append(TFM_Builder(
                              name=name,
                              work_dir=self._tbm_work_dir,
                              cfg_dict=build_cfg,
                              build_threads=self._tbm_build_threads,
                              img_sizes=self._tbm_img_sizes,
                              relative_paths=self._tbm_relative_paths))
        # When a seed pool is provided iterate through the entries
        # and update platform spefific parameters
        elif len(self._tbm_build_cfg):
            print("\r\n_tbm_build_cfg %s\r\n tbm_common_cfg %s\r\n" \
             % (self._tbm_build_cfg, self.tbm_common_cfg))
            for name, i in self._tbm_build_cfg.items():
                # Do not modify the original config
                build_cfg = self.get_build_config(i, name)
                self.pre_build(build_cfg)
                # Overrides path in expected artefacts
                print("Loading config %s" % name)

                build_pool.append(TFM_Builder(
                                  name=name,
                                  work_dir=self._tbm_work_dir,
                                  cfg_dict=build_cfg,
                                  build_threads=self._tbm_build_threads,
                                  img_sizes=self._tbm_img_sizes,
                                  relative_paths=self._tbm_relative_paths))
        else:
            print("Could not find any configuration. Check the rejection list")

        status_rep = {}
        build_rep = {}
        completed_build_count = 0
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
                completed_build_count += 1
                print("Build: Finished %s" % build.get_name())
                print("Build Progress:")
                show_progress(completed_build_count, len(build_pool))

                # Store status in report
                status_rep[build.get_name()] = build.get_status()
                build_rep[build.get_name()] = build.report()

        # Include the original input configuration in the report

        metadata = {"input_build_cfg": self._tbm_cfg,
                    "build_dir": self._tbm_work_dir
                    if not self._tbm_relative_paths
                    else resolve_rel_path(self._tbm_work_dir),
                    "time": time()}

        full_rep = {"report": build_rep,
                    "_metadata_": metadata}

        # Store the report
        self.stash("Build Status", status_rep)
        self.stash("Build Report", full_rep)

        if self._tbm_report:
            print("Exported build report to file:", self._tbm_report)
            save_json(self._tbm_report, full_rep)

    def get_build_config(self, i, name, silence=False, codebase_dir=None, jobs=None):
        build_cfg = deepcopy(self.tbm_common_cfg)
        if not codebase_dir:
            codebase_dir = build_cfg["codebase_root_dir"]
        else:
            # Would prefer to do all with the new variable
            # However, many things use this from build_cfg elsewhere
            build_cfg["codebase_root_dir"] = codebase_dir
        # Extract the common for all elements of config
        try:
            build_cfg["required_artefacts"] = deepcopy(self.tbm_common_cfg["required_artefacts"]["all"])
        except KeyError as E:
            build_cfg["required_artefacts"] = []
        build_cfg["post_build"] = ""
        # Extract the platform specific elements of config
        for key in ["post_build", "required_artefacts"]:
            try:
                if i.tfm_platform in self.tbm_common_cfg[key].keys():
                    build_cfg[key] += deepcopy(self.tbm_common_cfg[key]
                                               [i.tfm_platform])
            except Exception as E:
                pass

        if jobs is None:
            if os.cpu_count() >= 8:
                #run in a serviver with scripts, parallel build will use CPU numbers
                jobs = 2
            else:
                #run in a docker, usually docker with CPUs less than 8
                jobs = os.cpu_count()

        thread_no = " -j {} ".format(jobs)
        build_cfg["spe_cmake_build"] += thread_no
        build_cfg["nspe_cmake_build"] += thread_no

        # Overwrite command lines to set compiler
        build_cfg["set_compiler_path"] %= {"compiler": i.compiler}
        build_cfg["set_compiler_path"] += " ;\n{} --version".format(self.get_compiler_name(i.compiler))

        # Overwrite parameters of build configs
        overwrite_params = {"codebase_root_dir":   build_cfg["codebase_root_dir"],
                            "spe_root_dir":  build_cfg["codebase_root_dir"] + "/../tf-m-tests/tests_reg/spe",
                            "nspe_root_dir":  build_cfg["codebase_root_dir"] + "/../tf-m-tests/tests_reg",
                            "ci_build_root_dir":  build_cfg["codebase_root_dir"] + "/../ci_build",
                            "tfm_platform": i.tfm_platform,
                            "s_compiler": self.choose_toolchain(i.compiler, s_build = True),
                            "ns_compiler": self.choose_toolchain(i.compiler, s_build = False),
                            "isolation_level": i.isolation_level,
                            "test_regression": self.map_params(i.test_regression, mapRegTest),
                            "test_psa_api": i.test_psa_api,
                            "cmake_build_type": i.cmake_build_type,
                            "with_bl2": i.with_bl2,
                            "profile": "" if i.profile=="N.A" else i.profile}
        # The extra params can also contain paths with "codebase_root_dir" and
        # these also need to be substituted
        overwrite_params["extra_params"] = self.map_params(i.extra_params, mapExtraParams) % overwrite_params

        # Print more cmake command details to debug issue in Isolation Level 3
        if i.isolation_level == "3":
            overwrite_params["extra_params"] += " -DCMAKE_VERBOSE_MAKEFILE=ON"

        if i.test_psa_api == "IPC":
            overwrite_params["test_psa_api"] += " -DINCLUDE_PANIC_TESTS=1"
        if i.test_psa_api == "CRYPTO" and "musca" in i.tfm_platform:
            overwrite_params["test_psa_api"] += " -DCC312_LEGACY_DRIVER_API_ENABLED=OFF"
        if i.tfm_platform == "arm/musca_b1":
            overwrite_params["test_psa_api"] += " -DOTP_NV_COUNTERS_RAM_EMULATION=ON"

        # Test root dir
        if i.test_psa_api != "OFF":
            overwrite_params["spe_root_dir"] = build_cfg["codebase_root_dir"] + "/../tf-m-tests/tests_psa_arch/spe"
            overwrite_params["nspe_root_dir"] = build_cfg["codebase_root_dir"] + "/../tf-m-tests/tests_psa_arch"
        elif "PROF" in i.extra_params:
            overwrite_params["spe_root_dir"] = build_cfg["codebase_root_dir"]
            overwrite_params["nspe_root_dir"] = build_cfg["codebase_root_dir"] + "/../tf-m-tools/profiling/profiling_cases/tfm_profiling"

        # Overwrite commands for building TF-M image
        build_cfg["spe_config_template"] %= overwrite_params
        build_cfg["nspe_config_template"] %= overwrite_params
        build_cfg["spe_cmake_build"] %= overwrite_params
        build_cfg["nspe_cmake_build"] %= overwrite_params
        build_cfg["post_build"] %= overwrite_params

        # Disable NSPE CMake commands when NS is OFF
        if "NSOFF" in i.extra_params:
            build_cfg["nspe_config_template"] = ""
            build_cfg["nspe_cmake_build"] = ""

        return build_cfg

    def post_eval(self):
        """ If a single build failed fail the test """
        try:
            status_dict = self.unstash("Build Status")
            if not status_dict:
                raise Exception()
            retcode_sum = sum(status_dict.values())
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

        return ret_cfg

    def parse_config(self, cfg):
        """ Parse a valid configuration file into a set of build dicts """

        ret_cfg = {}

        # Config entries which are not subject to changes during combinations
        static_cfg = cfg["common_params"]

        # Converth the code path to absolute path
        abs_code_dir = static_cfg["codebase_root_dir"]
        abs_code_dir = os.path.abspath(os.path.expanduser(abs_code_dir))
        static_cfg["codebase_root_dir"] = abs_code_dir

        # seed_params is an optional field. Do not proccess if it is missing
        if "seed_params" in cfg:
            comb_cfg = cfg["seed_params"]
            # Generate a list of all possible confugration combinations
            ret_cfg = TFM_Build_Manager.generate_config_list(comb_cfg,
                                                             static_cfg)

            # valid is an optional field. Do not proccess if it is missing
            if "valid" in cfg:
                # Valid configurations(Need to build)
                valid_cfg = cfg["valid"]
                # Add valid configs to build list
                ret_cfg.update(TFM_Build_Manager.generate_optional_list(
                    comb_cfg,
                    static_cfg,
                    valid_cfg))

            # invalid is an optional field. Do not proccess if it is missing
            if "invalid" in cfg:
                # Invalid configurations(Do not build)
                invalid_cfg = cfg["invalid"]
                # Remove the rejected entries from the test list
                rejection_cfg = TFM_Build_Manager.generate_optional_list(
                    comb_cfg,
                    static_cfg,
                    invalid_cfg)

                # Subtract the two configurations
                ret_cfg = {k: v for k, v in ret_cfg.items()
                           if k not in rejection_cfg}
            self.simple_config = False
        else:
            self.simple_config = True
        return ret_cfg, static_cfg

    # ----- Override bellow methods when subclassing for other projects ----- #

    def print_summary(self):
        """ Print an comprehensive list of the build jobs with their status """

        try:
            full_rep = self.unstash("Build Report")["report"]
            fl = ([k for k, v in full_rep.items() if v['status'] == 'Failed'])
            ps = ([k for k, v in full_rep.items() if v['status'] == 'Success'])
        except Exception as E:
            print("No report generated", E)
            return
        if fl:
            print_test(t_list=fl, status="failed", tname="Builds")
        if ps:
            print_test(t_list=ps, status="passed", tname="Builds")

    @staticmethod
    def generate_config_list(seed_config, static_config):
        """ Generate all possible configuration combinations from a group of
        lists of compiler options"""
        config_list = []

        if static_config["config_type"] == "tf-m":
            cfg_name = "TFM_Build_CFG"
            # Ensure the fieds are sorted in the desired order
            # seed_config can be a subset of sort order for configurations with
            # optional parameters.
            tags = [n for n in static_config["sort_order"]
                    if n in seed_config.keys()]
            print("!!!!!!!!!!!gen list %s\r\n" % tags)

            data = []
            for key in tags:
                data.append(seed_config[key])
            config_list = gen_cfg_combinations(cfg_name,
                                               " ".join(tags),
                                               *data)
        else:
            print("Not information for project type: %s."
                  " Please check config" % static_config["config_type"])

        ret_cfg = {}
        # Notify the user for the rejected configuations
        for i in config_list:
            # Convert named tuples to string in a brief format
            config_param = []
            config_param.append(mapPlatform[list(i)[0]])
            config_param.append(list(i)[1].split("_")[0])
            config_param.append(list(i)[2]) # ISOLATION_LEVEL
            if list(i)[3] != "OFF":  # TEST_REGRESSION
                config_param.append(list(i)[3].replace(", ", "_"))
            if list(i)[4] != "OFF":    #TEST_PSA_API
                config_param.append(mapTestPsaApi[list(i)[4]])
            config_param.append(list(i)[5]) # BUILD_TYPE
            if list(i)[6]:  # BL2
                config_param.append("BL2")
            if list(i)[7]: # PROFILE
                config_param.append(mapProfile[list(i)[7]])
            if list(i)[8]: # EXTRA_PARAMS
                config_param.append(list(i)[8].replace(", ", "_"))
            i_str = "_".join(config_param)
            ret_cfg[i_str] = i
        return ret_cfg

    @staticmethod
    def generate_optional_list(seed_config,
                               static_config,
                               optional_list):
        optional_cfg = {}

        if static_config["config_type"] == "tf-m":

            # If optional list is empty do nothing
            if not optional_list:
                return optional_cfg

            tags = [n for n in static_config["sort_order"]
                    if n in seed_config.keys()]
            sorted_default_lst = [seed_config[k] for k in tags]

            # If tags are not alligned with optional list entries quit
            if len(tags) != len(optional_list[0]):
                print(len(tags), len(optional_list[0]))
                print("Error, tags should be assigned to each "
                      "of the optional inputs")
                return []

            # Replace wildcard ( "*") entries with every
            # inluded in cfg variant
            for k in optional_list:
                # Pad the omitted values with wildcard char *
                res_list = list(k) + ["*"] * (5 - len(k))
                print("Working on optional input: %s" % (res_list))

                for n in range(len(res_list)):

                    res_list[n] = [res_list[n]] if res_list[n] != "*" \
                        else sorted_default_lst[n]

                # Generate a configuration and a name for the completed array
                op_cfg = TFM_Build_Manager.generate_config_list(
                    dict(zip(tags, res_list)),
                    static_config)

                # Append the configuration to the existing ones
                optional_cfg = dict(optional_cfg, **op_cfg)

            # Notify the user for the optional configuations
            for i in optional_cfg.keys():
                print("Generating optional config %s" % i)
        else:
            print("Not information for project type: %s."
                  " Please check config" % static_config["config_type"])
        return optional_cfg
