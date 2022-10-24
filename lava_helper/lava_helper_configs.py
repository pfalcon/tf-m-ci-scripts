#!/usr/bin/env python3

""" lava_job_generator_configs.py:

    Default configurations for lava job generator """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2022, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

__author__ = "tf-m@lists.trustedfirmware.org"
__project__ = "Trusted Firmware-M Open CI"
__version__ = "1.4.0"


import os


tf_downloads="https://downloads.trustedfirmware.org"
coverage_trace_plugin=tf_downloads + "/coverage-plugin/qa-tools/coverage-tool/coverage-plugin/coverage_trace.so"


# LAVA test-monitor definition for configs without regression tests.
# "Non-Secure system starting..." is expected to indicate
# that TF-M has been booted successfully.
monitors_no_reg_tests = {
    'name': 'NS_SYSTEM_BOOTING',
    'start': 'Non-Secure system',
    'end': r'starting\\.{3}',
    'pattern': r'Non-Secure system starting\\.{3}',
    'fixup': {"pass": "!", "fail": ""},
}

# LAVA test-monitor definitions for configs with tests.
# Results of each test case is parsed separately, capturing test case id.
# Works across any test suites enabled.
monitors_mcuboot_tests = {
    'name': 'mcuboot_suite',
    'start': 'Execute test suites for the MCUBOOT area',
    'end': 'End of MCUBOOT test suites',
    'pattern': r"TEST: (?P<test_case_id>.+?) - (?P<result>(PASSED|FAILED|SKIPPED))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
}

monitors_s_reg_tests = {
    'name': 'secure_regression_suite',
    'start': 'Execute test suites for the Secure area',
    'end': 'End of Secure test suites',
    'pattern': r"TEST: (?P<test_case_id>.+?) - (?P<result>(PASSED|FAILED|SKIPPED))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
}

monitors_ns_reg_tests = {
    'name': 'non_secure_regression_suite',
    'start': 'Execute test suites for the Non-secure area',
    'end': 'End of Non-secure test suites',
    'pattern': r"TEST: (?P<test_case_id>.+?) - (?P<result>(PASSED|FAILED|SKIPPED))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
}

monitors_arch_tests = {
    'name': 'psa_api_suite',
    'start': 'Running..',
    'end': 'Entering standby..',
    'pattern': r" DESCRIPTION: +(?P<test_case_id>.+?)\r?\n"
                r".+?"
                r"TEST RESULT: (?P<result>(PASSED|FAILED|SKIPPED|SIM ERROR))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED", "sim_error": "SIM ERROR"},
}


# MPS2 with BL2 bootloader for AN521
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
    "platforms": {"arm/mps2/an521": "mps2_sse200_an512_new.tar.gz"},
    "binaries": {
        "firmware": "tfm_s_ns_signed.bin",
        "bootloader": "bl2.bin"
    },
    "monitors": {
        'no_reg_tests': [monitors_no_reg_tests],
        'reg_tests': [monitors_mcuboot_tests, monitors_s_reg_tests, monitors_ns_reg_tests],
        'arch_tests': [monitors_arch_tests] if os.getenv("TEST_PSA_API") != "IPC" else [], # FF test on FPGA not supported in LAVA yet
    }
}

# FVP with BL2 bootloader for AN552
# firmware <-> ns <-> application: --application cpu0=bl2.axf
# bootloader <-> s <-> data: --data cpu0=tfm_s_ns_signed.bin@0x01000000
fvp_mps3_an552_bl2 = {
    "templ": "fvp_mps3.jinja2",
    "job_name": "fvp_mps3_an552_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps3/an552": ""},
    "data_bin_offset": "0x01000000",
    "binaries": {
        "application": "bl2.axf",
        "data": "tfm_s_ns_signed.bin"
    },
    "monitors": {
        'no_reg_tests': [monitors_no_reg_tests],
        'reg_tests': [monitors_mcuboot_tests, monitors_s_reg_tests, monitors_ns_reg_tests],
    }
}

# FVP with BL1 and BL2 bootloader for Corstone1000
fvp_corstone1000 = {
    "templ": "fvp_corstone1000.jinja2",
    "job_name": "fvp_corstone1000",
    "device_type": "fvp",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/corstone1000": ""},
    "data_bin_offset": "0x68100000",
    "binaries": {
        "application": "bl1.bin",
        "data": "flash.bin"
    },
    "monitors": {
        'reg_tests': [monitors_mcuboot_tests, monitors_s_reg_tests] if "FVP" in os.getenv('EXTRA_PARAMS') else [],
    }
}

