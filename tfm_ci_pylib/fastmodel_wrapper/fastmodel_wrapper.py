#!/usr/bin/env python3

""" fastmodel_wrapper.py:

    Wraps around Fast models which will execute in headless model
    producing serial output to a defined log file. It will spawn two Proccesses
    and one thread to monitor the output of the simulation and end it when a
    user defined condition is matched. It will perform a set of tests and will
    change the script exit code based on the output of the test """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2020, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

__author__ = "tf-m@lists.trustedfirmware.org"
__project__ = "Trusted Firmware-M Open CI"
__version__ = "1.4.0"

import os
import re
import sys
import argparse
from time import sleep
from pprint import pprint
from copy import deepcopy
from threading import Thread
from queue import Queue, Empty
from subprocess import Popen, PIPE, STDOUT

try:
    from tfm_ci_pylib.utils import find_missing_files, \
        detect_python3, test, check_pid_status, save_json, save_dict_json, \
        load_json
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.utils import find_missing_files, \
        detect_python3, test, check_pid_status, save_json, save_dict_json, \
        load_json


class FastmodelWrapper(object):
    """ Controlling Class that wraps around an ARM Fastmodel and controls
    execution, adding regex flow controls, and headless testing """

    def __init__(self,
                 fvp_cfg=None,
                 work_dir="./",
                 fvp_dir=None,
                 fvp_binary=None,
                 fvp_app=None,
                 fvp_boot=None,
                 terminal_file=None,
                 fvp_time_out=None,
                 fvp_test_error=None):

        # Required by other methods, always set working directory first
        self.work_dir = os.path.abspath(work_dir)

        # Load the configuration from object or file
        self.config, self.name = self.load_config(fvp_cfg)

        self.show_config()

        # Print a header
        ln = int((62 - len(self.name) + 1) / 2)
        print("\n%s Running Test: %s %s\n" % ("#" * ln, self.name, "#" * ln))

        # consume the configuration parameters not related to FPV
        # Extract test cases
        self.test_list = self.config.pop("test_cases")
        self.test_end_string = self.config.pop("test_end_string")
        self.test_rex = self.config.pop("test_rex")

        # Command line arguments overrides
        # When those arguments are provided they override config entries
        f_dir = self.config.pop("directory")
        if fvp_dir:
            self.fvp_dir = os.path.abspath(fvp_dir)
        else:
            self.fvp_dir = os.path.abspath(f_dir)

        ef = self.config.pop("error_on_failed")
        if fvp_test_error:
            self.fvp_test_error = fvp_test_error
        else:
            self.fvp_test_error = ef

        tf = self.config.pop("terminal_log")
        if terminal_file:
            self.term_file = os.path.abspath(terminal_file)
        else:
            tf = os.path.join(self.work_dir, tf)
            self.term_file = os.path.abspath(tf)

        # Override config entries directly
        if fvp_binary:
            self.config["bin"] = fvp_binary

        if fvp_boot:
            if re.match(r'[\S]+.axf$', fvp_boot):
                self.config["application"] = "cpu0=" +\
                                             os.path.abspath(fvp_boot)
            else:
                print("Invalid bootloader %s. Expecting .axf file" % fvp_app)
                sys.exit(1)

        # Ensure that the firmware is copied at the appropriate memory region
        # perfect mathc regx for future ref r'^(?:cpu=)[\S]+.bin@0x10080000$'
        #  TODO remove that when other platforms are added
        if fvp_app:
            if re.match(r'[\S]+.bin$', fvp_app):
                self.config["data"] = "cpu0=" +\
                                      os.path.abspath(fvp_app) +\
                                      "@0x10080000"
            else:
                print("Invalid firmware %s. Expecting .bin file" % fvp_app)
                sys.exit(1)

        if fvp_time_out:
            self.fvp_time_out = fvp_time_out
            self.config["simlimit"] = fvp_time_out

        self.monitor_q = Queue()
        self.stop_all = False
        self.pids = []
        self.fvp_test_summary = False

        # Asserted only after a complete test run,including end string matching
        self.test_complete = False

        self.test_report = None

        # Change to working directory
        os.chdir(self.work_dir)
        print("Switching to working directory: %s" % self.work_dir)
        # Clear the file it it has been created before
        with open(self.term_file, "w") as F:
            F.write("")

    def show_config(self):
        """ print the configuration to console """

        print("\n%s config:\n" % self.name)
        pprint(self.config)

    def load_config(self, config):
        """ Load the configuration from a json file or a memory map"""

        try:
            # If config is an dictionary object use it as is
            if isinstance(config, dict):
                ret_config = config
            elif isinstance(config, str):
                # if the file provided is not detected attempt to look for it
                # in working directory
                if not os.path.isfile(config):
                    # remove path from file
                    cfg_file_2 = os.path.split(config)[-1]
                    # look in the current working directory
                    cfg_file_2 = os.path.join(self.work_dir, cfg_file_2)
                    if not os.path.isfile(cfg_file_2):
                        m = "Could not find cfg in %s or %s " % (config,
                                                                 cfg_file_2)
                        raise Exception(m)
                    # If fille exists in working directory
                    else:
                        config = cfg_file_2
                # Attempt to load the configuration from File
                ret_config = load_json(config)
            else:
                raise Exception("Need to provide a valid config name or file."
                                "Please use --config/--config-file parameter.")

        except Exception as e:
            print("Error! Could not load config. Quitting")
            sys.exit(1)

        # Generate Test name (Used in test report) from terminal file.
        tname = ret_config["terminal_log"].replace("terminal_", "")\
            .split(".")[0].lower()

        return deepcopy(ret_config), tname

    def save_config(self, config_file="fvp_tfm_config.json"):
        """ Safe current configuration to a json file """

        # Add stripped information to config
        exp_cfg = deepcopy(self.config)

        exp_cfg["terminal_log"] = self.term_file
        exp_cfg["error_on_failed"] = self.fvp_test_error
        exp_cfg["directory"] = self.fvp_dir
        exp_cfg["test_cases"] = self.test_list
        exp_cfg["test_end_string"] = self.test_end_string
        exp_cfg["test_rex"] = self.test_rex

        cfg_f = os.path.join(self.work_dir, config_file)
        save_dict_json(cfg_f, exp_cfg, exp_cfg.get_sort_order())
        print("Configuration %s exported." % cfg_f)

    def compile_cmd(self):
        """ Compile all the FPV realted information into a command that can
        be executed manually """

        cmd = ""
        for name, value in self.config.items():
            # Place executable to the beggining of the machine
            if name == "bin":
                cmd = value + cmd
            elif name == "parameters":
                cmd += " " + " ".join(["--parameter %s" % p for p in value])
            # Allows setting a second binary file as data field
            elif name == "application" and ".bin@0x0" in value:
                cmd += " --data %s" % value
            else:
                cmd += " --%s %s" % (name, value)

        # Add the path to the command
        cmd = os.path.join(self.fvp_dir, cmd)

        # Add the log file to the command (optional)
        cmd = cmd.replace("$TERM_FILE", self.term_file)
        return cmd

    def show_cmd(self):
        """ print the FPV command to console """

        print(self.compile_cmd())

    def run_fpv(self):
        """ Run the Fast Model test in a different proccess and return
        the pid for housekeeping puproses """

        def fpv_stdout_parser(dstream, queue):
            """ THREAD: Read STDOUT/STDERR and stop if proccess is done """

            for line in iter(dstream.readline, b''):
                if self.stop_all:
                    break
                else:
                    # Python2 ignores byte literals, P3 requires parsing
                    if detect_python3():
                        line = line.decode("utf-8")
                if "Info: /OSCI/SystemC: Simulation stopped by user" in line:
                    print("/OSCI/SystemC: Simulation stopped")
                    self.stop()
                    break

        # Convert to list
        cmd = self.compile_cmd().split(" ")
        print("fvp cmd ", self.compile_cmd())

        # Run it as subproccess
        self.fvp_proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=False)
        self._fvp_thread = Thread(target=fpv_stdout_parser,
                                  args=(self.fvp_proc.stdout,
                                        self.monitor_q))
        self._fvp_thread.daemon = True
        self._fvp_thread.start()
        return self.fvp_proc.pid

    def run_monitor(self):
        """ Run a parallel threaded proccess that monitors the output of
        the FPV and stops it when the a user specified string is found.
        It returns the pid of the proccess for housekeeping """

        def monitor_producer(dstream, queue):
            """ THREAD: Read STDOUT and push data into a queue """

            for line in iter(dstream.readline, b''):
                if self.stop_all:
                    break
                else:
                    # Python2 ignores byte literals, P3 requires parsing
                    if detect_python3():
                        line = line.decode("utf-8")

                    queue.put(line)

                # If the text end string is found terminate
                if str(line).find(self.test_end_string) > 0:

                    queue.put("Found End String \"%s\"" % self.test_end_string)
                    print("Found End String \"%s\"" % self.test_end_string)
                    self.test_complete = True
                    self.stop()
                    break
                # If the FPV stopps by iteself (i.e simlimit reached) terminate
                if "SystemC: Simulation stopped by user" in str(line):

                    queue.put("Simulation Ended \"%s\"" % self.test_end_string)
                    self.stop()
                    break

            dstream.close()
            return

        # Run the tail as a separate proccess
        cmd = ["tail", "-f", self.term_file]
        self.monitor_proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=False)

        self._fvp_mon_thread = Thread(target=monitor_producer,
                                      args=(self.monitor_proc.stdout,
                                            self.monitor_q))
        self._fvp_mon_thread.daemon = True
        self._fvp_mon_thread.start()
        return self.monitor_proc.pid

    def monitor_consumer(self):
        """ Read the ouptut of the monitor thread and print the queue entries
        one entry at the time (One line per call) """
        try:
            line = self.monitor_q.get_nowait()
        except Empty:
            pass
        else:
            print(line.rstrip())

    def has_stopped(self):
        """Retrun status of stop flag. True indicated stopped state """

        return self.stop_all

    def start(self):
        """ Start the FPV and the montor procccesses and keep
        track of their pids"""

        #  Do not spawn fpv unless everything is in place if
        bin_list = [os.path.join(self.fvp_dir, self.config["bin"]),
                    self.config["application"].replace("cpu0=", "")
                                              .replace("@0x0", ""),
                    self.config["data"].replace("@0x10080000", "")
                                       .replace("@0x00100000", "")
                                       .replace("cpu0=", "")]

        if find_missing_files(bin_list):
            print("Could not find all binaries from %s" % ", ".join(bin_list))
            print("Missing Files:", ", ".join(find_missing_files(bin_list)))
            sys.exit(1)
        self.show_cmd()
        self.pids.append(self.run_fpv())
        self.pids.append(self.run_monitor())
        print("Spawned Proccesses with PID %s" % repr(self.pids)[1:-1])
        return self

    def stop(self):
        """ Stop all threads, proccesses and make sure there are no leaks """

        self.stop_all = True

        # Send the gratious shutdown signal
        self.monitor_proc.terminate()
        self.fvp_proc.terminate()
        sleep(1)
        # List the Zombies
        # TODO remove debug output
        for pid in sorted(self.pids):
            if check_pid_status(pid, ["zombie", ]):
                pass
                # print("Warning. Defunc proccess %s" % pid)

    def test(self):
        """ Parse the output terminal file and evaluate status of tests """

        # read the output file
        with open(self.term_file, "r") as F:
            terminal_log = F.read()

        pass_text = "PASSED"
        # create a filtering regex
        rex = re.compile(self.test_rex)

        # Extract tests status as a tuple list
        tests = rex.findall(terminal_log)

        try:
            if isinstance(tests, list):
                if len(tests):
                    # when test regex is  in format [(test_name, RESULT),...]
                    if isinstance(tests[0], tuple):
                        # Convert result into a dictionary
                        tests = dict(zip(*list(zip(*tests))))
                    # when regex is  in format [(test_name, test_name 2),...]
                    # we just need to verify they exist
                    elif isinstance(tests[0], str):
                        pass_text = "PRESENT"
                        tests = dict(zip(tests,
                                     [pass_text for n in range(len(tests))]))
                    else:
                        raise Exception("Incompatible Test Format")
                else:
                    raise Exception("Incompatible Test Format")
            else:
                raise Exception("Incompatible Test Format")
        except Exception:

            if not self.test_complete:
                print("Warning! Test did not complete.")
            else:
                print("Error", "Invalid tests format: %s type: %s" %
                      (tests, type(tests)))
            # Pass an empty output to test. Do not exit prematurely
            tests = {}

        # Run the test and store the report
        self.test_report = test(self.test_list,
                                tests,
                                pass_text=pass_text,
                                test_name=self.name,
                                error_on_failed=self.fvp_test_error,
                                summary=self.fvp_test_summary)
        return self

    def get_report(self):
        """ Return the test report object to caller """

        if not self.test_report:
            raise Exception("Can not create report from incomplete run cycle!")
        return self.test_report

    def save_report(self, rep_f=None):
        """ Export report into a file, set by test name but can be overidden by
        rep_file"""

        if not self.stop_all or not self.test_report:
            print("Can not create report from incomplete run cycle!")
            return

        if not rep_f:
            rep_f = os.path.join(self.work_dir, "report_%s.json" % self.name)
            rep_f = os.path.abspath(rep_f)
        save_json(rep_f, self.test_report)
        print("Exported test report: %s" % rep_f)
        return self

    def block_wait(self):
        """ Block execution flow and wait for the monitor to complete """
        try:
            while True:
                for pid in sorted(self.pids):

                    if not check_pid_status(pid, ["running",
                                                  "sleeping",
                                                  "disk"]):
                        print("Child proccess of pid: %s has died, exitting!" %
                              pid)
                        self.stop()
                if self.has_stopped():
                    break
                else:
                    self.monitor_consumer()

        except KeyboardInterrupt:
            print("User initiated interrupt")
            self.stop()
        # Allows method to be chainloaded
        return self


