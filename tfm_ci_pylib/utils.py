#!/usr/bin/env python3

""" utils.py:

    various simple and commonly used methods and classes shared by the scripts
    in the CI environment """

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
import yaml
import argparse
import json
import itertools
from collections import OrderedDict, namedtuple
from subprocess import Popen, PIPE, STDOUT


def detect_python3():
    """ Return true if script is run with Python3 interpreter """

    return sys.version_info > (3, 0)


def print_test_dict(data_dict,
                    pad_space=80,
                    identation=5,
                    titl="Summary",
                    pad_char="*"):

    """ Configurable print formatter aimed for dictionaries of the type
    {"TEST NAME": "RESULT"} used in CI systems. It will also return
    the string which is printing """

    # Calculate pad space bewteen variables x, y t achieve alignment on y
    # taking into consideration a maximum aligment boundary p and
    # possible indentation i
    def flex_pad(x, y, p, i):
        return " " * (p - i * 2 - len(x) - len(y)) + "-> "

    # Calculate the padding for the dataset
    tests = [k + flex_pad(k,
                          v,
                          pad_space,
                          identation) + v for k, v in data_dict.items()]

    # Add the identation
    tests = map(lambda x: " " * identation + x, tests)

    # Convert to string
    tests = "\n".join(tests)

    # Calcuate the top header padding ceiling any rounding errors
    hdr_pad = (pad_space - len(titl) - 3) / 2

    if detect_python3():
        hdr_pad = int(hdr_pad)

    # Generate a print formatting dictionary
    print_dict = {"pad0": pad_char * (hdr_pad),
                  "pad1": pad_char * (hdr_pad + 1 if len(titl) % 2
                                      else hdr_pad),
                  "sumry": tests,
                  "pad2": pad_char * pad_space,
                  "titl": titl}

    # Compose & print the report
    r = "\n%(pad0)s %(titl)s %(pad1)s\n\n%(sumry)s\n\n%(pad2)s\n" % print_dict
    print(r)
    return r


def print_test(t_name=None, t_list=None, status="failed", tname="Tests"):
    """ Print a list of tests in a stuctured ascii table format """

    gfx_line1 = "=" * 80
    gfx_line2 = "\t" + "-" * 70
    if t_name:
        print("%(line)s\n%(name)s\n%(line)s" % {"line": gfx_line1,
                                                "name": t_name})
    print("%s %s:" % (tname, status))
    print(gfx_line2 + "\n" +
          "\n".join(["\t|  %(key)s%(pad)s|\n%(line)s" % {
              "key": n,
              "pad": (66 - len(n)) * " ",
              "line": gfx_line2} for n in t_list]))


def test(test_list,
         test_dict,
         test_name="TF-M Test",
         pass_text=["PASSED", "PRESENT"],
         error_on_failed=True,
         summary=True):

    """ Using input of a test_lst and a test results dictionary in the format
    of test_name: resut key-value pairs, test() method will verify that Every
    single method in the test_list has been tested and passed. Pass and Failed,
    status tests can be overriden and error_on_failed flag, exits the script
    with failure if a single test fails or is not detected. Returns a json
    containing status and fields for each test passed/failed/missing, if error
    on failed is not set.
    """

    t_report = {"name": test_name,
                "success": None,
                "passed": [],
                "failed": [],
                "missing": []}
    # Clean-up tests that are not requested by test_list
    test_dict = {k: v for k, v in test_dict.items() if k in test_list}

    # Calculate the difference of the two sets to find missing tests
    t_report["missing"] = list(set(test_list) - set(test_dict.keys()))

    # Sor the items into the apropriate lists (failed or passed)
    # based on their status.
    for k, v in test_dict.items():
        # print(k, v)
        key = "passed" if v in pass_text else "failed"
        t_report[key] += [k]

    # For the test to pass every singe test in test_list needs to be present
    # and be in the passed list
    if len(test_list) == len(t_report["passed"]):
        t_report["success"] = True
    else:
        t_report["success"] = False

    # Print a summary
    if summary:
        if t_report["passed"]:
            print_test(test_name, t_report["passed"], status="passed")
        if t_report["missing"]:
            print_test(test_name, t_report["missing"], status="missing")
        if t_report["failed"]:
            print_test(test_name, t_report["failed"], status="Failed")

    print("\nTest %s has %s!" % (t_report["name"],
                                 " been successful" if t_report["success"]
                                 else "failed"))
    print("-" * 80)
    if error_on_failed:
        syscode = 0 if t_report["success"] else 1
        sys.exit(syscode)
    return t_report


