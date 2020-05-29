#!/usr/bin/env python3

""" report_parser.py:

    Report parser parses openci json reports and conveys the invormation in a
    one or more standard formats (To be implememented)

    After all information is captured it validates the success/failure status
    and can change the script exit code for intergration with standard CI
    executors.
    """

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


import os
import re
import sys
import json
import argparse
import xmltodict
from pprint import pprint

try:
    from tfm_ci_pylib.utils import load_json, get_local_git_info, \
        save_json, list_subdirs, get_remote_git_info, \
        convert_git_ref_path
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))

    from tfm_ci_pylib.utils import load_json, get_local_git_info, \
        save_json, list_subdirs, get_remote_git_info, \
        convert_git_ref_path


def xml_read(file):
    """" Read the contects of an xml file and convert it to python object """

    data = None
    try:
        with open(file, "r") as F:
            data = xmltodict.parse(F.read())
    except Exception as E:
        print("Error", E)
    return data


def split_keys(joint_arg, sep="="):
    """ Split two keys spread by a separator, and return them as a tuple
    with whitespace removed """

    keys = joint_arg.split(sep)

    # Remove whitespace
    keys = map(str.strip, list(keys))
    # If key contains the word True/False convert it.
    keys = list(map(lambda x:
                eval(x.title()) if x.lower() in ["true", "false"] else x,
                keys))
    return keys


