#!/usr/bin/env python3 -u

""" lava_helper.py:

    Generate custom defined LAVA definitions rendered from Jinja2 templates.
    It can also parse the yaml output of LAVA and verify the test outcome """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2021, Arm Limited. All rights reserved.
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
import shutil
import argparse
from copy import deepcopy
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader
from lava_helper_configs import *

try:
    from tfm_ci_pylib.utils import save_json, load_json, sort_dict,\
        load_yaml, test, print_test
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.utils import save_json, load_json, sort_dict,\
        load_yaml, test, print_test
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector


def sort_lavagen_config(cfg):
    """ Create a constact dictionary object. This method is tailored for
    the complicated configuration structure of this module """

    res = OrderedDict()
    if sorted(lavagen_config_sort_order) == sorted(cfg.keys()):
        item_list = sorted(cfg.keys(),
                           key=lambda x: lavagen_config_sort_order.index(x))
    else:
        item_list = sorted(cfg.keys(), key=len)
    for k in item_list:
        v = cfg[k]
        if isinstance(v, dict):
            res[k] = sort_lavagen_config(v)
        elif isinstance(v, list) and isinstance(v[0], dict):
            res[k] = [sort_dict(e, lava_gen_monitor_sort_order) for e in v]
        else:
            res[k] = v
    return res


def save_config(cfg_f, cfg_obj):
    """ Export configuration to json file """
    save_json(cfg_f, sort_lavagen_config(cfg_obj))


def print_configs():
    """ Print supported configurations """

    print("%(pad)s Built-in configurations: %(pad)s" % {"pad": "*" * 10})
    for k in lava_gen_config_map.keys():
        print("\t * %s" % k)


def get_artifact_url(artifact_store_url, params, filename):
    url = "{}/{}/artifact/build-ci-all/{}_{}_Config{}_{}_{}/bin/{}/{}".format(
        artifact_store_url,
        params['build_no'],
        params['platform'],
        params['compiler'],
        params['name'],
        params['build_type'],
        params['boot_type'],
        params['platform'],
        filename,
    )
    return url

def get_recovery_url(recovery_store_url, build_no, recovery):
    return("{}/{}/artifact/{}".format(
        recovery_store_url,
        build_no,
        recovery
    ))

def get_job_name(name, params, job):
    return("{}_{}_{}_{}_{}_{}_{}_{}".format(
        name,
        job,
        params['platform'],
        params['build_no'],
        params['compiler'],
        params['build_type'],
        params['boot_type'],
        params['name'],
        ))

def generate_test_definitions(config, work_dir, user_args):
    """ Get a dictionary configuration, and an existing jinja2 template
    and generate a LAVA compatbile yaml definition """

    template_loader = FileSystemLoader(searchpath=work_dir)
    template_env = Environment(loader=template_loader)
    recovery_store_url = "{}/job/{}".format(
        user_args.jenkins_url,
        user_args.jenkins_job
    )
    build_no = user_args.build_no
    artifact_store_url = recovery_store_url
    template_file = config.pop("templ")

    definitions = {}

    for platform, recovery in config['platforms'].items():
        recovery_image_url = get_recovery_url(
            recovery_store_url,
            build_no,
            recovery)
        for compiler in config['compilers']:
            for build_type in config['build_types']:
                for boot_type in config['boot_types']:
                    for test_name, test_dict in config['tests'].items():
                        params = {
                            "device_type": config['device_type'],
                            "job_timeout": config['job_timeout'],
                            "action_timeout": config['action_timeout'],
                            "monitor_timeout": config['monitor_timeout'],
                            "poweroff_timeout": config['poweroff_timeout'],
                            'compiler': compiler,
                            'build_type': build_type,
                            'build_no': build_no,
                            'boot_type': boot_type,
                            'name': test_name,
                            'test': test_dict,
                            'platform': platform,
                            'recovery_image_url': recovery_image_url,
                            }
                        params.update({
                            'firmware_url': get_artifact_url(
                                artifact_store_url,
                                params,
                                test_dict['binaries']['firmware']
                                ),
                            'bootloader_url': get_artifact_url(
                                artifact_store_url,
                                params,
                                test_dict['binaries']['bootloader']
                                )
                        })
                        params.update({
                            'job_name': get_job_name(
                                config['job_name'],
                                params,
                                user_args.jenkins_job,
                                )
                        })

                        definition = template_env.get_template(template_file).render(params)
                        definitions.update({params['job_name']: definition})
    return definitions