# FVP with BL2 bootloader for AN521
# application: --application cpu0=bl2.axf
# data: --data cpu0=tfm_s_ns_signed.bin@0x10080000
fvp_mps2_an521_bl2 = {
    "templ": "fvp_mps2.jinja2",
    "job_name": "fvp_mps2_an521_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps2/an521": ""},
    "data_bin_offset": "0x10080000",
    "binaries": {
        "application": "bl2.axf",
        "data": "tfm_s_ns_signed.bin"
    },
    "monitors": {
        'no_reg_tests': [monitors_no_reg_tests],
        'reg_tests': [monitors_mcuboot_tests, monitors_s_reg_tests, monitors_ns_reg_tests],
        'arch_tests': [monitors_arch_tests],
    }
}


# FVP with BL2 bootloader for AN519
# application: --application cpu0=bl2.axf
# data: --data cpu0=tfm_s_ns_signed.bin@0x10080000
fvp_mps2_an519_bl2 = {
    "templ": "fvp_mps2.jinja2",
    "job_name": "fvp_mps2_an519_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps2/an519": ""},
    "data_bin_offset": "0x10080000",
    "cpu0_baseline": 1,
    "binaries": {
        "application": "bl2.axf",
        "data": "tfm_s_ns_signed.bin"
    },
    "monitors": {
        'no_reg_tests': [monitors_no_reg_tests],
        'reg_tests': [monitors_mcuboot_tests, monitors_s_reg_tests, monitors_ns_reg_tests],
    }
}


# QEMU for AN521 with BL2 bootloader
qemu_mps2_bl2 = {
    "templ": "qemu_mps2_bl2.jinja2",
    "job_name": "qemu_mps2_bl2",
    "device_type": "qemu",
    "job_timeout": 30,
    "action_timeout": 20,
    "monitor_timeout": 20,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps2/an521": ""},
    "binaries": {
        "firmware": "tfm_s_ns_signed.bin",
        "bootloader": "bl2.bin"
    },
    "monitors": {
        'reg_tests': [monitors_mcuboot_tests, monitors_s_reg_tests, monitors_ns_reg_tests],
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
    "platforms": {"arm/musca_b1": ""},
    "binaries": {
        "firmware": "tfm.hex",
    },
    "monitors": {
        'no_reg_tests': [monitors_no_reg_tests],
        'reg_tests': [monitors_mcuboot_tests, monitors_s_reg_tests, monitors_ns_reg_tests],
    }
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
    "platforms": {"stm/stm32l562e_dk": ""},
    "binaries": {
        "tarball": "stm32l562e-dk-tfm.tar.bz2",
    },
    "monitors": {
        'reg_tests': [monitors_mcuboot_tests, monitors_s_reg_tests, monitors_ns_reg_tests],
    }
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
    "platforms": {"nxp/lpcxpresso55s69": ""},
    "binaries": {
        "tarball": "lpcxpresso55s69-tfm.tar.bz2",
    },
    "monitors": {
        'no_reg_tests': [monitors_no_reg_tests],
        'reg_tests': [monitors_s_reg_tests, monitors_ns_reg_tests],
    }
}

# Cypress PSoC64
psoc64 = {
    "templ": "psoc64.jinja2",
    "job_name": "psoc64",
    "device_type": "cy8ckit-064s0s2-4343w",
    "job_timeout": 30,
    "action_timeout": 20,
    "monitor_timeout": 20,
    "poweroff_timeout": 5,
    "platforms": {"cypress/psoc64": ""},
    "binaries": {
        "spe": "tfm_s_signed.hex",
        "nspe": "tfm_ns_signed.hex",
    },
    "monitors": {
        'reg_tests': [monitors_s_reg_tests, monitors_ns_reg_tests],
    }
}

# All configurations should be mapped here
lava_gen_config_map = {
    "mps2_an521_bl2": tfm_mps2_sse_200,
    "fvp_mps3_an552_bl2": fvp_mps3_an552_bl2,
    "fvp_corstone1000": fvp_corstone1000,
    "fvp_mps2_an521_bl2": fvp_mps2_an521_bl2,
    "fvp_mps2_an519_bl2": fvp_mps2_an519_bl2,
    "qemu_mps2_bl2": qemu_mps2_bl2,
    "musca_b1": musca_b1_bl2,
    "stm32l562e_dk": stm32l562e_dk,
    "lpcxpresso55s69": lpcxpresso55s69,
    "psoc64": psoc64,
}

lavagen_config_sort_order = [
    "templ",
    "job_name",
    "device_type",
    "job_timeout",
    "action_timeout",
    "monitor_timeout",
    "recovery_store_url",
    "platforms",
    "monitors"
]

lava_gen_monitor_sort_order = [
    'name',
    'start',
    'end',
    'pattern',
    'fixup',
]
