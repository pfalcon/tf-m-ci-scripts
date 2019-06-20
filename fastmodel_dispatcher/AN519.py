#!/usr/bin/env python3

""" an521.py:

    Contains AN519 specific configuration variants. Each configuration is
    created by a template(defines the expected output of the test) and a
    decorated class setting the parameters. The whole scope of this module
    is imported in the config map, to avoid keeping a manual list of the
    configurations up to date. """

from __future__ import print_function
import os
import sys

__copyright__ = """
/*
 * Copyright (c) 2019, Arm Limited. All rights reserved.
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
        template_coreipc_config, template_coreipctfmlevel2_config
except ImportError:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.fastmodel_wrapper import FastmodelConfigMap
    from tfm_ci_pylib.fastmodel_wrapper import config_variant
    from tfm_ci_pylib.fastmodel_wrapper import \
        template_default_config, template_regression_config, \
        template_coreipc_config, template_coreipctfmlevel2_config
# =====================  AN521 Configuration Classes ======================
# Configurations will be dynamically defined

# =====================  Default Config ======================


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an519_armclang_configdefault_debug_bl2(template_default_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an519_gnuarm_configdefault_debug_bl2(template_default_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an519_armclang_configdefault_debug_nobl2(template_default_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an519_gnuarm_configdefault_debug_nobl2(template_default_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an519_armclang_configdefault_release_bl2(template_default_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an519_gnuarm_configdefault_release_bl2(template_default_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an519_armclang_configdefault_release_nobl2(template_default_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an519_gnuarm_configdefault_release_nobl2(template_default_config):
    pass

# =====================  Regressions Config ======================


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an519_armclang_configregression_debug_bl2(template_regression_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an519_gnuarm_configregression_debug_bl2(template_regression_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an519_armclang_configregression_debug_nobl2(template_regression_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an519_gnuarm_configregression_debug_nobl2(template_regression_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an519_armclang_configregression_release_bl2(template_regression_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an519_gnuarm_configregression_release_bl2(template_regression_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an519_armclang_configregression_release_nobl2(
        template_regression_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an519_gnuarm_configregression_release_nobl2(template_regression_config):
    pass

# =====================  CoreIPC Config ======================


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an519_armclang_configcoreipc_debug_bl2(template_coreipc_config):

    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an519_armclang_configcoreipc_debug_nobl2(template_coreipc_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an519_armclang_configcoreipc_release_bl2(template_coreipc_config):

    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an519_armclang_configcoreipc_release_nobl2(template_coreipc_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an519_gnuarm_configcoreipc_debug_bl2(template_coreipc_config):

    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an519_gnuarm_configcoreipc_debug_nobl2(template_coreipc_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an519_gnuarm_configcoreipc_release_bl2(template_coreipc_config):

    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an519_gnuarm_configcoreipc_release_nobl2(template_coreipc_config):
    pass

# =====================  CoreIPCTfmLevel2 Config ======================


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="BL2")
class an519_armclang_configcoreipctfmlevel2_debug_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Debug",
                bootloader="NOBL2")
class an519_armclang_configcoreipctfmlevel2_debug_nobl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="BL2")
class an519_armclang_configcoreipctfmlevel2_release_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN519",
                compiler="ARMCLANG",
                build_type="Release",
                bootloader="NOBL2")
class an519_armclang_configcoreipctfmlevel2_release_nobl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="BL2")
class an519_gnuarm_configcoreipctfmlevel2_debug_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Debug",
                bootloader="NOBL2")
class an519_gnuarm_configcoreipctfmlevel2_debug_nobl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Release",
                bootloader="BL2")
class an519_gnuarm_configcoreipctfmlevel2_release_bl2(template_coreipctfmlevel2_config):
    pass


@config_variant(platform="AN519",
                compiler="GNUARM",
                build_type="Release",
                bootloader="NOBL2")
class an519_gnuarm_configcoreipctfmlevel2_release_nobl2(template_coreipctfmlevel2_config):
    pass

AN519 = FastmodelConfigMap(globals(), "AN519")

if __name__ == "__main__":
    pass
