#!/usr/bin/env python3

""" lava_job_generator_configs.py:

    Default configurations for lava job generator """

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

tf_downloads="https://downloads.trustedfirmware.org"
coverage_trace_plugin=tf_downloads + "/coverage-plugin/qa-tools/coverage-tool/coverage-plugin/coverage_trace.so"

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
        tests.pop("CoreIPCTfmLevel3")
    if not regression:
        tests.pop("Regression")

    cfg["tests"] = tests
    return cfg


# LAVA test-monitor definition for PSA API testsuites, testcases identified
# by "UT" value in output (testcase identifier).
monitors_psaapitest_by_ut = [
    {
        'name': 'psa_api_suite',
        'start': 'Running..',
        'end': 'Entering standby..',
        'pattern': r" UT: +(?P<test_case_id>[A-Za-z0-9_]+)\r?\n"
                   r".+?"
                   r"TEST RESULT: (?P<result>(PASSED|FAILED|SKIPPED))",
        'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
    },
]

# LAVA test-monitor definition for PSA API testsuites, testcases identified
# by description in output (for when UT is not set to unique identifier).
monitors_psaapitest_by_desc = [
    {
        'name': 'psa_api_suite',
        'start': 'Running..',
        'end': 'Entering standby..',
        'pattern': r" DESCRIPTION: +(?P<test_case_id>.+?) \\|"
                   r".+?"
                   r"TEST RESULT: (?P<result>(PASSED|FAILED|SKIPPED))",
        'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
    },
]

# LAVA test-monitor definition for PSA API "crypto" testsuite, which has some
# failing testcases which we don't want to treat as failures, so can't use
# normal monitors_psaapitest_by_ut. Note that this is a flaky workaround
# which will break if e.g. a new testcase is added. This issue should be
# fixed on TF-M side instead
monitors_psaapitest_crypto_workaround = [
    {
        'name': 'psa_api_crypto_workaround',
        'start': 'Running..',
        'end': r"TOTAL TESTS     : 63\r?\n.*?TOTAL PASSED    : 51\r?\n",
        'pattern': '__ignored__',
        'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
    },
]


# MPS2 with BL2 bootloader
# IMAGE0ADDRESS: 0x10000000
# IMAGE0FILE: \Software\bl2.bin  ; BL2 bootloader
# IMAGE1ADDRESS: 0x10080000
# IMAGE1FILE: \Software\tfm_s_ns_signed.bin ; TF-M example application binary blob
tfm_mps2_sse_200 = {
    "templ": "mps2.jinja2",
    "job_name": "mps2_an521_bl2",
    "device_type": "mps",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "recovery_store_url": "https://ci.trustedfirmware.org/userContent/",
    "platforms": {"AN521": "mps2_sse200_an512_new.tar.gz"},
    "compilers": ["GNUARM", "ARMCLANG"],
    "build_types": ["Debug", "Release", "Minsizerel"],
    "boot_types": ["BL2"],
    "tests": {
        'Default': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # Default
        'DefaultProfileS': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileS
        'DefaultProfileM': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileM
        'DefaultProfileL': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileL

        'Regression': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression

        'RegressionProfileM': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileM
        'RegressionProfileS': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileS
        'RegressionProfileL': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileL

        'RegressionIPC': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionIPCTfmLevel2': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionIPCTfmLevel3': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'CoreIPC': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPC
        'CoreIPCTfmLevel2': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel2
        'CoreIPCTfmLevel3': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel3

        'PsaApiTest_Crypto': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": monitors_psaapitest_crypto_workaround,
        }, # PsaApiTest_Crypto

        'PsaApiTest_STORAGE': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": monitors_psaapitest_by_desc,
        }, # PsaApiTest_Storage

        'PsaApiTestIPC_STORAGE': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": monitors_psaapitest_by_desc,
        }, # PsaApiTestIPC_Storage

        'PsaApiTest_Attest': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": monitors_psaapitest_by_ut,
        }, # PsaApiTest_Attest

        'PsaApiTestIPC_Attest': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": monitors_psaapitest_by_ut,
        }, # PsaApiTestIPC_Attest

    }  # Tests
}


