#!/usr/bin/env python3

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2020-2022, Arm Limited. All rights reserved.
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


def get_recovery_url(recovery_store_url, recovery):
    return "{}/{}".format(recovery_store_url.rstrip('/'), recovery)


def load_config_overrides(user_args, config_key):
    """Load a configuration from multiple locations and override it with user provided
    arguments"""

    print("Using built-in config: %s" % config_key)
    try:
        config = lava_gen_config_map_bl2[config_key] if os.getenv("BL2") == "True" \
                 else lava_gen_config_map_nobl2[config_key]
    except KeyError:
        print("No template found for config: %s" % config_key)
        sys.exit(1)

    # Add the template folder
    config["templ"] = os.path.join(user_args.template_dir, config["templ"])
    return config


def generate_test_definitions(config, work_dir, user_args):
    """Get a dictionary configuration and an existing jinja2 template to generate
    a LAVA compatible yaml definition"""

    template_loader = FileSystemLoader(searchpath=work_dir)
    template_env = Environment(loader=template_loader)
    recovery_store_url = config.get('recovery_store_url', '')
    template_file = config.pop("templ")

    definitions = {}

    for platform, recovery in config["platforms"].items():
        if platform != os.getenv('TFM_PLATFORM'):
            continue
        recovery_image_url = get_recovery_url(recovery_store_url, recovery)
        if os.getenv("TEST_PSA_API") != "OFF":
            monitor_name = "arch_tests"
        elif os.getenv("TEST_REGRESSION") == "OFF":
            monitor_name = "no_reg_tests"
        else:
            monitor_name = "reg_tests"
        params = {
            "job_name": "{}_{}_{}".format(os.getenv('CONFIG_NAME'), os.getenv("BUILD_NUMBER"), config["device_type"]),
            "build_name": os.getenv('CONFIG_NAME'),
            "device_type": config["device_type"],
            "job_timeout": config["job_timeout"],
            "action_timeout": config.get("action_timeout", ''),
            "monitor_timeout": config.get("monitor_timeout", ''),
            "poweroff_timeout": config.get("poweroff_timeout", ''),
            "build_no": os.getenv("BUILD_NUMBER"),
            "name": monitor_name,
            "monitors": config['monitors'].get(monitor_name, []),
            "platform": platform,
            "recovery_image_url": recovery_image_url,
            "data_bin_offset": config.get('data_bin_offset', ''),
            "docker_prefix": vars(user_args).get('docker_prefix', ''),
            "license_variable": vars(user_args).get('license_variable', ''),
            "enable_code_coverage": user_args.enable_code_coverage == "TRUE",
            "coverage_trace_plugin": coverage_trace_plugin,
            "build_job_url": os.getenv("BUILD_URL"),
            "cpu0_baseline": config.get("cpu0_baseline", 0),
            "cpu0_initvtor_s": config.get("cpu0_initvtor_s", "0x10000000"),
            "psa_api_suite": os.getenv("TEST_PSA_API") if os.getenv("TEST_PSA_API") == "IPC" else "",
        }
        for binary_type, binary_name in config["binaries"].items():
            params.update(
                {
                    "{}_url".format(binary_type): "{}/artifact/ci_build/{}".format(params["build_job_url"], binary_name)
                }
            )

        if len(params["monitors"]) == 0:
            break

        definition = template_env.get_template(template_file).render(
            params
        )
        definitions.update({params["job_name"]: definition})

    return definitions


def generate_lava_job_defs(user_args, config):
    """Create a LAVA test job definition file"""

    # Evaluate current directory
    work_dir = os.path.abspath(os.path.dirname(__file__))

    # If platform exists in the LAVA platforms
    if os.getenv("TFM_PLATFORM") in config["platforms"]:
        # Only test this platform
        platform = os.getenv("TFM_PLATFORM")
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
    config_keys = list(lava_gen_config_map_bl2.keys()) if os.getenv("BL2") == "True" \
                  else list(lava_gen_config_map_nobl2.keys())
    if user_args.fvp_only:
        config_keys = [key for key in config_keys if "fvp" in key]
    if user_args.physical_board_only:
        config_keys = [key for key in config_keys
                       if "fvp" not in key and "qemu" not in key]
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
    device_type = parser.add_mutually_exclusive_group()

    # Configuration control
    cmdargs.add_argument(
        "--config-name",
        dest="config_key",
        action="store",
        help="Select built-in configuration by name",
    )
    cmdargs.add_argument(
        "--output-dir",
        dest="lava_def_output",
        action="store",
        default="job_results",
        help="Set LAVA compatible .yaml output file",
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
        "--docker-prefix", dest="docker_prefix", action="store", help="Prefix string for the FVP docker registry location"
    )
    cmdargs.add_argument(
        "--license-variable", dest="license_variable", action="store", help="License string for Fastmodels"
    )
    cmdargs.add_argument(
        "--enable-code-coverage", dest="enable_code_coverage", action="store", default="FALSE", help="Enable trace-base code coverage"
    )

    device_type.add_argument(
        "--fvp-only",
        dest="fvp_only",
        action="store_true",
        help="Run test cases on FVP only",
    )
    device_type.add_argument(
        "--physical-board-only",
        dest="physical_board_only",
        action="store_true",
        help="Run test cases on physical boards only",
    )

    return parser.parse_args()

if __name__ == "__main__":
    main(get_cmd_args())