def generate_lava_job_defs(user_args, config):
    """ Create a LAVA test job definition file """

    # Evaluate current directory
    if user_args.work_dir:
        work_dir = os.path.abspath(user_args.work_dir)
    else:
        work_dir = os.path.abspath(os.path.dirname(__file__))

    # If a single platform is requested and it exists in the platform
    if user_args.platform and user_args.platform in config["platforms"]:
        # Only test this platform
        platform = user_args.platform
        config["platforms"] = {platform: config["platforms"][platform]}

    # Generate the ouptut definition
    definitions = generate_test_definitions(config, work_dir, user_args)

    # Write it into a file
    out_dir = os.path.abspath(user_args.lava_def_output)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    for name, definition in definitions.items():
        out_file = os.path.join(out_dir, "{}{}".format(name, ".yaml"))
        with open(out_file, "w") as F:
           F.write(definition)
        print("Definition created at %s" % out_file)


def test_map_from_config(lvg_cfg=tfm_mps2_sse_200):
    """ Extract all required information from a lavagen config map
    and generate a map of required tests, indexed by test name """

    test_map = {}
    suffix_l = []
    for p in lvg_cfg["platforms"]:
        for c in lvg_cfg["compilers"]:
            for bd in lvg_cfg["build_types"]:
                for bt in lvg_cfg["boot_types"]:
                    suffix_l.append("%s_%s_%s_%s_%s" % (p, c, "%s", bd, bt))

    for test_cfg_name, tst in lvg_cfg["tests"].items():
        for monitor in tst["monitors"]:
            for suffix in suffix_l:
                key = (monitor["name"] + "_" + suffix % test_cfg_name).lower()
                # print (monitor['required'])
                test_map[key] = monitor['required']

    return deepcopy(test_map)


def test_lava_results(user_args, config):
    """ Uses input of a test config dictionary and a LAVA summary Files
    and determines if the test is a successful or not """

    # Parse command line arguments to override config
    result_raw = load_yaml(user_args.lava_results)

    test_map = test_map_from_config(config)
    t_dict = {k: {} for k in test_map}

    # Return true if test is contained in test_groups
    def test_filter(x):
        return x["metadata"]['definition'] in test_map

    # Create a dictionary with common keys as the test map and test results
    # {test_suite: {test_name: pass/fail}}
    def format_results(x):
        t_dict[x["metadata"]["definition"]].update({x["metadata"]["case"]:
                                                    x["metadata"]["result"]})

    # Remove all irelevant entries from data
    test_results = list(filter(test_filter, result_raw))

    # Call the formatter
    list(map(format_results, test_results))

    # Remove the ignored commits if requested
    if user_args.ignore_configs:
        print(user_args.ignore_configs)
        for cfg in user_args.ignore_configs:
            try:
                print("Rejecting config: ", cfg)
                t_dict.pop(cfg)
            except KeyError as e:
                print("Warning! Rejected config %s not found"
                      " in LAVA results" % cfg)

    #  We need to check that each of the tests contained in the test_map exist
    #  AND that they have a passed status
    t_sum = 0

    with open("lava_job.url", "r") as F:
        job_url = F.read().strip()

    out_rep = {"report": {},
               "_metadata_": {"job_url": job_url}}
    for k, v in t_dict.items():
        try:
            out_rep["report"][k] = test(test_map[k],
                                        v,
                                        pass_text=["pass"],
                                        error_on_failed=False,
                                        test_name=k,
                                        summary=user_args.lava_summary)
            t_sum += int(out_rep["report"][k]["success"])
        # Status can be None if a test did't fully run/complete
        except TypeError as E:
            t_sum = 1
    print("\n")
    sl = [x["name"] for x in out_rep["report"].values()
          if x["success"] is True]
    fl = [x["name"] for x in out_rep["report"].values()
          if x["success"] is False]

    if sl:
        print_test(t_list=sl, status="passed", tname="Tests")
    if fl:
        print_test(t_list=fl, status="failed", tname="Tests")

    # Generate the output report is requested
    if user_args.output_report:
        save_json(user_args.output_report, out_rep)

    # Every single of the tests need to have passed for group to succeed
    if t_sum != len(t_dict):
        print("Group Testing FAILED!")
        if user_args.eif:
            sys.exit(1)
    else:
        print("Group Testing PASS!")