# FVP with BL2 bootloader
# firmware <-> ns <-> application: --application cpu0=bl2.axf
# bootloader <-> s <-> data: --data cpu0=tfm_s_ns_signed.bin@0x10080000
fvp_mps2_an521_bl2 = {
    "templ": "fvp_mps2.jinja2",
    "job_name": "fvp_mps2_an521_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"AN521": ""},
    "compilers": ["GNUARM", "ARMCLANG"],
    "build_types": ["Debug", "Release", "Minsizerel"],
    "boot_types": ["BL2"],
    "data_bin_offset": "0x10080000",
    "tests": {
        'Default': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # Default
        'DefaultProfileS': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileS
        'DefaultProfileM': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileM
        'DefaultProfileL': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileL

        'Regression': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression

        'RegressionProfileM': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileM
        'RegressionProfileS': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileS
        'RegressionProfileL': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileL

        'RegressionIPC': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionIPCTfmLevel2': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionIPCTfmLevel3': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'CoreIPC': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPC
        'CoreIPCTfmLevel2': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel2
        'CoreIPCTfmLevel3': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel3

        'PsaApiTest_Crypto': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": monitors_psaapitest_crypto_workaround,
        }, # PsaApiTest_Crypto

        'PsaApiTest_STORAGE': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": monitors_psaapitest_by_desc,
        }, # PsaApiTest_Storage

        'PsaApiTestIPC_STORAGE': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": monitors_psaapitest_by_desc,
        }, # PsaApiTestIPC_Storage

        'PsaApiTest_Attest': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": monitors_psaapitest_by_ut,
        }, # PsaApiTest_Attest

        'PsaApiTestIPC_Attest': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": monitors_psaapitest_by_ut,
        }, # PsaApiTestIPC_Attest

    }  # Tests
}


# FVP without BL2 bootloader
# firmware <-> ns <-> application: --application cpu0=tfm_s.axf
# bootloader <-> s <-> data: --data cpu0=tfm_ns.bin@0x00100000
fvp_mps2_an521_nobl2 = {
    "templ": "fvp_mps2.jinja2",
    "job_name": "fvp_mps2_an521_nobl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"AN521": ""},
    "compilers": ["GNUARM", "ARMCLANG"],
    "build_types": ["Debug", "Release", "Minsizerel"],
    "boot_types": ["NOBL2"],
    "data_bin_offset": "0x00100000",
    "cpu_baseline": 1,
    "tests": {
        'Default': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }
            ]
        },  # Default
        'DefaultProfileS': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileS
        'DefaultProfileM': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileM
        'DefaultProfileL': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileL

        'Regression': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionProfileM': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileM
        'RegressionProfileS': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileS
        'RegressionProfileL': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileL

        'RegressionIPC': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionIPC
        'RegressionIPCTfmLevel2': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionIPCTfmLevel2
        'RegressionIPCTfmLevel3': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionIPCTfmLevel3
        'CoreIPC': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPC
        'CoreIPCTfmLevel2': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel2
        'CoreIPCTfmLevel3': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel3
    }  # Tests
}


# FVP with BL2 bootloader
# firmware <-> ns <-> application: --application cpu0=bl2.axf
# bootloader <-> s <-> data: --data cpu0=tfm_s_ns_signed.bin@0x10080000
fvp_mps2_an519_bl2 = {
    "templ": "fvp_mps2.jinja2",
    "job_name": "fvp_mps2_an519_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"AN519": ""},
    "compilers": ["GNUARM", "ARMCLANG"],
    "build_types": ["Debug", "Release", "Minsizerel"],
    "boot_types": ["BL2"],
    "data_bin_offset": "0x10080000",
    "cpu0_baseline": 1,
    "tests": {
        'Default': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # Default
        'DefaultProfileS': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileS
        'DefaultProfileM': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileM

        'Regression': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression

        'RegressionProfileM': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileM
        'RegressionProfileS': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileS

        'RegressionIPC': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionIPCTfmLevel2': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'CoreIPC': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPC
        'CoreIPCTfmLevel2': {
            "binaries": {
                "firmware": "bl2.axf",
                "bootloader": "tfm_s_ns_signed.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel2
    }  # Tests
}


# FVP without BL2 bootloader
# firmware <-> ns <-> application: --application cpu0=tfm_s.axf
# bootloader <-> s <-> data: --data cpu0=tfm_ns.bin@0x00100000
fvp_mps2_an519_nobl2 = {
    "templ": "fvp_mps2.jinja2",
    "job_name": "fvp_mps2_an519_nobl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"AN519": ""},
    "compilers": ["GNUARM", "ARMCLANG"],
    "build_types": ["Debug", "Release", "Minsizerel"],
    "boot_types": ["NOBL2"],
    "data_bin_offset": "0x00100000",
    "cpu0_baseline": 1,
    "tests": {
        'Default': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }
            ]
        },  # Default
        'DefaultProfileS': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileS
        'DefaultProfileM': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                } # Monitors
            ]
        },  # DefaultProfileM

        'Regression': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionProfileM': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileM
        'RegressionProfileS': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileS

        'RegressionIPC': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionIPC
        'RegressionIPCTfmLevel2': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                           "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                           "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionIPCTfmLevel2
        'CoreIPC': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPC
        'CoreIPCTfmLevel2': {
            "binaries": {
                "firmware": "tfm_s.axf",
                "bootloader": "tfm_ns.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }  # Monitors
            ]
        },  # CoreIPCTfmLevel2
    }  # Tests
}


