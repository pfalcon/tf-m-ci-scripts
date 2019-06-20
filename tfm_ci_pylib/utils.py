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
__version__ = "1.1"

import os
import re
import sys
import yaml
import requests
import argparse
import json
import itertools
import xmltodict
from shutil import move
from collections import OrderedDict, namedtuple
from subprocess import Popen, PIPE, STDOUT, check_output


def detect_python3():
    """ Return true if script is run with Python3 interpreter """

    return sys.version_info > (3, 0)


def find_missing_files(file_list):
    """ Return the files that dot not exist in the file_list """

    F = set(file_list)
    T = set(list(filter(os.path.isfile, file_list)))
    return list(F.difference(T))


def resolve_rel_path(target_path, origin_path=os.getcwd()):
    """ Resolve relative path from origin to target. By default origin
    path is current working directory. """

    common = os.path.commonprefix([origin_path, target_path])
    return os.path.relpath(target_path, common)


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


def get_pid_status(pid):
    """ Read the procfc in Linux machines to determine a proccess's statusself.
    Returns status if proccess exists or None if it does not """

    try:
        with open("/proc/%s/status" % pid, "r") as F:
            full_state = F.read()
            return re.findall(r'(?:State:\t[A-Z]{1} \()(\w+)',
                              full_state, re.MULTILINE)[0]
    except Exception as e:
        print("Exception", e)


def check_pid_status(pid, status_list):
    """ Check a proccess's status againist a provided lists and return True
    if the proccess exists and has a status included in the list. (Linux) """

    pid_status = get_pid_status(pid)

    if not pid_status:
        print("PID  %s does not exist." % pid)
        return False

    ret = pid_status in status_list
    # TODO Remove debug print
    if not ret:
        print("PID status %s not in %s" % (pid_status, ",".join(status_list)))
    return ret


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


def show_progress(current_count, total_count):
    """ Display the percent progress percentage of input metric a over b """

    progress = int((current_count / total_count) * 100)
    completed_count = int(progress * 0.7)
    remaining_count = 70 - completed_count
    print("[ %s%s | %d%% ]" % ("#" * completed_count,
                               "~" * remaining_count,
                               progress))


def get_cmd_args(descr="", parser=None):
    """ Parse command line arguments """
    # Parse command line arguments to override config

    if not parser:
        parser = argparse.ArgumentParser(description=descr)
    return parser.parse_args()


def arm_non_eabi_size(filename):
    """ Run arm-non-eabi-size command and parse the output using regex. Will
    return a tuple with the formated data as well as the raw output of the
    command """

    size_info_rex = re.compile(r'^\s+(?P<text>[0-9]+)\s+(?P<data>[0-9]+)\s+'
                               r'(?P<bss>[0-9]+)\s+(?P<dec>[0-9]+)\s+'
                               r'(?P<hex>[0-9a-f]+)\s+(?P<file>\S+)',
                               re.MULTILINE)

    eabi_size = check_output(["arm-none-eabi-size",
                              filename],
                             timeout=2).decode('UTF-8').rstrip()

    size_data = re.search(size_info_rex, eabi_size)

    return [{"text": size_data.group("text"),
             "data": size_data.group("data"),
             "bss": size_data.group("bss"),
             "dec": size_data.group("dec"),
             "hex": size_data.group("hex")}, eabi_size]


def list_subdirs(directory):

    directory = os.path.abspath(directory)
    abs_sub_dirs = [os.path.join(directory, n) for n in os.listdir(directory)]
    return [n for n in abs_sub_dirs if os.path.isdir(os.path.realpath(n))]