def test_lava_dispatch_credentials(user_args):
    """ Will validate if provided token/credentials are valid. It will return
    a valid connection or exit program if not"""

    # Collect the authentication tokens
    try:
        if user_args.token_from_env:
            usr = os.environ['LAVA_USER']
            secret = os.environ['LAVA_TOKEN']
        elif user_args.lava_user and user_args.lava_token:
            usr = user_args.lava_user
            secret = user_args.lava_token

        # Do not submit job without complete credentials
        if not len(usr) or not len(secret):
            raise Exception("Credentials not set")

        lava = LAVA_RPC_connector(usr,
                                  secret,
                                  user_args.lava_url,
                                  user_args.lava_rpc)

        # Test the credentials againist the backend
        if not lava.test_credentials():
            raise Exception("Server rejected user authentication")
    except Exception as e:
        print("Credential validation failed with : %s" % e)
        print("Did you set set --lava_user, --lava_token?")
        sys.exit(1)
    return lava


def lava_dispatch(user_args):
    """ Submit a job to LAVA backend, block untill it is completed, and
    fetch the results files if successful. If not, calls sys exit with 1
    return code """

    lava = test_lava_dispatch_credentials(user_args)
    job_id, job_url = lava.submit_job(user_args.dispatch)

    # The reason of failure will be reported to user by LAVA_RPC_connector
    if job_id is None and job_url is None:
        sys.exit(1)
    else:
        print("Job submitted at: " + job_url)

    with open("lava_job.id", "w") as F:
        F.write(str(job_id))
    print("Job id %s stored at lava_job.id file." % job_id)
    with open("lava_job.url", "w") as F:
        F.write(str(job_url))
    print("Job url %s stored at lava_job.url file." % job_id)

    # Wait for the job to complete
    status = lava.block_wait_for_job(job_id, int(user_args.dispatch_timeout))
    print("Job %s returned with status: %s" % (job_id, status))
    if status == "Complete":
        lava.get_job_results(job_id, user_args.lava_job_results)
        print("Job results exported at: %s" % user_args.lava_job_results)
        sys.exit(0)
    sys.exit(1)


def dispatch_cancel(user_args):
    """ Sends a cancell request for user provided job id (dispatch_cancel)"""
    lava = test_lava_dispatch_credentials(user_args)
    id = user_args.dispatch_cancel
    result = lava.cancel_job(id)
    print("Request to cancell job: %s returned with status %s" % (id, result))