def dependencies_mdt_collect(path_list,
                             out_f=None,
                             known_content_types=["mbedcrypto",
                                                  "cmsis",
                                                  "checkpatch",
                                                  "fpga",
                                                  "fastmodel"],
                             expected_paths=["mbedcrypto",
                                             "cmsis",
                                             "checkpatch"]):
    """ Collect dependencies checkout metadata. It creates a json report which
    can be optionally exported to a file """

    cpaths = {k: v for k, v in [n.split("=") for n in path_list]}
    cwd = os.path.abspath(os.getcwd())

    # Test that all the required paths are present
    intsec_set = set(expected_paths).intersection(set(cpaths.keys()))
    if len(intsec_set) != len(set(expected_paths)):
        _missing = set(expected_paths).difference(intsec_set)
        err_msg = "Error missing core paths.\nRequired: %s\nPresent: %s" % (
            ",".join(_missing), ",".join(cpaths.keys())
        )
        print(err_msg)
        raise Exception(err_msg)

    # Create a dataset for the entires of known data format
    known_data = {n: {} for n in
                  set(known_content_types).intersection(set(cpaths.keys()))}

    # Create a dataset for unexpected data entries of unknown format
    extra_data = {n: {}
                  for n in set(cpaths.keys()).difference(set(known_data))}

    for d in list_subdirs(cpaths["mbedcrypto"]):
        print("mbed-crypto dir: ", d)
        # if checkout directory name contains a git reference convert to short
        d = convert_git_ref_path(d)

        git_info = get_local_git_info(d)
        tag = os.path.split(git_info["dir"])[-1].split("-")[-1]

        # Absolute paths will not work in jenkins since it will change the
        # workspaace directory between stages convert to relative path
        git_info["dir"] = os.path.relpath(git_info["dir"], cwd)
        known_data["mbedcrypto"][tag] = git_info

    for d in list_subdirs(cpaths["cmsis"]):
        print("CMS subdir: ", d)
        d = convert_git_ref_path(d)
        git_info = get_local_git_info(d)
        tag = os.path.split(git_info["dir"])[-1]

        # Absolute paths will not work in jenkins since it will change the
        # workspaace directory between stages convert to relative path
        git_info["dir"] = os.path.relpath(git_info["dir"], cwd)
        known_data["cmsis"][tag] = git_info

    for d in list_subdirs(cpaths["checkpatch"]):
        print("Checkpatch subdir:", d)

        with open(os.path.join(d, "version.info"), "r") as F:
            url = F.readline().strip()

        git_info = get_remote_git_info(url)
        d = convert_git_ref_path(d)
        git_info['dir'] = d
        tag = os.path.split(git_info["dir"])[-1].split("_")[-1]

        # Absolute paths will not work in jenkins since it will change the
        # workspaace directory between stages convert to relative path
        git_info["dir"] = os.path.relpath(git_info["dir"], cwd)
        known_data["checkpatch"][tag] = git_info

    if "fastmodel" in cpaths:
        for d in list_subdirs(cpaths["fastmodel"]):
            print("Fastmodel subdir:", d)
            json_info = load_json(os.path.join(d, "version.info"))
            json_info["dir"] = os.path.relpath(d, cwd)

            tag = json_info["version"]
            # Absolute paths will not work in jenkins since it will change the
            # workspaace directory between stages convert to relative path
            known_data["fastmodel"][tag] = json_info

    if "fpga" in cpaths:
        for d in os.listdir(cpaths["fpga"]):
            print("FPGA imagefile:", d)
            if ".tar.gz" in d:
                name = d.split(".tar.gz")[0]
                platform, subsys, ver = name.split("_")
                known_data["fpga"][name] = {"platform": platform,
                                            "subsys": subsys,
                                            "version": ver,
                                            "recovery": os.path.join(
                                                                 cpaths["fpga"],
                                                                 d)}

    #Attempt to detect what the unexpected paths contain
    for e_path in extra_data.keys():
        for d in list_subdirs(cpaths[e_path]):
            print("%s subdir: %s" % (e_path, d))
            # If it contains a version.info
            if os.path.isfile(os.path.join(d, "version.info")):
                json_info = load_json(os.path.join(d, "version.info"))
                json_info["dir"] = os.path.relpath(d, cwd)

                tag = json_info["version"]
                # Absolute paths will not work in jenkins since it will change
                # the workspaace directory between stages convert to rel-path
                extra_data[e_path][tag] = json_info
            # If it contains git information
            elif os.path.exists(os.path.join(d, ".git")):
                d = convert_git_ref_path(d)

                git_info = get_local_git_info(d)
                tag = os.path.split(git_info["dir"])[-1].split("-")[-1]

                # Absolute paths will not work in jenkins since it will change
                # the workspaace directory between stages convert to rel-path
                git_info["dir"] = os.path.relpath(git_info["dir"], cwd)
                extra_data[e_path][tag] = git_info
            # Do not break flow if detection fails
            else:
                print("Error determining contents of directory: %s/%s for "
                      "indexing purposes" % (e_path, d))
                extra_data[e_path][tag] = {"info": "N.A"}

    # Add the extra paths to the expected ones
    for k, v in extra_data.items():
        known_data[k] = v
    if out_f:
        print("Exporting metadata to", out_f)
        save_json(out_f, known_data)
    else:
        pprint(known_data)


def cppcheck_mdt_collect(file_list, out_f=None):
    """ XML parse multiple cppcheck output files and create a json report """

    xml_files = list(map(os.path.abspath, file_list))

    dict_data = []
    version = None
    for xf in xml_files:
        data = xml_read(xf)

        version = data["results"]["cppcheck"]["@version"]
        # If nothing is found the errors dictionary will be a Nonetype object
        if data["results"]["errors"] is not None:
            # Use json to flatten ordered dict
            str_data = json.dumps(data["results"]["errors"]["error"])
            # Remove @ prefix on first char of files that cppcheck adds
            str_data = str_data.replace("@", '')

            # Convert to dict again(xml to json will have added an array)
            _dt = json.loads(str_data)

            if isinstance(_dt, list):
                dict_data += _dt
            # If only one error is foud it will give it as a single item
            elif isinstance(_dt, dict):
                dict_data += [_dt]
            else:
                print("Ignoring  cpp entry %s of type %s" % (_dt, type(_dt)))

    out_data = {"_metadata_": {"cppcheck-version": version},
                "report": {}}

    for E in dict_data:

        sever = E.pop("severity")

        # Sort it based on serverity
        try:
            out_data["report"][sever].append(E)
        except KeyError:
            out_data["report"][sever] = [E]

    _errors = 0
    for msg_sever, msg_sever_entries in out_data["report"].items():
        out_data["_metadata_"][msg_sever] = str(len(msg_sever_entries))
        if msg_sever == "error":
            _errors = len(msg_sever_entries)

    out_data["_metadata_"]["success"] = True if not int(_errors) else False

    if out_f:
        save_json(out_f, out_data)
    else:
        pprint(out_data)