# MPS2 with BL2 bootloader
# IMAGE0ADDRESS: 0x10000000
# IMAGE0FILE: \Software\bl2.bin  ; BL2 bootloader
# IMAGE1ADDRESS: 0x10080000
# IMAGE1FILE: \Software\tfm_s_ns_signed.bin ; TF-M example application binary blob
qemu_mps2_bl2 = {
    "templ": "qemu_mps2_bl2.jinja2",
    "job_name": "qemu_mps2_bl2",
    "device_type": "qemu",
    "job_timeout": 300,
    "action_timeout": 300,
    "poweroff_timeout": 20,
    "platforms": {"AN521": ""},
    "compilers": ["GNUARM", "ARMCLANG"],
    "build_types": ["Debug", "Release"],
    "boot_types": ["BL2"],
    "tests": {
        # 'Default': {
        #     "binaries": {
        #         "firmware": "tfm_s_ns_signed.bin",
        #         "bootloader": "bl2.bin"
        #     },
        #     "monitors": [
        #         {
        #             'name': 'Secure_Test_Suites_Summary',
        #             'start': r'[Sec Thread]',
        #             'end': r'system starting',
        #             'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
        #                        r'(?P<test_case_id>Secure image '
        #                        r'initializing)(?P<result>!)',
        #             'fixup': {"pass": "!", "fail": ""},
        #             'required': ["secure_image_initializing"]
        #         }  # Monitors
        #     ]
        # },  # Default
        # 'DefaultProfileS': {
        #     "binaries": {
        #         "firmware": "tfm_s_ns_signed.bin",
        #         "bootloader": "bl2.bin"
        #     },
        #     "monitors": [
        #         {
        #             'name': 'Secure_Test_Suites_Summary',
        #             'start': r'[Sec Thread]',
        #             'end': r'system starting',
        #             'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
        #                        r'(?P<test_case_id>Secure image '
        #                        r'initializing)(?P<result>!)',
        #             'fixup': {"pass": "!", "fail": ""},
        #             'required': ["secure_image_initializing"]
        #         }  # Monitors
        #     ]
        # },  # DefaultProfileS
        # 'DefaultProfileM': {
        #     "binaries": {
        #         "firmware": "tfm_s_ns_signed.bin",
        #         "bootloader": "bl2.bin"
        #     },
        #     "monitors": [
        #         {
        #             'name': 'Secure_Test_Suites_Summary',
        #             'start': r'[Sec Thread]',
        #             'end': r'system starting',
        #             'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
        #                        r'(?P<test_case_id>Secure image '
        #                        r'initializing)(?P<result>!)',
        #             'fixup': {"pass": "!", "fail": ""},
        #             'required': ["secure_image_initializing"]
        #         }  # Monitors
        #     ]
        # },  # DefaultProfileM
        'Regression': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionProfileS': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # RegressionProfileS
        'RegressionIPC': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionIPCTfmLevel2': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        'RegressionIPCTfmLevel3': {
            "binaries": {
                "firmware": "tfm_s_ns_signed.bin",
                "bootloader": "bl2.bin"
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has (.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },  # Regression
        # 'CoreIPC': {
        #     "binaries": {
        #         "firmware": "tfm_s_ns_signed.bin",
        #         "bootloader": "bl2.bin"
        #     },
        #     "monitors": [
        #         {
        #             'name': 'Secure_Test_Suites_Summary',
        #             'start': r'[Sec Thread]',
        #             'end': r'system starting',
        #             'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
        #                        r'(?P<test_case_id>Secure image '
        #                        r'initializing)(?P<result>!)',
        #             'fixup': {"pass": "!", "fail": ""},
        #             'required': ["secure_image_initializing"]
        #         }  # Monitors
        #     ]
        # },  # CoreIPC
        # 'CoreIPCTfmLevel2': {
        #     "binaries": {
        #         "firmware": "tfm_s_ns_signed.bin",
        #         "bootloader": "bl2.bin"
        #     },
        #     "monitors": [
        #         {
        #             'name': 'Secure_Test_Suites_Summary',
        #             'start': r'[Sec Thread]',
        #             'end': r'system starting',
        #             'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
        #                        r'(?P<test_case_id>Secure image '
        #                        r'initializing)(?P<result>!)',
        #             'fixup': {"pass": "!", "fail": ""},
        #             'required': ["secure_image_initializing"]
        #         }  # Monitors
        #     ]
        # },  # CoreIPCTfmLevel2
        # 'CoreIPCTfmLevel3': {
        #     "binaries": {
        #         "firmware": "tfm_s_ns_signed.bin",
        #         "bootloader": "bl2.bin"
        #     },
        #     "monitors": [
        #         {
        #             'name': 'Secure_Test_Suites_Summary',
        #             'start': r'[Sec Thread]',
        #             'end': r'system starting',
        #             'pattern': r'\x1b\\[1;34m\\[Sec Thread\\] '
        #                        r'(?P<test_case_id>Secure image '
        #                        r'initializing)(?P<result>!)',
        #             'fixup': {"pass": "!", "fail": ""},
        #             'required': ["secure_image_initializing"]
        #         }  # Monitors
        #     ]
        # },  # CoreIPCTfmLevel3
    }
}


# Musca-B1 with BL2 bootloader
# unified hex file comprising of both bl2.bin and tfm_s_ns_signed.bin
# srec_cat bin/bl2.bin -Binary -offset 0xA000000 bin/tfm_s_ns_signed.bin -Binary -offset 0xA020000 -o tfm.hex -Intel
musca_b1_bl2 = {
    "templ": "musca_b1.jinja2",
    "job_name": "musca_b1_bl2",
    "device_type": "musca-b",
    "job_timeout": 40,
    "action_timeout": 20,
    "monitor_timeout": 30,
    "poweroff_timeout": 40,
    "platforms": {"MUSCA_B1": ""},
    "compilers": ["GNUARM", "ARMCLANG"],
    "build_types": ["Debug", "Release", "Minsizerel"],
    "boot_types": ["BL2"],
    "tests": {
        "Default": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "CoreIPC": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "CoreIPCTfmLevel2": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "CoreIPCTfmLevel3": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "DefaultProfileM": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "DefaultProfileS": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "Regression": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },
        "RegressionIPC": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },
        "RegressionIPCTfmLevel2": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },
        "RegressionIPCTfmLevel3": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },
        "RegressionProfileM": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },
        "RegressionProfileS": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },
    },
}

