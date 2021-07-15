#!/usr/bin/env python3

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2020-2021, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

"""
Script to create LAVA definitions from a single tf-m-build-config Jenkins Job
"""

import os
import sys
import argparse
from jinja2 import Environment, FileSystemLoader
from lava_helper_configs import *

try:
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.lava_rpc_connector import LAVA_RPC_connector


def load_config_overrides(user_args, config_key):
    """Load a configuration from multiple locations and override it with user provided
    arguments"""

    print("Using built-in config: %s" % config_key)
    try:
        config = lava_gen_config_map[config_key]
    except KeyError:
        print("No template found for config: %s" % config_key)
        sys.exit(1)

    config["build_no"] = user_args.build_no
    config["artifact_store_url"] = user_args.jenkins_build_url

    # Add the template folder
    config["templ"] = os.path.join(user_args.template_dir, config["templ"])
    return config


def get_artifact_url(artifact_store_url, params, filename):
    platform = params["platform"]
    if params["device_type"] == "fvp":
        platform = "fvp"

    url = "{}/artifact/trusted-firmware-m/build/bin/{}".format(artifact_store_url.rstrip("/"), filename)
    return url


def get_recovery_url(recovery_store_url, recovery):
    return "{}/{}".format(recovery_store_url.rstrip('/'), recovery)


def get_job_name(name, params, job):
    return "{}_{}_{}_{}_{}_{}_{}_{}".format(
        name,
        job,
        params["platform"],
        params["build_no"],
        params["compiler"],
        params["build_type"],
        params["boot_type"],
        params["name"],
    )


def get_build_name(params):
    return "{}_{}_{}_{}_{}".format(
        params["platform"],
        params["compiler"],
        params["name"],
        params["build_type"],
        params["boot_type"],
    )


def generate_test_definitions(config, work_dir, user_args):
    """Get a dictionary configuration and an existing jinja2 template to generate
    a LAVA compatible yaml definition"""

    template_loader = FileSystemLoader(searchpath=work_dir)
    template_env = Environment(loader=template_loader)
    recovery_store_url = config.get('recovery_store_url', '')
    build_no = user_args.build_no
    artifact_store_url = config["artifact_store_url"]
    template_file = config.pop("templ")

    definitions = {}

    for platform, recovery in config["platforms"].items():
        if platform != user_args.platform:
            continue
        recovery_image_url = get_recovery_url(recovery_store_url, recovery)
        for compiler in config["compilers"]:
            if compiler != user_args.compiler:
                continue
            for build_type in config["build_types"]:
                if build_type != user_args.build_type:
                    continue
                for boot_type in config["boot_types"]:
                    bl2_string = "BL2" if user_args.bl2 else "NOBL2"
                    if boot_type != bl2_string:
                        continue
                    for test_name, test_dict in config["tests"].items():
                        if "Config{}".format(test_name) != user_args.proj_config:
                            continue
                        params = {
                            "device_type": config["device_type"],
                            "job_timeout": config["job_timeout"],
                            "action_timeout": config.get("action_timeout", ''),
                            "monitor_timeout": config.get("monitor_timeout", ''),
                            "poweroff_timeout": config.get("poweroff_timeout", ''),
                            "compiler": compiler,
                            "build_type": build_type,
                            "build_no": build_no,
                            "boot_type": boot_type,
                            "name": test_name,
                            "test": test_dict,
                            "platform": platform,
                            "recovery_image_url": recovery_image_url,
                            "data_bin_offset": config.get('data_bin_offset', ''),
                            "docker_prefix": vars(user_args).get('docker_prefix', ''),
                            "license_variable": vars(user_args).get('license_variable', ''),
                            "enable_code_coverage": user_args.enable_code_coverage == "TRUE",
                            "coverage_trace_plugin": coverage_trace_plugin,
                            "build_job_url": artifact_store_url,
                            "cpu0_baseline": config.get("cpu0_baseline", 0),
                            "cpu0_initvtor_s": config.get("cpu0_initvtor_s", "0x10000000")
                        }
                        params.update(
                            {
                                "firmware_url": get_artifact_url(
                                    artifact_store_url,
                                    params,
                                    test_dict.get("binaries").get("firmware"),
                                ),
                                "tarball_url": get_artifact_url(
                                    artifact_store_url,
                                    params,
                                    test_dict.get("binaries").get("tarball"),
                                ),
                            }
                        )
                        params.update(
                            {
                                "bootloader_url": get_artifact_url(
                                    artifact_store_url,
                                    params,
                                    test_dict.get("binaries").get("bootloader"),
                                ),
                            }
                        )
                        params.update(
                            {
                                "job_name": get_job_name(
                                    config["job_name"], params, user_args.jenkins_job,
                                ),
                                "build_name": get_build_name(params)
                            }
                        )

                        definition = template_env.get_template(template_file).render(
                            params
                        )
                        definitions.update({params["job_name"]: definition})
    return definitions