def checkpatch_mdt_collect(file_name, out_f=None):
    """ Regex parse a checpatch output file and create a report """

    out_data = {"_metadata_": {"errors": 0,
                               "warnings": 0,
                               "lines": 0,
                               "success": True},
                "report": {}
                }
    with open(file_name, "r") as F:
        cpatch_data = F.read().strip()

    # checkpatch will not report anything when no issues are found
    if len(cpatch_data):
        stat_rex = re.compile(r'^total: (\d+) errors, '
                              r'(\d+) warnings, (\d+) lines',
                              re.MULTILINE)
        line_rex = re.compile(r'([\S]+:)\s([\S]+:)\s([\S ]+)\n', re.MULTILINE)
        ewl = stat_rex.search(cpatch_data)
        try:
            _errors, _warnings, _lines = ewl.groups()
        except Exception as E:
            print("Exception parsing checkpatch file.", E)
            # If there is text but not in know format return -1 and fail job
            _errors = _warnings = _lines = "-1"
        checkpath_entries = line_rex.findall(cpatch_data)

        for en in checkpath_entries:
            _file, _line, _ = en[0].split(":")
            try:
                _type, _subtype, _ = en[1].split(":")
            except Exception as e:
                print("WARNING: Ignoring Malformed checkpatch line: %s" %
                      "".join(en))
                continue
            _msg = en[2]

            out_data["_metadata_"] = {"errors": _errors,
                                      "warnings": _warnings,
                                      "lines": _lines,
                                      "success": True if not int(_errors)
                                      else False}

            E = {"id": _subtype,
                 "verbose": _subtype,
                 "msg": _msg,
                 "location": {"file": _file, "line": _line}
                 }
            try:
                out_data["report"][_type.lower()].append(E)
            except KeyError:
                out_data["report"][_type.lower()] = [E]

    if out_f:
        save_json(out_f, out_data)
    else:
        pprint(out_data)


def jenkins_mdt_collect(out_f):
    """ Collects Jenkins enviroment information and stores
     it in a key value list """

    # Jenkins environment parameters are always valid
    jenkins_env_keys = ["BUILD_ID",
                        "BUILD_URL",
                        "JOB_BASE_NAME",
                        "GERRIT_URL",
                        "GERRIT_PROJECT"]
    # The following Gerrit parameters only exist when
    # a job is triggered by a web hook
    gerrit_trigger_keys = ["GERRIT_CHANGE_NUMBER",
                           "GERRIT_CHANGE_SUBJECT",
                           "GERRIT_CHANGE_ID",
                           "GERRIT_PATCHSET_REVISION",
                           "GERRIT_PATCHSET_NUMBER",
                           "GERRIT_REFSPEC",
                           "GERRIT_CHANGE_URL",
                           "GERRIT_BRANCH",
                           "GERRIT_CHANGE_OWNER_EMAIL",
                           "GERRIT_PATCHSET_UPLOADER_EMAIL"]

    # Find as mamny of the variables in environent
    el = set(os.environ).intersection(set(jenkins_env_keys +
                                          gerrit_trigger_keys))
    # Format it in key:value pairs
    out_data = {n: os.environ[n] for n in el}
    if out_f:
        save_json(out_f, out_data)
    else:
        pprint(out_data)