# Musca-B1 with BL2 bootloader and OTP enabled
# unified hex file comprising of both bl2.bin and tfm_s_ns_signed.bin
# srec_cat bin/bl2.bin -Binary -offset 0xA000000 bin/tfm_s_ns_signed.bin -Binary -offset 0xA020000 -o tfm.hex -Intel
musca_b1_otp_bl2 = {
    "templ": "musca_b1_otp.jinja2",
    "job_name": "musca_b1_opt_bl2",
    "device_type": "musca-b",
    "job_timeout": 40,
    "action_timeout": 20,
    "monitor_timeout": 30,
    "poweroff_timeout": 40,
    "platforms": {"MUSCA_B1_OTP": ""},
    "compilers": ["GNUARM"],
    "build_types": ["Debug"],
    "boot_types": ["BL2"],
    "tests": {
        "RegressionIPCTfmLevel3": {
            "binaries": {
                "firmware": "tfm.hex",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage_"
                         "s_interface_tests_tfm_sst_test_2xxx_"),
                        "sst_reliability_tests_tfm_sst_test_3xxx_",
                        "sst_rollback_protection_tests_tfm_sst_test_4xxx_",
                        ("psa_internal_trusted_storage_"
                         "s_interface_tests_tfm_its_test_2xxx_"),
                        "its_reliability_tests_tfm_its_test_3xxx_",
                        ("audit_"
                         "logging_secure_interface_test_tfm_audit_test_1xxx_"),
                        "crypto_secure_interface_tests_tfm_crypto_test_5xxx_",
                        ("initial_attestation_service_"
                         "secure_interface_tests_tfm_attest_test_1xxx_"),
                    ]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': r'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': [
                        ("psa_protected_storage"
                         "_ns_interface_tests_tfm_sst_test_1xxx_"),
                        ("psa_internal_trusted_storage"
                         "_ns_interface_tests_tfm_its_test_1xxx_"),
                        ("auditlog_"
                         "non_secure_interface_test_tfm_audit_test_1xxx_"),
                        ("crypto_"
                         "non_secure_interface_test_tfm_crypto_test_6xxx_"),
                        ("initial_attestation_service_"
                         "non_secure_interface_tests_tfm_attest_test_2xxx_"),
                        "core_non_secure_positive_tests_tfm_core_test_1xxx_"
                    ]
                }
            ]  # Monitors
        },
    },
}

