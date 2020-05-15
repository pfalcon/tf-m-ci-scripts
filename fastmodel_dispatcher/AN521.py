#!/usr/bin/env python3

""" an521.py:

    Contains AN521 specific configuration variants. Each configuration is
    created by a template(defines the expected output of the test) and a
    decorated class setting the parameters. The whole scope of this module
    is imported in the config map, to avoid keeping a manual list of the
    configurations up to date. """

from __future__ import print_function
import os
import sys

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

try:
    from tfm_ci_pylib.fastmodel_wrapper import FastmodelConfigMap
    from tfm_ci_pylib.fastmodel_wrapper import config_variant

    from tfm_ci_pylib.fastmodel_wrapper import \
        template_default_config, template_regression_config, \
        template_coreipc_config, template_coreipctfmlevel2_config, \
        template_regressionipc_config, template_regressionipctfmlevel2_config, \
        template_psaapitestipctfmlevel2_config, \
        template_psaapitestipc_config, template_psaapitest_config
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.fastmodel_wrapper import FastmodelConfigMap
    from tfm_ci_pylib.fastmodel_wrapper import config_variant
    from tfm_ci_pylib.fastmodel_wrapper import \
        template_default_config, template_regression_config, \
        template_coreipc_config, template_coreipctfmlevel2_config, \
        template_regressionipc_config, template_regressionipctfmlevel2_config, \
        template_psaapitestipctfmlevel2_config, \
        template_psaapitestipc_config, template_psaapitest_config

# =====================  AN521 Configuration Classes ======================
# Configurations will be dynamically defined