def metadata_collect(user_args):
    """ Logic for information collection during different stages of
    the build """

    if user_args.dependencies_checkout and user_args.content_paths:
        dependencies_mdt_collect(user_args.content_paths,
                                 user_args.out_f)
    elif user_args.git_info:
        git_info = get_local_git_info(os.path.abspath(user_args.git_info))

        if user_args.out_f:
            save_json(user_args.out_f, git_info)
        else:
            pprint(git_info)
    elif user_args.cppcheck_files:
        cppcheck_mdt_collect(user_args.cppcheck_files, user_args.out_f)
    elif user_args.checkpatch_file:
        checkpatch_mdt_collect(user_args.checkpatch_file, user_args.out_f)
    elif user_args.jenkins_info:
        jenkins_mdt_collect(user_args.out_f)
    else:
        print("Invalid Metadata collection arguments")
        print(user_args)
        sys.exit(1)


def collate_report(key_file_list, ouput_f=None, stdout=True):
    """ Join different types of json formatted reports into one """

    out_data = {"_metadata_": {}, "report": {}}
    for kf in key_file_list:
        try:
            key, fl = kf.split("=")
            data = load_json(fl)
            # If data is a standard reprort (metdata-report parse it)
            if ("_metadata_" in data.keys() and "report" in data.keys()):
                out_data["_metadata_"][key] = data["_metadata_"]
                out_data["report"][key] = data["report"]
            # Else treat it as a raw information passing dataset
            else:
                try:
                    out_data["info"][key] = data
                except KeyError as E:
                    out_data["info"] = {key: data}
        except Exception as E:
            print("Exception parsing argument", kf, E)
            continue
    if ouput_f:
        save_json(ouput_f, out_data)
    elif stdout:
        pprint(out_data)
    return out_data


def filter_report(key_value_list, input_f, ouput_f):
    """ Generates a subset of the data contained in
    input_f, by selecting only the values defined in key_value list """

    try:
        rep_data = load_json(input_f)
    except Exception as E:
        print("Exception parsing ", input_f, E)
        sys.exit(1)

    out_data = {}
    for kf in key_value_list:
        try:
            tag, value = kf.split("=")
            # if multiple selection
            if(",") in value:
                out_data[tag] = {}
                for v in value.split(","):
                    data = rep_data[tag][v]
                    out_data[tag][v] = data
            else:
                data = rep_data[tag][value]
                out_data[tag] = {value: data}
        except Exception as E:
            print("Could not extract data-set for k: %s v: %s" % (tag, value))
            print(E)
            continue
    if ouput_f:
        save_json(ouput_f, out_data)
    else:
        pprint(out_data)


def parse_report(user_args):
    """ Parse a report and attempt to determine if it is overall successful or
    not. It will set the script's exit code accordingly """

    # Parse Mode
    in_rep = load_json(user_args.report)
    report_eval = None

    # Extract the required condition for evalutation to pass
    pass_key, pass_val = split_keys(user_args.set_pass)

    print("Evaluation will succeed if \"%s\" is \"%s\"" % (pass_key,
                                                           pass_val))
    try:
        report_eval = in_rep["_metadata_"][pass_key] == pass_val
        print("Evaluating detected '%s' field in _metaddata_. " % pass_key)
    except Exception as E:
        pass

    if report_eval is None:
        if isinstance(in_rep, dict):
            # If report contains an overall success field in metadata do not
            # parse the items
            in_rep = in_rep["report"]
            ev_list = in_rep.values()
        elif isinstance(in_rep, list):
            ev_list = in_rep
        else:
            print("Invalid data type: %s" % type(in_rep))
            return

        if user_args.onepass:
            try:
                report_eval = in_rep[user_args.onepass][pass_key] == pass_val
            except Exception as e:
                report_eval = False

        # If every singel field need to be succesfful, invert the check and
        # look for those who are not
        elif user_args.allpass:
            try:
                if list(filter(lambda x: x[pass_key] != pass_val, ev_list)):
                    pass
                else:
                    report_eval = True
            except Exception as e:
                print(e)
                report_eval = False
        else:
            print("Evaluation condition not set. Please use -a or -o. Launch"
                  "help (-h) for more information")

    print("Evaluation %s" % ("passed" if report_eval else "failed"))
    if user_args.eif:
        print("Setting script exit status")
        sys.exit(0 if report_eval else 1)