def save_json(f_name, data_object):
    """ Save object to json file """

    with open(f_name, "w") as F:
        F.write(json.dumps(data_object, indent=2))


def save_dict_json(f_name, data_dict, sort_list=None):
    """ Save a dictionary object to file with optional sorting """

    if sort_list:
        data_object = (sort_dict(data_dict, sort_list))
    save_json(f_name, data_object)


def sort_dict(config_dict, sort_order_list=None):
    """ Create a fixed order disctionary out of a config dataset """

    if sort_order_list:
        ret = OrderedDict([(k, config_dict[k]) for k in sort_order_list])
    else:
        ret = OrderedDict([(k, config_dict[k]) for k in sorted(config_dict)])
    return ret


def load_json(f_name):
    """ Load object from json file """

    with open(f_name, "r") as F:
        try:
            return json.loads(F.read())
        except ValueError as exc:
            print("No JSON object could be decoded from file: %s" % f_name)
        except IOError:
            print("Error opening file: %s" % f_name)
        raise Exception("Failed to load file")


def load_yaml(f_name):

    # Parse command line arguments to override config
    with open(f_name, "r") as F:
        try:
            return yaml.load(F.read())
        except yaml.YAMLError as exc:
            print("Error parsing file: %s" % f_name)
        except IOError:
            print("Error opening file: %s" % f_name)
        raise Exception("Failed to load file")


def subprocess_log(cmd, log_f, prefix=None, append=False, silent=False):
    """ Run a command as subproccess an log the output to stdout and fileself.
    If prefix is spefified it will be added as the first line in file """

    with open(log_f, 'a' if append else "w") as F:
        if prefix:
            F.write(prefix + "\n")
        pcss = Popen(cmd,
                     stdout=PIPE,
                     stderr=STDOUT,
                     shell=True,
                     env=os.environ)
        for line in pcss.stdout:
            if detect_python3():
                line = line.decode("utf-8")
            if not silent:
                sys.stdout.write(line)
            F.write(line)
        pcss.communicate()
        return pcss.returncode
    return


def run_proccess(cmd):
    """ Run a command as subproccess an log the output to stdout and file.
    If prefix is spefified it will be added as the first line in file """

    pcss = Popen(cmd,
                 stdout=PIPE,
                 stderr=PIPE,
                 shell=True,
                 env=os.environ)
    pcss.communicate()
    return pcss.returncode


def list_chunks(l, n):
    """ Yield successive n-sized chunks from l. """

    for i in range(0, len(l), n):
        yield l[i:i + n]


def export_config_map(config_m, dir=None):
    """ Will export a dictionary of configurations to a group of JSON files """

    _dir = dir if dir else os.getcwd()
    for _cname, _cfg in config_m.items():
        _cname = _cname.lower()
        _fname = os.path.join(_dir, _cname + ".json")
        print("Exporting config %s" % _fname)
    save_json(_fname, _cfg)


def gen_cfg_combinations(name, categories, *args):
    """ Create a list of named tuples of `name`, with elements defined in a
    space separated string `categories` and equal ammount of lists for said
    categories provided as arguments. Order of arguments should match the
    order of the categories lists """

    build_config = namedtuple(name, categories)
    return [build_config(*x) for x in itertools.product(*args)]


def get_cmd_args(descr="", parser=None):
    """ Parse command line arguments """
    # Parse command line arguments to override config

    if not parser:
        parser = argparse.ArgumentParser(description=descr)
    return parser.parse_args()
