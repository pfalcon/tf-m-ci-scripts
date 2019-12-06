#!/usr/bin/env python3

""" config_templatess.py:

 """

from __future__ import print_function
from copy import deepcopy
from .fastmodel_wrapper_config import fpv_wrapper_config

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


# ===================  Template Classes ===================
class template_cfg(fpv_wrapper_config):
    """ Creates a skeleton template configuration that allows creation of
    configuration variants which set the parameters of:
    buildpath, config, platform, compiler , as well as the missing test params,
    test_rex, test_cases, test_end_string """

    _name = fpv_wrapper_config._name + "_%(platform)s_%(compiler)s_" + \
        "%(config)s_%(build_type)s_%(bootloader)s"
    # variant dictionary allows indivudal and targeted parameter modification
    _vdict = {
        "build_path": "%(build_path)s",
        "variant_name_tpl": "%(variant_name_tpl)s",
        "app_bin_path": "%(app_bin_path)s",
        "app_bin": "%(app_bin)s",
        "data_bin_path": "%(data_bin_path)s",
        "data_bin": "%(data_bin)s",
        "data_bin_offset": "%(data_bin_offset)s",
        "config": "%(config)s",
        "platform": "%(platform)s",
        "compiler": "%(compiler)s",
        "build_type": "%(build_type)s",
        "bootloader": "%(bootloader)s"
    }

    _cfg = deepcopy(fpv_wrapper_config._cfg)
    _cfg["directory"] = "FVP_MPS2"
    _cfg["terminal_log"] = "terminal_%(variant_name_tpl)s.log"
    _cfg["bin"] = "FVP_MPS2_AEMv8M"
    _cfg["error_on_failed"] = False
    _cfg["application"] = (
        "cpu0=%(build_path)s/%(variant_name_tpl)s/" +
        "%(app_bin_path)s/%(app_bin)s")
    _cfg["data"] = (
        "cpu0=%(build_path)s/%(variant_name_tpl)s/%(data_bin_path)s/" +
        "%(data_bin)s@%(data_bin_offset)s")
    _cfg["simlimit"] = "600"
    _cfg["parameters"] = [
        "fvp_mps2.platform_type=2",
        "cpu0.baseline=0",
        "cpu0.INITVTOR_S=0x10000000",
        "cpu0.semihosting-enable=0",
        "fvp_mps2.DISABLE_GATING=0",
        "fvp_mps2.telnetterminal0.start_telnet=0",
        "fvp_mps2.telnetterminal1.start_telnet=0",
        "fvp_mps2.telnetterminal2.start_telnet=0",
        "fvp_mps2.telnetterminal0.quiet=1",
        "fvp_mps2.telnetterminal1.quiet=1",
        "fvp_mps2.telnetterminal2.quiet=1",
        "fvp_mps2.UART0.out_file=$TERM_FILE",
        "fvp_mps2.UART0.unbuffered_output=1",
        "fvp_mps2.UART0.shutdown_on_eot=1",
        "fvp_mps2.mps2_visualisation.disable-visualisation=1"]


class template_default_config(template_cfg):
    """ Will automatically populate the required information for tfm
    Default configuration testing. User still needs to set the
    buildpath, platform, compiler variants """

    _cfg = deepcopy(template_cfg._cfg)

    _vdict = deepcopy(template_cfg._vdict)

    # Set defaults across all variants
    _vdict["build_path"] = "build-ci-all"
    _vdict["app_bin_path"] = "install/outputs/fvp"
    _vdict["data_bin_path"] = "install/outputs/fvp"
    _vdict["variant_name_tpl"] = "%(platform)s_%(compiler)s_%(config)s_" + \
        "%(build_type)s_%(bootloader)s"

    # Mofify the %(config)s parameter of the template
    _vdict["config"] = "ConfigDefault"
    _cfg["terminal_log"] = _cfg["terminal_log"] % _vdict

    # System supports two types of matching with
    # test_case_id and result match group and only test_case_id
    _cfg["test_rex"] = (r'\x1b\[1;34m\[Sec Thread\] '
                        r'(?P<test_case_id>Secure image initializing!)\x1b\[0m'
                        )

    # test_case_id capture group Should match test_cases entries
    _cfg["test_cases"] = [
        'Secure image initializing!',
    ]
    # Testing will stop if string is reached
    _cfg["test_end_string"] = "Secure image initializing"
    _cfg["simlimit"] = "120"