def load_config_overrides(user_args):
    """ Load a configuration from multiple locations and override it with
    user provided arguemnts """

    if user_args.config_file:
        print("Loading config from file %s" % user_args.config_file)
        try:
            config = load_json(user_args.config_file)
        except Exception:
            print("Failed to load config from: %s ." % user_args.config_file)
            sys.exit(1)
    else:
        print("Using built-in config: %s" % user_args.config_key)
        try:
            config = lava_gen_config_map[user_args.config_key]
        except KeyError:
            print("No template found for config: %s" % user_args.config_key)
            sys.exit(1)

    config["build_no"] = user_args.build_no

    # Override with command line provided URL/Job Name
    if user_args.jenkins_url:
        _over_d = {"jenkins_url": user_args.jenkins_url,
                   "jenkins_job": "%(jenkins_job)s"}
        config["recovery_store_url"] = config["recovery_store_url"] % _over_d
        config["artifact_store_url"] = config["artifact_store_url"] % _over_d

    if user_args.jenkins_job:
        _over_d = {"jenkins_job": user_args.jenkins_job}
        config["recovery_store_url"] = config["recovery_store_url"] % _over_d
        config["artifact_store_url"] = config["artifact_store_url"] % _over_d

    #  Add the template folder
    config["templ"] = os.path.join(user_args.template_dir, config["templ"])
    return config


def main(user_args):
    """ Main logic, forked according to task arguments """

    # If a configuration listing is requested
    if user_args.ls_config:
        print_configs()
        return
    elif user_args.cconfig:
        config_key = user_args.cconfig
        if config_key in lava_gen_config_map.keys():
            config_file = "lava_job_gen_cfg_%s.json" % config_key
            save_config(config_file, lava_gen_config_map[config_key])
            print("Configuration exported at %s" % config_file)
        return
    if user_args.dispatch is not None or user_args.dispatch_cancel is not None:
        pass
    else:
        config = load_config_overrides(user_args)

    # Configuration is assumed fixed at this point
    if user_args.lava_results:
        print("Evaluating File", user_args.lava_results)
        test_lava_results(user_args, config)
    elif user_args.dispatch:
        lava_dispatch(user_args)
    elif user_args.dispatch_cancel:
        dispatch_cancel(user_args)
    elif user_args.create_definition:
        print("Generating Lava")
        generate_lava_job_defs(user_args, config)
    else:
        print("Nothing to do, please select a task")