def generate_lava_job_defs(user_args, config):
    """Create a LAVA test job definition file"""

    # Evaluate current directory
    work_dir = os.path.abspath(os.path.dirname(__file__))

    # If a single platform is requested and it exists in the platform
    if user_args.platform and user_args.platform in config["platforms"]:
        # Only test this platform
        platform = user_args.platform
        config["platforms"] = {platform: config["platforms"][platform]}
    # Generate the output definition
    definitions = generate_test_definitions(config, work_dir, user_args)

    # Write it into a file
    out_dir = os.path.abspath(user_args.lava_def_output)
    os.makedirs(out_dir, exist_ok=True)
    for name, definition in definitions.items():
        out_file = os.path.join(out_dir, "{}{}".format(name, ".yaml"))
        with open(out_file, "w") as F:
            F.write(definition)
        print("Definition created at %s" % out_file)


def main(user_args):
    user_args.template_dir = "jinja2_templates"
    config_keys = list(lava_gen_config_map.keys())
    if user_args.fvp_only:
        for key in config_keys:
            if "fvp" not in key:
                config_keys.remove(key)
    if user_args.config_key:
        config_keys = [user_args.config_key]
    for config_key in config_keys:
        config = load_config_overrides(user_args, config_key)
        generate_lava_job_defs(user_args, config)


def get_cmd_args():
    """Parse command line arguments"""

    # Parse command line arguments to override config
    parser = argparse.ArgumentParser(description="Lava Create Jobs")
    cmdargs = parser.add_argument_group("Create LAVA Jobs")

    # Configuration control
    cmdargs.add_argument(
        "--config-name",
        dest="config_key",
        action="store",
        help="Select built-in configuration by name",
    )
    cmdargs.add_argument(
        "--build-number",
        dest="build_no",
        action="store",
        default="lastSuccessfulBuild",
        help="JENKINS Build number selector. " "Default: lastSuccessfulBuild",
    )
    cmdargs.add_argument(
        "--output-dir",
        dest="lava_def_output",
        action="store",
        default="job_results",
        help="Set LAVA compatible .yaml output file",
    )
    cmdargs.add_argument(
        "--platform",
        dest="platform",
        action="store",
        help="Override platform.Only the provided one " "will be tested",
    )
    cmdargs.add_argument(
        "--compiler",
        dest="compiler",
        action="store",
        help="Compiler to build definitions for",
    )
    cmdargs.add_argument(
        "--jenkins-build-url",
        dest="jenkins_build_url",
        action="store",
        help="Set the Jenkins URL",
    )
    cmdargs.add_argument(
        "--jenkins-job",
        dest="jenkins_job",
        action="store",
        default="tf-m-build-config",
        help="Set the jenkins job name",
    )
    cmdargs.add_argument(
        "--fvp-only",
        dest="fvp_only",
        action="store_true",
        help="Run test cases on FVP only",
    )
    cmdargs.add_argument(
        "--proj-config", dest="proj_config", action="store", help="Proj config"
    )
    cmdargs.add_argument(
        "--build-type", dest="build_type", action="store", help="Build type"
    )
    cmdargs.add_argument(
        "--docker-prefix", dest="docker_prefix", action="store", help="Prefix string for the FVP docker registry location"
    )
    cmdargs.add_argument(
        "--license-variable", dest="license_variable", action="store", help="License string for Fastmodels"
    )
    cmdargs.add_argument(
        "--enable-code-coverage", dest="enable_code_coverage", action="store", default="FALSE", help="Enable trace-base code coverage"
    )
    cmdargs.add_argument("--bl2", dest="bl2", action="store_true", help="BL2")
    cmdargs.add_argument(
        "--psa-api-suite", dest="psa_suite", action="store", help="PSA API Suite name"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(get_cmd_args())