class template_regression_config(template_cfg):
    """ Will automatically populate the required information for tfm
    Regression configuration testing. User still needs to set the
    buildpath, platform, compiler variants """

    _cfg = deepcopy(template_cfg._cfg)
    _vdict = deepcopy(template_cfg._vdict)

    # Set defaults across all variants
    _vdict["build_path"] = "build-ci-all"
    _vdict["app_bin_path"] = "install/outputs/fvp"
    _vdict["data_bin_path"] = "install/outputs/fvp"
    _vdict["variant_name_tpl"] = "%(platform)s_%(compiler)s_%(config)s_" + \
        "%(build_type)s_%(bootloader)s"

    # Mofify the %(config)s parameter of the template
    _vdict["config"] = "ConfigRegression"
    _cfg["terminal_log"] = _cfg["terminal_log"] % _vdict

    # Populate the test cases
    _cfg["test_rex"] = (r"[\x1b]\[37mTest suite '(?P<test_case_id>[^\n]+)'"
                        r" has [\x1b]\[32m (?P<result>PASSED|FAILED)")
    _cfg["test_cases"] = [
        'PSA protected storage S interface tests (TFM_SST_TEST_2XXX)',
        'PSA protected storage NS interface tests (TFM_SST_TEST_1XXX)',
        'SST reliability tests (TFM_SST_TEST_3XXX)',
        'PSA internal trusted storage S interface tests (TFM_ITS_TEST_2XXX)',
        'PSA internal trusted storage NS interface tests (TFM_ITS_TEST_1XXX)',
        'ITS reliability tests (TFM_ITS_TEST_3XXX)',
        'Core non-secure positive tests (TFM_CORE_TEST_1XXX)',
        'AuditLog non-secure interface test (TFM_AUDIT_TEST_1XXX)',
        'Crypto non-secure interface test (TFM_CRYPTO_TEST_6XXX)',
        'Initial Attestation Service '
        'non-secure interface tests(TFM_ATTEST_TEST_2XXX)',
        'SST rollback protection tests (TFM_SST_TEST_4XXX)',
        'Audit Logging secure interface test (TFM_AUDIT_TEST_1XXX)',
        'Crypto secure interface tests (TFM_CRYPTO_TEST_5XXX)',
        'Initial Attestation Service secure '
        'interface tests(TFM_ATTEST_TEST_1XXX)',
    ]
    _cfg["test_end_string"] = "End of Non-secure test suites"

    _cfg["simlimit"] = "1200"


class template_coreipc_config(template_cfg):
    """ Will automatically populate the required information for tfm
    coreipc configuration testing. User still needs to set the
    buildpath, platform, compiler variants """

    _cfg = deepcopy(template_cfg._cfg)

    _vdict = deepcopy(template_cfg._vdict)

    # Set defaults across all variants
    _vdict["build_path"] = "build-ci-all"

    _vdict["app_bin_path"] = "install/outputs/fvp"
    _vdict["data_bin_path"] = "install/outputs/fvp"

    _vdict["variant_name_tpl"] = "%(platform)s_%(compiler)s_%(config)s_" + \
        "%(build_type)s_%(bootloader)s"

    # Mofify the %(config)s parameter of the template
    _vdict["config"] = "ConfigCoreIPC"
    _cfg["terminal_log"] = _cfg["terminal_log"] % _vdict

    # System supports two types of matching with
    # test_case_id and result match group and only test_case_id
    _cfg["test_rex"] = (r'\x1b\[1;34m\[Sec Thread\] '
                        r'(?P<test_case_id>Secure image initializing!)\x1b\[0m'
                        )

    # test_case_id capture group Should match test_cases entries
    _cfg["test_cases"] = [
        'Secure image initializing!',
    ]
    # Testing will stop if string is reached
    _cfg["test_end_string"] = "Secure image initializing"
    _cfg["simlimit"] = "1200"

class template_coreipctfmlevel2_config(template_cfg):
    """ Will automatically populate the required information for tfm
    coreipc tfmlevel2 configuration testing. User still needs to set the
    buildpath, platform, compiler variants """

    _cfg = deepcopy(template_cfg._cfg)

    _vdict = deepcopy(template_cfg._vdict)

    # Set defaults across all variants
    _vdict["build_path"] = "build-ci-all"

    _vdict["app_bin_path"] = "install/outputs/fvp"
    _vdict["data_bin_path"] = "install/outputs/fvp"

    _vdict["variant_name_tpl"] = "%(platform)s_%(compiler)s_%(config)s_" + \
        "%(build_type)s_%(bootloader)s"

    # Mofify the %(config)s parameter of the template
    _vdict["config"] = "ConfigCoreIPCTfmLevel2"
    _cfg["terminal_log"] = _cfg["terminal_log"] % _vdict

    # System supports two types of matching with
    # test_case_id and result match group and only test_case_id
    _cfg["test_rex"] = (r'\x1b\[1;34m\[Sec Thread\] '
                        r'(?P<test_case_id>Secure image initializing!)\x1b\[0m'
                        )

    # test_case_id capture group Should match test_cases entries
    _cfg["test_cases"] = [
        'Secure image initializing!',
    ]
    # Testing will stop if string is reached
    _cfg["test_end_string"] = "Secure image initializing"
    _cfg["simlimit"] = "1200"
