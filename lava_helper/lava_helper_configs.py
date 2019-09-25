#!/usr/bin/env python3

""" lava_job_generator_configs.py:

    Default configurations for lava job generator """

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


def lava_gen_get_config_subset(config,
                               default=True,
                               core=True,
                               regression=True):
    """ Allow dynamic generation of configuration combinations by subtracking
    undesired ones """

    from copy import deepcopy
    cfg = deepcopy(config)
    tests = deepcopy(config["tests"])

    # Remove all configs not requests by the caller
    if not default:
        tests.pop("Default")
    if not core:
        tests.pop("CoreIPC")
        tests.pop("CoreIPCTfmLevel2")
    if not regression:
        tests.pop("Regression")

    cfg["tests"] = tests
    return cfg


tfm_mps2_sse_200 = {
    "templ": "template_tfm_mps2_sse_200.jinja2",
    "job_name": "mps2plus-arm-tfm",
    "device_type": "mps",
    "job_timeout": 120,
    "action_timeout": 90,
    "monitor_timeout": 90,
    "poweroff_timeout": 10,
    "recovery_store_url": "%(jenkins_url)s/"
                          "job/%(jenkins_job)s",
    "artifact_store_url": "%(jenkins_url)s/"
                          "job/%(jenkins_job)s",
    "platforms": {"AN521": "mps2_an521_v3.0.tar.gz"},
    "compilers": ["GNUARM"],
    "build_types": ["Debug", "Release"],
    "boot_types": ["BL2"],
    "tests": {
        'Default': {
            "binaries": {
                "firmware": "tfm_sign.bin",
                "bootloader": "mcuboot.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Jumping to the first image slot',
                    'end': '\\x1b\\\[0m',
                    'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
                               r'(?P<test_case_id>Secure image '
                               r'initializing)(?P<result>!)',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # Default
        'Regression': {
            "binaries": {
                "firmware": "tfm_sign.bin",
                "bootloader": "mcuboot.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"[\x1b]\\[37mTest suite '(?P<"
                               r"test_case_id>[^\n]+)' has [\x1b]\\[32m "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                        "invert_secure_interface_tests_tfm_invert_test_1xxx_"
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"[\x1b]\\[37mTest suite '(?P"
                               r"<test_case_id>[^\n]+)' has [\x1b]\\[32m "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        ("invert_"
                         "non_secure_interface_tests_tfm_invert_test_1xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'CoreIPC': {
            "binaries": {
                "firmware": "tfm_sign.bin",
                "bootloader": "mcuboot.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Jumping to the first image slot',
                    'end': '\\x1b\\\[0m',
                    'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
                               r'(?P<test_case_id>Secure image '
                               r'initializing)(?P<result>!)',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPC
        'CoreIPCTfmLevel2': {
            "binaries": {
                "firmware": "tfm_sign.bin",
                "bootloader": "mcuboot.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Jumping to the first image slot',
                    'end': '\\x1b\\\[0m',
                    'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
                               r'(?P<test_case_id>Secure image '
                               r'initializing)(?P<result>!)',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel2
    }  # Tests
}

# All configurations should be mapped here
lava_gen_config_map = {"tfm_mps2_sse_200": tfm_mps2_sse_200}
lavagen_config_sort_order = [
    "templ",
    "job_name",
    "device_type",
    "job_timeout",
    "action_timeout",
    "monitor_timeout",
    "recovery_store_url",
    "artifact_store_url",
    "platforms",
    "compilers",
    "build_types",
    "boot_types",
    "tests"
]

lava_gen_monitor_sort_order = [
    'name',
    'start',
    'end',
    'pattern',
    'fixup',
]

if __name__ == "__main__":
    import os
    import sys
    from lava_helper import sort_lavagen_config
    try:
        from tfm_ci_pylib.utils import export_config_map
    except ImportError:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(os.path.join(dir_path, "../"))
        from tfm_ci_pylib.utils import export_config_map

    if len(sys.argv) == 2:
        if sys.argv[1] == "--export":
            export_config_map(lava_gen_config_map)
    if len(sys.argv) == 3:
        if sys.argv[1] == "--export":
            export_config_map(sort_lavagen_config(lava_gen_config_map),
                              sys.argv[2])
