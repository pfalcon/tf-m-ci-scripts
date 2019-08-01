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
__version__ = "1.0"

import os
from .utils import *
import shutil
from .structured_task import structuredTask


class TFM_Builder(structuredTask):
    """ Wrap around tfm cmake system and spawn a thread to build the project.
    """
    _tfb_build_params = ["TARGET_PLATFORM",
                         "COMPILER",
                         "PROJ_CONFIG",
                         "CMAKE_BUILD_TYPE",
                         "WITH_MCUBOOT"
                         ]

    _tfb_build_template = ("cmake -G \"Unix Makefiles\" -DPROJ_CONFIG=`"
                           "readlink -f %(PROJ_CONFIG)s.cmake` "
                           "-DTARGET_PLATFORM=%(TARGET_PLATFORM)s "
                           "-DCOMPILER=%(COMPILER)s "
                           "-DCMAKE_BUILD_TYPE=%(CMAKE_BUILD_TYPE)s "
                           "-DBL2=%(WITH_MCUBOOT)s "
                           "%(TFM_ROOT)s")

    def __init__(self,
                 name,      # Proccess name
                 tfm_dir,   # TFM root directory
                 work_dir,  # Current working directory(ie logs)
                 cfg_dict,  # Input config dictionary of the following form
                            # input_dict = {"PROJ_CONFIG": "ConfigRegression",
                            #               "TARGET_PLATFORM": "MUSCA_A",
                            #               "COMPILER": "ARMCLANG",
                            #               "CMAKE_BUILD_TYPE": "Debug"}
                 install=False,    # Install library after build
                 build_threads=4,  # Number of CPU thrads used in build
                 silent=False):    # Silence stdout ouptut

        self._tfb_cfg = cfg_dict
        self._tfb_build_threads = build_threads
        self._tfb_install = install
        self._tfb_silent = silent
        self._tfb_binaries = []

        # Required by other methods, always set working directory first
        self._tfb_work_dir = os.path.abspath(os.path.expanduser(work_dir))

        self._tfb_tfm_dir = os.path.abspath(os.path.expanduser(tfm_dir))
        # Entries will be filled after sanity test on cfg_dict dring pre_exec
        self._tfb_build_dir = None
        self._tfb_log_f = None
        super(TFM_Builder, self).__init__(name=name)

    def mute(self):
        self._tfb_silent = True

    def log(self):
        """ Print and return the contents of log file """
        with open(self._tfb_log_f, "r") as F:
            log = F.read()
        print(log)
        return log

    def report(self):
        """Return the report on the job """
        return self.unstash("Build Report")

    def pre_eval(self):
        """ Tests that need to be run in set-up state """

        # Test that all required entries exist in config
        diff = list(set(self._tfb_build_params) - set(self._tfb_cfg.keys()))
        if diff:
            print("Cound't find require build entry: %s in config" % diff)
            return False
        # TODO check validity of passed config values
        # TODO test detection of srec
        # self.srec_path = shutil.which("srec_cat")
        return True

    def pre_exec(self, eval_ret):
        """ Create all required directories, files if they do not exist """

        self._tfb_build_dir = os.path.join(self._tfb_work_dir,
                                           self.get_name())
        # Ensure we have a clean build directory
        shutil.rmtree(self._tfb_build_dir, ignore_errors=True)

        self._tfb_cfg["TFM_ROOT"] = self._tfb_tfm_dir

        # Append the path for the config
        self._tfb_cfg["PROJ_CONFIG"] = os.path.join(self._tfb_tfm_dir,
                                                    "configs",
                                                    self._tfb_cfg[("PROJ_"
                                                                   "CONFIG")])

        # Log will be placed in work directory, named as the build dir
        self._tfb_log_f = "%s.log" % self._tfb_build_dir

        # Confirm that the work/build directory exists
        for p in [self._tfb_work_dir, self._tfb_build_dir]:
            if not os.path.exists(p):
                os.makedirs(p)

        # Calcuate a list of expected binaries
        binaries = []

        # If install is asserted pick the iems from the appropriate location
        if self._tfb_install:

            fvp_path = os.path.join(self._tfb_build_dir,
                                    "install", "outputs", "fvp")
            platform_path = os.path.join(self._tfb_build_dir,
                                         "install",
                                         "outputs",
                                         self._tfb_cfg["TARGET_PLATFORM"])

            # Generate a list of binaries included in both directories
            common_bin_list = ["tfm_%s.%s" % (s, e) for s in ["s", "ns"]
                               for e in ["bin", "axf"]]
            if self._tfb_cfg["WITH_MCUBOOT"]:
                common_bin_list += ["mcuboot.%s" % e for e in ["bin", "axf"]]

                # When building with bootloader extra binaries are expected
                binaries += [os.path.join(platform_path, b) for b in
                             ["tfm_sign.bin"]]
                binaries += [os.path.join(fvp_path, b) for b in
                             ["tfm_s_ns_signed.bin"]]

            binaries += [os.path.join(p, b) for p in [fvp_path, platform_path]
                         for b in common_bin_list]

            # Add Musca required binaries
            if self._tfb_cfg["TARGET_PLATFORM"] == "MUSCA_A":
                binaries += [os.path.join(platform_path,
                                          "musca_firmware.hex")]

            self._tfb_binaries = binaries

        else:
            binaries += [os.path.join(self._tfb_build_dir, "app", "tfm_ns")]
            binaries += [os.path.join(self._tfb_build_dir, "app",
                                          "secure_fw", "tfm_s")]
            if self._tfb_cfg["WITH_MCUBOOT"]:
                binaries += [os.path.join(self._tfb_build_dir,
                             "bl2", "ext", "mcuboot", "mcuboot")]

            ext = ['.bin', '.axf']
            self._tfb_binaries = ["%s%s" % (n, e) for n in binaries
                                  for e in ext]

            # Add Musca required binaries
            if self._tfb_cfg["TARGET_PLATFORM"] == "MUSCA_A":
                self._tfb_binaries += [os.path.join(self._tfb_build_dir,
                                       "tfm_sign.bin")]
                self._tfb_binaries += [os.path.join(self._tfb_build_dir,
                                       "musca_firmware.hex")]

    def get_binaries(self,
                     bootl=None,
                     bin_s=None,
                     bin_ns=None,
                     bin_sign=None,
                     filt=None):
        """ Return the absolute location of binaries (from config)
        if they exist. Can add a filter parameter which will only
        consider entries with /filter/ in their path as a directory """
        ret_boot = None
        ret_bin_ns = None
        ret_bin_s = None
        ret_bin_sign = None

        # Apply filter as a /filter/ string to the binary list
        filt = "/" + filt + "/" if filter else None
        binaries = list(filter(lambda x: filt in x, self._tfb_binaries)) \
            if filt else self._tfb_binaries

        for obj_file in binaries:
            fname = os.path.split(obj_file)[-1]
            if bootl:
                if fname == bootl:
                    ret_boot = obj_file
                    continue
            if bin_s:
                if fname == bin_s:
                    ret_bin_s = obj_file
                    continue

            if bin_ns:
                if fname == bin_ns:
                    ret_bin_ns = obj_file
                    continue
            if bin_sign:
                if fname == bin_sign:
                    ret_bin_sign = obj_file
                    continue
        return [ret_boot, ret_bin_s, ret_bin_ns, ret_bin_sign]

    def task_exec(self):
        """ Main tasks """

        # Mark proccess running as status
        self.set_status(-1)
        # Go to build directory
        os.chdir(self._tfb_build_dir)
        # Compile the build commands
        cmake_cmd = self._tfb_build_template % self._tfb_cfg
        build_cmd = "cmake --build ./ -- -j %s" % self._tfb_build_threads

        # Pass the report to later stages
        rep = {"build_cmd": "%s" % build_cmd,
               "cmake_cmd": "%s" % cmake_cmd}
        self.stash("Build Report", rep)

        # Calll camke to configure the project
        if not subprocess_log(cmake_cmd,
                              self._tfb_log_f,
                              prefix=cmake_cmd,
                              silent=self._tfb_silent):
            # Build it
            if subprocess_log(build_cmd,
                              self._tfb_log_f,
                              append=True,
                              prefix=build_cmd,
                              silent=self._tfb_silent):
                raise Exception("Build Failed please check log: %s" %
                                self._tfb_log_f)
        else:
            raise Exception("Cmake Failed please check log: %s" %
                            self._tfb_log_f)

        if self._tfb_install:
            install_cmd = "cmake --build ./ -- -j install"
            if subprocess_log(install_cmd,
                              self._tfb_log_f,
                              append=True,
                              prefix=install_cmd,
                              silent=self._tfb_silent):
                raise Exception(("Make install Failed."
                                 " please check log: %s") % self._tfb_log_f)
        if self._tfb_cfg["TARGET_PLATFORM"] == "MUSCA_A":
            boot_f, s_bin, ns_bin, sns_signed_bin = self.get_binaries(
                bootl="mcuboot.bin",
                bin_s="tfm_s.bin",
                bin_ns="tfm_ns.bin",
                bin_sign="tfm_sign.bin",
                filt="MUSCA_A")
            self.convert_to_hex(boot_f, sns_signed_bin)
        self._t_stop()

    def sign_img(self, secure_bin, non_secure_bin):
        """Join a secure and non secure image and sign them"""

        imgtool_dir = os.path.join(self._tfb_tfm_dir,
                                   "bl2/ext/mcuboot/scripts/")
        flash_layout = os.path.join(self._tfb_tfm_dir,
                                    "platform/ext/target/musca_a/"
                                    "partition/flash_layout.h")
        sign_cert = os.path.join(self._tfb_tfm_dir,
                                 "bl2/ext/mcuboot/root-rsa-2048.pem")
        sns_unsigned_bin = os.path.join(self._tfb_build_dir,
                                        "sns_unsigned.bin")
        sns_signed_bin = os.path.join(self._tfb_build_dir, "sns_signed.bin")

        # Early versions of the tool hard relative imports, run from its dir
        os.chdir(imgtool_dir)
        assemble_cmd = ("python3 assemble.py -l  %(layout)s -s %(s)s "
                        "-n %(ns)s -o %(sns)s") % {"layout": flash_layout,
                                                   "s": secure_bin,
                                                   "ns": non_secure_bin,
                                                   "sns": sns_unsigned_bin
                                                   }
        sign_cmd = ("python3 imgtool.py sign -k %(cert)s --align 1 -v "
                    "1.0 -H 0x400 --pad 0x30000 "
                    "%(sns)s %(sns_signed)s") % {"cert": sign_cert,
                                                 "sns": sns_unsigned_bin,
                                                 "sns_signed": sns_signed_bin
                                                 }
        run_proccess(assemble_cmd)
        run_proccess(sign_cmd)
        # Return to build directory
        os.chdir(self._tfb_build_dir)
        return sns_signed_bin

    def convert_to_hex(self,
                       boot_bin,
                       sns_signed_bin,
                       qspi_base=0x200000,
                       boot_size=0x10000):
        """Convert a signed image to an intel hex format with mcuboot """
        if self._tfb_install:
            platform_path = os.path.join(self._tfb_build_dir,
                                         "install",
                                         "outputs",
                                         self._tfb_cfg["TARGET_PLATFORM"])
            firmware_hex = os.path.join(platform_path, "musca_firmware.hex")
        else:
            firmware_hex = os.path.join(self._tfb_build_dir,
                                        "musca_firmware.hex")

        img_offset = qspi_base + boot_size
        merge_cmd = ("srec_cat %(boot)s -Binary -offset 0x%(qspi_offset)x "
                     "%(sns_signed)s -Binary -offset 0x%(img_offset)x "
                     "-o %(hex)s -Intel") % {"boot": boot_bin,
                                             "sns_signed": sns_signed_bin,
                                             "hex": firmware_hex,
                                             "qspi_offset": qspi_base,
                                             "img_offset": img_offset
                                             }
        run_proccess(merge_cmd)
        return

    def post_eval(self):
        """ Verify that the artefacts exist """
        print("%s Post eval" % self.get_name())

        ret_eval = False
        rep = self.unstash("Build Report")
        missing_binaries = list(filter(lambda x: not os.path.isfile(x),
                                self._tfb_binaries))

        if len(missing_binaries):
            print("ERROR: Could not locate the following binaries:")
            print("\n".join(missing_binaries))

            # Update the artifacts to not include missing ones
            artf = [n for n in self._tfb_binaries if n not in missing_binaries]
            # TODO update self._tfb_binaries
            ret_eval = False
        else:
            print("SUCCESS: Produced binaries:")
            print("\n".join(self._tfb_binaries))
            ret_eval = True

            artf = self._tfb_binaries

        # Add artefact related information to report
        rep["log"] = self._tfb_log_f
        rep["missing_artefacts"] = missing_binaries
        rep["artefacts"] = artf

        rep["status"] = "Success" if ret_eval else "Failed"
        self.stash("Build Report", rep)
        return ret_eval

    def post_exec(self, eval_ret):
        """ """

        if eval_ret:
            print("TFM Builder %s was Successful" % self.get_name())
        else:
            print("TFM Builder %s was UnSuccessful" % self.get_name())