def get_cmd_args():
    """ Parse command line arguments """

    # Parse command line arguments to override config
    parser = argparse.ArgumentParser(description="Lava Helper")

    def_g = parser.add_argument_group('Create LAVA Definition')
    disp_g = parser.add_argument_group('Dispatch LAVA job')
    parse_g = parser.add_argument_group('Parse LAVA results')
    config_g = parser.add_argument_group('Configuration handling')
    over_g = parser.add_argument_group('Overrides')

    # Configuration control
    config_g.add_argument("-cn", "--config-name",
                          dest="config_key",
                          action="store",
                          default="tfm_mps2_sse_200",
                          help="Select built-in configuration by name")
    config_g.add_argument("-cf", "--config-file",
                          dest="config_file",
                          action="store",
                          help="Load config from external file in JSON format")
    config_g.add_argument("-te", "--task-config-export",
                          dest="cconfig",
                          action="store",
                          help="Export a json file with the current config "
                               "parameters")
    config_g.add_argument("-tl", "--task-config-list",
                          dest="ls_config",
                          action="store_true",
                          default=False,
                          help="List built-in configurations")

    def_g.add_argument("-tc", "--task-create-definition",
                       dest="create_definition",
                       action="store_true",
                       default=False,
                       help="Used in conjunction with --config parameters. "
                            "A LAVA compatible job definition will be created")
    def_g.add_argument("-cb", "--create-definition-build-no",
                       dest="build_no",
                       action="store",
                       default="lastSuccessfulBuild",
                       help="JENKINGS Build number selector. "
                            "Default: lastSuccessfulBuild")
    def_g.add_argument("-co", "--create-definition-output-dir",
                       dest="lava_def_output",
                       action="store",
                       default="job_results",
                       help="Set LAVA compatible .yaml output file")

    # Parameter override commands
    over_g.add_argument("-ow", "--override-work-path",
                        dest="work_dir",
                        action="store",
                        help="Working Directory (absolute path)")
    over_g.add_argument("-ot", "--override-template-dir",
                        dest="template_dir",
                        action="store",
                        default="jinja2_templates",
                        help="Set directory where Jinja2 templates are stored")
    over_g.add_argument("-op", "--override-platform",
                        dest="platform",
                        action="store",
                        help="Override platform.Only the provided one "
                             "will be tested")
    over_g.add_argument("-ou", "--override-jenkins-url",
                        dest="jenkins_url",
                        action="store",
                        help="Override %%(jenkins_url)s params in config if "
                             "present. Sets the jenkings address including "
                             "port")
    over_g.add_argument("-oj", "--override-jenkins-job",
                        dest="jenkins_job",
                        action="store",
                        help="Override %%(jenkins_job)s params in config if "
                             "present. Sets the jenkings job name")
    parse_g.add_argument("-tp", "--task-lava-parse",
                         dest="lava_results",
                         action="store",
                         help="Parse provided yaml file, using a configuration"
                              " as reference to determine the outpcome"
                              " of testing")
    parse_g.add_argument("-ls", "--lava-parse-summary",
                         dest="lava_summary",
                         default=False,
                         action="store_true",
                         help="Print full test summary")
    parse_g.add_argument("-or", "--output-report",
                         dest="output_report",
                         action="store",
                         help="Print full test summary")
    parser.add_argument("-ef", "--error-if-failed",
                        dest="eif",
                        action="store_true",
                        help="If set will change the script exit code if one "
                             "or more tests fail")
    parser.add_argument('-ic', '--ignore-configs',
                        dest="ignore_configs",
                        nargs='+',
                        help="Pass a space separated list of build"
                             "configurations which will get ignored when"
                             "evaluation LAVA results")

    # Lava job control commands
    disp_g.add_argument("-td", "--task-dispatch",
                        dest="dispatch",
                        action="store",
                        help="Submit yaml file defined job to backend, and "
                             "wait for it to complete. \nRequires:"
                             " --lava_url --lava_token_usr/pass/--"
                             "lava_token_from_environ arguments, with optional"
                             "\n--lava_rpc_prefix\n--lava-job-results\n"
                             "parameters. \nIf not set they get RPC2 and "
                             "lava_job_results.yaml default values.\n"
                             "The number job id will be stored at lava_job.id")
    disp_g.add_argument("-dc", "--dispatch-cancel",
                        dest="dispatch_cancel",
                        action="store",
                        help="Send a cancell request for job with provided id")
    disp_g.add_argument("-dt", "--dispatch-timeout",
                        dest="dispatch_timeout",
                        default="3600",
                        action="store",
                        help="Maximum Time to block for job"
                        " submission to complete")
    disp_g.add_argument("-dl", "--dispatch-lava-url",
                        dest="lava_url",
                        action="store",
                        help="Sets the lava hostname during job dispatch")
    disp_g.add_argument("-dr", "--dispatch-lava-rpc-prefix",
                        dest="lava_rpc",
                        action="store",
                        default="RPC2",
                        help="Application prefix on Backend"
                             "(i.e www.domain.com/APP)\n"
                             "By default set to RPC2")
    disp_g.add_argument("-du", "--dispatch-lava_token_usr",
                        dest="lava_user",
                        action="store",
                        help="Lava user submitting the job")
    disp_g.add_argument("-ds", "--dispatch-lava_token_secret",
                        dest="lava_token",
                        action="store",
                        help="Hash token used to authenticate"
                             "user during job submission")
    disp_g.add_argument("-de", "--dispatch-lava_token_from_environ",
                        dest="token_from_env",
                        action="store_true",
                        help="If set dispatcher will use the enviroment"
                             "stored $LAVA_USER, $LAVA_TOKEN for credentials")
    disp_g.add_argument("-df", "--dispatch-lava-job-results-file",
                        dest="lava_job_results",
                        action="store",
                        default="lava_job_results.yaml",
                        help="Name of the job results file after job is "
                             "complete. Default: lava_job_results.yaml")
    return parser.parse_args()


if __name__ == "__main__":
    main(get_cmd_args())