# =====================  Default Config ======================


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configdefault_debug_bl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configdefault_debug_bl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an521_armclang_configdefault_debug_nobl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an521_gnuarm_configdefault_debug_nobl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configdefault_release_bl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configdefault_release_bl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an521_armclang_configdefault_release_nobl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an521_gnuarm_configdefault_release_nobl2(template_default_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configdefault_minsizerel_bl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configdefault_minsizerel_bl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_armclang_configdefault_minsizerel_nobl2(template_default_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_gnuarm_configdefault_minsizerel_nobl2(template_default_config):
    pass

# =====================  Regressions Config ======================

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configregression_debug_bl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configregression_debug_bl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an521_armclang_configregression_debug_nobl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an521_gnuarm_configregression_debug_nobl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configregression_release_bl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configregression_release_bl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an521_armclang_configregression_release_nobl2(
        template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an521_gnuarm_configregression_release_nobl2(template_regression_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configregression_minsizerel_bl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configregression_minsizerel_bl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_armclang_configregression_minsizerel_nobl2(template_regression_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_gnuarm_configregression_minsizerel_nobl2(template_regression_config):
    pass

# =====================  RegressionIPC Config ======================

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configregressionipc_debug_bl2(template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configregressionipc_debug_bl2(template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an521_armclang_configregressionipc_debug_nobl2(template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an521_gnuarm_configregressionipc_debug_nobl2(template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configregressionipc_release_bl2(template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configregressionipc_release_bl2(template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an521_armclang_configregressionipc_release_nobl2(
        template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an521_gnuarm_configregressionipc_release_nobl2(template_regressionipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configregressionipc_minsizerel_bl2(template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configregressionipc_minsizerel_bl2(template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_armclang_configregressionipc_minsizerel_nobl2(
        template_regressionipc_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_gnuarm_configregressionipc_minsizerel_nobl2(template_regressionipc_config):
    pass

# =====================  RegressionIPCTfmLevel2 Config ======================

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configregressionipctfmlevel2_debug_bl2(template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configregressionipctfmlevel2_debug_bl2(template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an521_armclang_configregressionipctfmlevel2_debug_nobl2(template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an521_gnuarm_configregressionipctfmlevel2_debug_nobl2(template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configregressionipctfmlevel2_release_bl2(template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configregressionipctfmlevel2_release_bl2(template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an521_armclang_configregressionipctfmlevel2_release_nobl2(
        template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an521_gnuarm_configregressionipctfmlevel2_release_nobl2(template_regressionipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configregressionipctfmlevel2_minsizerel_bl2(template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configregressionipctfmlevel2_minsizerel_bl2(template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_armclang_configregressionipctfmlevel2_minsizerel_nobl2(
        template_regressionipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_gnuarm_configregressionipctfmlevel2_minsizerel_nobl2(template_regressionipctfmlevel2_config):
    pass

# =====================  CoreIPC Config ======================


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configcoreipc_debug_bl2(template_coreipc_config):

    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an521_armclang_configcoreipc_debug_nobl2(template_coreipc_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configcoreipc_release_bl2(template_coreipc_config):

    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an521_armclang_configcoreipc_release_nobl2(template_coreipc_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configcoreipc_debug_bl2(template_coreipc_config):

    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an521_gnuarm_configcoreipc_debug_nobl2(template_coreipc_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configcoreipc_release_bl2(template_coreipc_config):

    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an521_gnuarm_configcoreipc_release_nobl2(template_coreipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configcoreipc_minsizerel_bl2(template_coreipc_config):

    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_armclang_configcoreipc_minsizerel_nobl2(template_coreipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configcoreipc_minsizerel_bl2(template_coreipc_config):

    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_gnuarm_configcoreipc_minsizerel_nobl2(template_coreipc_config):
    pass

# =====================  CoreIPCTfmLevel2 Config ======================


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configcoreipctfmlevel2_debug_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an521_armclang_configcoreipctfmlevel2_debug_nobl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configcoreipctfmlevel2_release_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an521_armclang_configcoreipctfmlevel2_release_nobl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configcoreipctfmlevel2_debug_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an521_gnuarm_configcoreipctfmlevel2_debug_nobl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configcoreipctfmlevel2_release_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an521_gnuarm_configcoreipctfmlevel2_release_nobl2(template_coreipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configcoreipctfmlevel2_minsizerel_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="ARMCLANG",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_armclang_configcoreipctfmlevel2_minsizerel_nobl2(template_coreipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configcoreipctfmlevel2_minsizerel_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN521",
                compiler="GNUARM",
                build_type="Minsizerel",
                bootloader="NOBL2")
class an521_gnuarm_configcoreipctfmlevel2_minsizerel_nobl2(template_coreipctfmlevel2_config):
    pass

# =====================  ConfigPsaApiTestIPCTfmLevel2 Config ======================

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_crypto_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_crypto_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_crypto_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_ps_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_ps_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_ps_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_its_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_its_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_its_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_attest_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_attest_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_attest_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_crypto_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_crypto_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_crypto_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_ps_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_ps_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_ps_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_its_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_its_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_its_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_attest_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_attest_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_attest_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="FF",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_ff_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="FF",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_ff_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="FF",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipctfmlevel2_ff_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="FF",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_ff_debug_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="FF",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_ff_release_bl2(template_psaapitestipctfmlevel2_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="FF",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipctfmlevel2_ff_minsizerel_bl2(template_psaapitestipctfmlevel2_config):
    pass

# =====================  ConfigPsaApiTestIPC Config ======================

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_crypto_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_crypto_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_crypto_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_ps_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_ps_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_ps_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_its_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_its_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_its_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_attest_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_attest_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_attest_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_crypto_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_crypto_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_crypto_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_ps_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_ps_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_ps_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_its_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_its_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_its_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_attest_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_attest_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_attest_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="FF",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_ff_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="FF",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_ff_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="FF",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitestipc_ff_minsizerel_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="FF",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_ff_debug_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="FF",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_ff_release_bl2(template_psaapitestipc_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="FF",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitestipc_ff_minsizerel_bl2(template_psaapitestipc_config):
    pass

# =====================  ConfigPsaApiTest Config ======================

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_crypto_debug_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_crypto_release_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Crypto",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_crypto_minsizerel_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_ps_debug_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_ps_release_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="PS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_ps_minsizerel_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_its_debug_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_its_release_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="ITS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_its_minsizerel_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Debug",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_attest_debug_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Release",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_attest_release_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="GNUARM",
                psa_suite="Attest",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_gnuarm_configpsaapitest_attest_minsizerel_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitest_crypto_debug_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitest_crypto_release_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Crypto",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitest_crypto_minsizerel_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitest_ps_debug_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitest_ps_release_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="PS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitest_ps_minsizerel_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitest_its_debug_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitest_its_release_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="ITS",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitest_its_minsizerel_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Debug",
                bootloader="BL2")
class an521_armclang_configpsaapitest_attest_debug_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Release",
                bootloader="BL2")
class an521_armclang_configpsaapitest_attest_release_bl2(template_psaapitest_config):
    pass

@config_variant(platform="AN521",
                compiler="ARMCLANG",
                psa_suite="Attest",
                build_type="Minsizerel",
                bootloader="BL2")
class an521_armclang_configpsaapitest_attest_minsizerel_bl2(template_psaapitest_config):
    pass

AN521 = FastmodelConfigMap(globals(), "AN521")

if __name__ == "__main__":
    pass