# STM32L562E-DK
stm32l562e_dk = {
    "templ": "stm32l562e_dk.jinja2",
    "job_name": "stm32l562e_dk",
    "device_type": "stm32l562e-dk",
    "job_timeout": 24,
    "action_timeout": 15,
    "monitor_timeout": 15,
    "poweroff_timeout": 5,
    "platforms": {"stm32l562e_dk": ""},
    "compilers": ["GNUARM", "ARMCLANG"],
    "build_types": ["Release", "Minsizerel"],
    "boot_types": ["BL2"],
    "tests": {
        "Regression": {
            "binaries": {
                "tarball": "stm32l562e-dk-tfm.tar.bz2",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': 'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "RegressionIPC": {
            "binaries": {
                "tarball": "stm32l562e-dk-tfm.tar.bz2",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': 'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "RegressionIPCTfmLevel2": {
            "binaries": {
                "tarball": "stm32l562e-dk-tfm.tar.bz2",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': 'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
        "RegressionIPCTfmLevel3": {
            "binaries": {
                "tarball": "stm32l562e-dk-tfm.tar.bz2",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': 'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
    },
}

# LPCxpresso55S69
lpcxpresso55s69 = {
    "templ": "lpcxpresso55s69.jinja2",
    "job_name": "lpcxpresso55s69",
    "device_type": "lpcxpresso55s69",
    "job_timeout": 24,
    "action_timeout": 15,
    "monitor_timeout": 15,
    "poweroff_timeout": 5,
    "platforms": {"lpcxpresso55s69": ""},
    "compilers": ["GNUARM"],
    "build_types": ["Relwithdebinfo"],
    "boot_types": ["NOBL2"],
    "tests": {
        "DefaultProfileM": {
            "binaries": {
                "tarball": "lpcxpresso55s69-tfm.tar.bz2",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Non-Secure system',
                    'end': r'starting\\.{3}',
                    'pattern': r'Non-Secure system starting\\.{3}',
                    'fixup': {"pass": "!", "fail": ""},
                }
            ]  # Monitors
        },
        "RegressionProfileM": {
            "binaries": {
                "tarball": "lpcxpresso55s69-tfm.tar.bz2",
            },
            "monitors": [
                {
                    'name': 'Secure_Test_Suites_Summary',
                    'start': 'Secure test suites summary',
                    'end': 'End of Secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                },
                {
                    'name': 'Non_Secure_Test_Suites_Summary',
                    'start': 'Non-secure test suites summary',
                    'end': 'End of Non-secure test suites',
                    'pattern': r"Test suite '(?P<"
                               r"test_case_id>[^\n]+)' has(.*) "
                               r"(?P<result>PASSED|FAILED)",
                    'fixup': {"pass": "PASSED", "fail": "FAILED"},
                    'required': ["secure_image_initializing"]
                }
            ]  # Monitors
        },
    }
}

# All configurations should be mapped here
lava_gen_config_map = {
    "mps2_an521_bl2": tfm_mps2_sse_200,
    "fvp_mps2_an521_bl2": fvp_mps2_an521_bl2,
    "fvp_mps2_an521_nobl2": fvp_mps2_an521_nobl2,
    "fvp_mps2_an519_bl2": fvp_mps2_an519_bl2,
    "fvp_mps2_an519_nobl2": fvp_mps2_an519_nobl2,
    "qemu_mps2_bl2": qemu_mps2_bl2,
    "musca_b1": musca_b1_bl2,
    "musca_b1_otp": musca_b1_otp_bl2,
    "stm32l562e_dk": stm32l562e_dk,
    "lpcxpresso55s69": lpcxpresso55s69,
}

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