def get_local_git_info(directory, json_out_f=None):
    """ Extract git related information from a target directory. It allows
    optional export to json file """

    directory = os.path.abspath(directory)
    cur_dir = os.path.abspath(os.getcwd())
    os.chdir(directory)

    # System commands to collect information
    cmd1 = "git log HEAD -n 1 --pretty=format:'%H%x09%an%x09%ae%x09%ai%x09%s'"
    cmd2 = "git log HEAD -n 1  --pretty=format:'%b'"
    cmd3 = "git remote -v | head -n 1 | awk '{ print $2}';"
    cmd4 = ("git ls-remote --heads origin | "
            "grep $(git rev-parse HEAD) | cut -d / -f 3")

    git_info_rex = re.compile(r'(?P<body>^[\s\S]*?)((?:Change-Id:\s)'
                              r'(?P<change_id>.*)\n)((?:Signed-off-by:\s)'
                              r'(?P<sign_off>.*)\n?)', re.MULTILINE)

    proc_res = []
    for cmd in [cmd1, cmd2, cmd3, cmd4]:
        r, e = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()
        if e:
            print("Error", e)
            return
        else:
            try:
                txt_body = r.decode('ascii')
            except UnicodeDecodeError as E:
                txt_body = r.decode('utf-8')
            proc_res.append(txt_body.rstrip())

    # Unpack and tag the data
    hash, name, email, date, subject = proc_res[0].split('\t')

    _raw_body = proc_res[1]
    _bd_items = re.findall(r'(Signed-off-by|Change-Id)', _raw_body,
                           re.MULTILINE)

    signed_off = None
    body = None
    change_id = None
    # If both sign-off and gerrit-id exist
    if len(_bd_items) == 2:
        m = git_info_rex.search(_raw_body)
        print(git_info_rex.findall(_raw_body))
        if m is not None:
            match_dict = m.groupdict()
            if "body" in match_dict.keys():
                body = match_dict["body"]
            if "sign_off" in match_dict.keys():
                signed_off = match_dict["sign_off"]
            if "change_id" in match_dict.keys():
                change_id = match_dict["change_id"]
        else:
            print("Error: Could not regex parse message", repr(_raw_body))
            body = _raw_body
    # If only one of sign-off / gerrit-id exist
    elif len(_bd_items) == 1:
        _entry_key = _bd_items[0]
        body, _extra = _raw_body.split(_entry_key)
        if _entry_key == "Change-Id":
            change_id = _extra
        else:
            signed_off = _extra
    # If the message contains commit message body only
    else:
        body = _raw_body

    # Attempt to read the branch from Gerrit Trigger
    try:
        branch = os.environ["GERRIT_BRANCH"]
    # IF not compare the commit hash with the remote branches to determine the
    # branch of origin. Warning this assumes that only one branch has its head
    # on this commit.
    except KeyError as E:
        branch = proc_res[3]

    remote = proc_res[2]
    # Internal Gerrit specific code
    # Intended for converting the git remote to a more usuable url
    known_remotes = ["https://gerrit.oss.arm.com",
                     "http://gerrit.mirror.oss.arm.com"]

    for kr in known_remotes:
        if kr in remote:
            print("Applying Remote specific patch to remote", kr)

            remote = remote.split(kr)[-1][1:]
            print("REMOTE", remote)
            remote = "%s/gitweb?p=%s.git;a=commit;h=%s" % (kr, remote, hash)
            break

    out = {"author": name.strip(),
           "email": email.strip(),
           "dir": directory.strip(),
           "remote": remote.strip(),
           "date": date.strip(),
           "commit": hash.strip(),
           "subject": subject.strip(),
           "message": body.strip(),
           "change_id": change_id.strip() if change_id is not None else "N.A",
           "sign_off": signed_off.strip() if signed_off is not None else "N.A",
           "branch": branch.strip()}

    # Restore the directory path
    os.chdir(cur_dir)
    if json_out_f:
        save_json(json_out_f, out)
    return out


def get_remote_git_info(url):
    """ Collect git information from a Linux Kernel web repository """

    auth_rex = re.compile(r'(?:<th>author</th>.*)(?:span>)(.*)'
                          r'(?:;.*\'right\'>)([0-9\+\-:\s]+)')
    # commiter_rex = re.compile(r'(?:<th>committer</th>.*)(?:</div>)(.*)'
    #                          r'(?:;.*\'right\'>)([0-9\+\-:\s]+)')
    subject_rex = re.compile(r'(?:\'commit-subject\'>)(.*)(?:</div>)')
    body_rex = re.compile(r'(?:\'commit-msg\'>)([\s\S^<]*)(?:</div>'
                          r'<div class=\'diffstat-header\'>)', re.MULTILINE)

    content = requests.get(url).text
    author, date = re.search(auth_rex, content).groups()
    subject = re.search(subject_rex, content).groups()[0]
    body = re.search(body_rex, content).groups()[0]
    remote, hash = url.split("=")

    outdict = {"author": author,
               "remote": remote[:-3],
               "date": date,
               "commit": hash,
               "subject": subject,
               "message": body}
    # Clean up html noise
    return {k: re.sub(r'&[a-z]t;?', "", v) for k, v in outdict.items()}


def convert_git_ref_path(dir_path):
    """ If a git long hash is detected in a path move it to a short hash """

    # Detect a git hash on a directory naming format of name_{hash},
    # {hash}, name-{hash}
    git_hash_rex = re.compile(r'(?:[_|-])*([a-f0-9]{40})')

    # if checkout directory name contains a git reference convert to short
    git_hash = git_hash_rex.findall(dir_path)
    if len(git_hash):
        d = dir_path.replace(git_hash[0], git_hash[0][:7])
        print("Renaming %s -> %s", dir_path, d)
        move(dir_path, d)
        dir_path = d
    return dir_path


def xml_read(file):
    """" Read the contects of an xml file and convert it to python object """

    data = None
    try:
        with open(file, "r") as F:
            data = xmltodict.parse(F.read())
    except Exception as E:
        print("Error", E)
    return data


def list_filtered_tree(directory, rex_filter=None):
    ret = []
    for path, subdirs, files in os.walk(directory):
        for fname in files:
            ret.append(os.path.join(path, fname))
    if rex_filter:
        rex = re.compile(rex_filter)
        return [n for n in ret if rex.search(n)]
    else:
        return ret


def gerrit_patch_from_changeid(remote, change_id):
    """ Use Gerrit's REST api for a best effort to retrieve the url of the
    patch-set under review """

    try:
        r = requests.get('%s/changes/%s' % (remote, change_id),
                         headers={'Accept': 'application/json'})
        resp_data = r.text[r.text.find("{"):].rstrip()
        change_no = json.loads(resp_data)["_number"]
        return "%s/#/c/%s" % (remote, change_no)
    except Exception as E:
        print("Failed to retrieve change (%s) from URL %s" % (change_id,
                                                              remote))
        print("Exception Thrown:", E)
        raise Exception()