def get_cmd_args():
    """ Parse command line arguments """

    # Parse command line arguments to override config
    parser = argparse.ArgumentParser(description="TFM Fastmodel wrapper.")
    parser.add_argument("--bin",
                        dest="fvp_bin",
                        action="store",
                        help="Fast Model platform binary file")
    parser.add_argument("--firmware",
                        dest="fvp_firm",
                        action="store",
                        help="Firmware application file to run")
    parser.add_argument("--boot",
                        dest="fvp_boot",
                        action="store",
                        help="Fast Model bootloader file")
    parser.add_argument("--fpv-path",
                        dest="fvp_dir",
                        action="store",
                        help="Directory path containing the Fast Models")
    parser.add_argument("--work-path",
                        dest="work_dir", action="store",
                        default="./",
                        help="Working directory (Where logs are stored)")
    parser.add_argument("--time-limit",
                        dest="time", action="store",
                        help="Time in seconds to run the simulation")
    parser.add_argument("--log-file",
                        dest="termf",
                        action="store",
                        help="Set terminal log file name")
    parser.add_argument("--error",
                        dest="test_err",
                        action="store",
                        help="raise sys.error = 1 if test failed")
    parser.add_argument("--config-file",
                        dest="config_file",
                        action="store",
                        help="Path of configuration file")
    parser.add_argument("--print-config",
                        dest="p_config",
                        action="store_true",
                        help="Print the configuration to console")
    parser.add_argument("--print-command",
                        dest="p_command",
                        action="store_true",
                        help="Print the FPV launch command to console")
    return parser.parse_args()


def main(user_args):
    """ Main logic """

    # Create FPV handler
    F = FastmodelWrapper(fvp_cfg=user_args.config_file,
                         work_dir=user_args.work_dir,
                         fvp_dir=user_args.fvp_dir,
                         fvp_binary=user_args.fvp_bin,
                         fvp_boot=user_args.fvp_boot,
                         fvp_app=user_args.fvp_firm,
                         terminal_file=user_args.termf,
                         fvp_time_out=user_args.time,
                         fvp_test_error=user_args.test_err)

    if user_args.p_config:
        F.show_config()
        sys.exit(0)

    if user_args.p_command:
        F.show_cmd()
        sys.exit(0)

    # Start the wrapper
    F.start()

    # Wait for the wrapper to complete
    F.block_wait()

    print("Shutting Down")
    # Test the output of the system only after a full execution
    if F.test_complete:
        F.test()


if __name__ == "__main__":
    main(get_cmd_args())