def main(user_args):
    """ Main logic """

    # Metadat Collect Mode
    if user_args.collect:
        metadata_collect(user_args)
        return
    elif user_args.filter_report:
        filter_report(user_args.filter_report,
                      user_args.report,
                      user_args.out_f)
    elif user_args.collate_report:
        collate_report(user_args.collate_report, user_args.out_f)
    else:
        parse_report(user_args)


def get_cmd_args():
    """ Parse command line arguments """

    # Parse command line arguments to override config
    parser = argparse.ArgumentParser(description="TFM Report Parser.")
    parser.add_argument("-e", "--error_if_failed",
                        dest="eif",
                        action="store_true",
                        help="If set will change the script exit code")
    parser.add_argument("-s", "--set-success-field",
                        dest="set_pass",
                        default="status = Success",
                        action="store",
                        help="Set the key which the script will use to"
                        "assert success/failure")
    parser.add_argument("-a", "--all-fields-must-pass",
                        dest="allpass",
                        action="store_true",
                        help="When set and a list is provided, all entries"
                        "must be succefull for evaluation to pass")
    parser.add_argument("-o", "--one-field-must-pass",
                        dest="onepass",
                        action="store",
                        help="Only the user defined field must pass")
    parser.add_argument("-r", "--report",
                        dest="report",
                        action="store",
                        help="JSON file containing input report")
    parser.add_argument("-c", "--collect",
                        dest="collect",
                        action="store_true",
                        help="When set, the parser will attempt to collect"
                             "information and produce a report")
    parser.add_argument("-d", "--dependencies-checkout",
                        dest="dependencies_checkout",
                        action="store_true",
                        help="Collect information from a dependencies "
                             "checkout job")
    parser.add_argument("-f", "--output-file",
                        dest="out_f",
                        action="store",
                        help="Output file to store captured information")
    parser.add_argument('-p', '--content-paths',
                        dest="content_paths",
                        nargs='*',
                        help=("Pass a space separated list of paths in the"
                              "following format: -p mbedtls=/yourpath/"
                              "fpv=/another/path .Used in conjuction with -n"))
    parser.add_argument("-g", "--git-info",
                        dest="git_info",
                        action="store",
                        help="Extract git information from given path. "
                             "Requires --colect directive. Optional parameter"
                             "--output-file ")
    parser.add_argument("-x", "--cpp-check-xml",
                        dest="cppcheck_files",
                        nargs='*',
                        action="store",
                        help="Extract cppcheck static analysis information "
                             " output files, provided as a space separated "
                             "list. Requires --colect directive."
                             " Optional parameter --output-file ")
    parser.add_argument("-z", "--checkpatch-parse-f",
                        dest="checkpatch_file",
                        action="store",
                        help="Extract checkpatch static analysis information "
                             " output file. Requires --colect directive."
                             " Optional parameter --output-file ")
    parser.add_argument("-j", "--jenkins-info",
                        dest="jenkins_info",
                        action="store_true",
                        help="Extract jenkings and gerrit trigger enviroment "
                             "information fr. Requires --colect directive."
                             " Optional parameter --output-file ")
    parser.add_argument("-l", "--collate-report",
                        dest="collate_report",
                        action="store",
                        nargs='*',
                        help="Pass a space separated list of key-value pairs"
                             "following format: -l report_key_0=report_file_0"
                             " report_key_1=report_file_1. Collate will "
                             "generate a joint dataset and print it to stdout."
                             "Optional parameter --output-file ")
    parser.add_argument("-t", "--filter-report",
                        dest="filter_report",
                        action="store",
                        nargs='*',
                        help="Requires --report parameter for input file."
                             "Pass a space separated list of key-value pairs"
                             "following format: -l report_key_0=value_0"
                             " report_key_1=value_0. Filter will remote all"
                             "entries of the original report but the ones"
                             "mathing the key:value pairs defined and print it"
                             "to stdout.Optional parameter --output-file")
    return parser.parse_args()


if __name__ == "__main__":
    main(get_cmd_args())
