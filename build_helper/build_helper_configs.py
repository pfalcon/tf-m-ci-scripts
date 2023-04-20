#!/usr/bin/env python3

""" builtin_configs.py:

    Default configuration files used as reference """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2023, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

__author__ = "tf-m@lists.trustedfirmware.org"
__project__ = "Trusted Firmware-M Open CI"
__version__ = "1.4.0"

from copy import deepcopy


# common parameters for tf-m build system
# This configuration template will be passed into the tfm-builder module after
# the template evaluation is converted to a command

_common_tfm_builder_cfg = {
    "config_type": "tf-m",
    "codebase_root_dir": "tf-m",
    # Order to which the variants are evaluated. This affects the name of
    # variant configuration and the wildcard replacement logic in invalid
    # configuration tuples
    "sort_order": ["tfm_platform",
                   "compiler",
                   "isolation_level",
                   "test_regression",
                   "test_psa_api",
                   "cmake_build_type",
                   "with_bl2",
                   "profile",
                   "extra_params"],

    # Keys for the templace will come from the combinations of parameters
    # provided in the seed dictionary.

    "config_template": "cmake -G Ninja " + \
        "-DTFM_PLATFORM=%(tfm_platform)s " + \
        "-DTFM_TOOLCHAIN_FILE=%(codebase_root_dir)s/%(compiler)s " + \
        "-DTFM_ISOLATION_LEVEL=%(isolation_level)s " + \
        "%(test_regression)s " + \
        "-DCMAKE_BUILD_TYPE=%(cmake_build_type)s " + \
        "-DTEST_PSA_API=%(test_psa_api)s " + \
        "-DBL2=%(with_bl2)s " + \
        "-DTFM_PROFILE=%(profile)s " + \
        "%(extra_params)s " + \
        "-DTFM_TEST_REPO_PATH=%(codebase_root_dir)s/../tf-m-tests " + \
        "-DMBEDCRYPTO_PATH=%(codebase_root_dir)s/../mbedtls " + \
        "-DPSA_ARCH_TESTS_PATH=%(codebase_root_dir)s/../psa-arch-tests " + \
        "-DMCUBOOT_PATH=%(codebase_root_dir)s/../mcuboot " + \
        "-DQCBOR_PATH=%(codebase_root_dir)s/../QCBOR " + \
        "%(codebase_root_dir)s",

    "set_compiler_path": "export PATH=$PATH:$%(compiler)s_PATH",

    # A small subset of  string substitution params is allowed in commands.
    # tfm_build_manager will replace %(_tbm_build_dir_)s,  %(_tbm_code_dir_)s,
    # _tbm_target_platform_ with the  paths set when building

    "artifact_capture_rex": (r'%(_tbm_build_dir_)s/bin'
                             r'/(\w+\.(?:axf|bin|hex))$'),

    # ALL commands will be executed for every build.
    # Other keys will append extra commands when matching target_platform
    "build_cmds": {"all": ["cmake --build ./ -- install"],
                   "arm/musca_b1": [("srec_cat "
                                 "%(_tbm_build_dir_)s/bin/"
                                 "bl2.bin "
                                 "-Binary -offset 0xA000000 "
                                 "-fill 0xFF 0xA000000 0xA020000 "
                                 "%(_tbm_build_dir_)s/bin/"
                                 "tfm_s_ns_signed.bin "
                                 "-Binary -offset 0xA020000 "
                                 "-fill 0xFF 0xA020000 0xA200000 "
                                 "-o %(_tbm_build_dir_)s/bin/"
                                 "tfm.hex -Intel")],
                   "arm/musca_s1": [("srec_cat "
                                 "%(_tbm_build_dir_)s/bin/"
                                 "bl2.bin "
                                 "-Binary -offset 0xA000000 "
                                 "-fill 0xFF 0xA000000 0xA020000 "
                                 "%(_tbm_build_dir_)s/bin/"
                                 "tfm_s_ns_signed.bin "
                                 "-Binary -offset 0xA020000 "
                                 "-fill 0xFF 0xA020000 0xA200000 "
                                 "-o %(_tbm_build_dir_)s/bin/"
                                 "tfm.hex -Intel")],
                   "stm/stm32l562e_dk": [("echo 'STM32L562E-DK board post process';"
                                          "%(_tbm_build_dir_)s/postbuild.sh;"
                                          "pushd %(_tbm_build_dir_)s;"
                                          "BIN_FILES=$(grep -o '\/.*\.bin' TFM_UPDATE.sh | sed 's/^/bin/');"
                                          "tar jcf ./bin/stm32l562e-dk-tfm.tar.bz2 regression.sh TFM_UPDATE.sh ${BIN_FILES};"
                                          "popd")],
                   "stm/b_u585i_iot02a": [("echo 'STM32U5 board post process';"
                                          "%(_tbm_build_dir_)s/postbuild.sh;"
                                          "pushd %(_tbm_build_dir_)s;"
                                          "BIN_FILES=$(grep -o '\/.*\.bin' TFM_UPDATE.sh | sed 's/^/bin/');"
                                          "tar jcf ./bin/b_u585i_iot02a-tfm.tar.bz2 regression.sh TFM_UPDATE.sh ${BIN_FILES};"
                                          "popd")],
                  "nxp/lpcxpresso55s69": [("echo 'LPCXpresso55S69 board post process\n';"
                                            "if [ -f \"%(_tbm_build_dir_)s/bin/bl2.hex\" ]; then FLASH_FILE='flash_bl2_JLink.py'; else FLASH_FILE='flash_JLink.py'; fi;"
                                            "pushd %(_tbm_build_dir_)s/../platform/ext/target/nxp/lpcxpresso55s69/scripts;"
                                            "LN=$(grep -n 'JLinkExe' ${FLASH_FILE}|awk -F: '{print $1}');"
                                            "sed -i \"${LN}s/.*/    print('flash.jlink generated')/\" ${FLASH_FILE};"
                                            "python3 ./${FLASH_FILE};"
                                            "cd %(_tbm_build_dir_)s/bin;"
                                            "BIN_FILES=$(grep loadfile flash.jlink | awk '{print $2}');"
                                            "tar jcf lpcxpresso55s69-tfm.tar.bz2 flash.jlink ${BIN_FILES};"
                                            "popd")],
                   "cypress/psoc64": [("echo 'Sign binaries for Cypress PSoC64 platform';"
                                       "pushd %(_tbm_build_dir_)s/..;"
                                       "sudo /usr/local/bin/cysecuretools "
                                       "--policy platform/ext/target/cypress/psoc64/security/policy/policy_multi_CM0_CM4_tfm.json "
                                       "--target cy8ckit-064s0s2-4343w "
                                       "sign-image "
                                       "--hex %(_tbm_build_dir_)s/bin/tfm_s.hex "
                                       "--image-type BOOT --image-id 1;"
                                       "sudo /usr/local/bin/cysecuretools "
                                       "--policy platform/ext/target/cypress/psoc64/security/policy/policy_multi_CM0_CM4_tfm.json "
                                       "--target cy8ckit-064s0s2-4343w "
                                       "sign-image "
                                       "--hex %(_tbm_build_dir_)s/bin/tfm_ns.hex "
                                       "--image-type BOOT --image-id 16;"
                                       "mv %(_tbm_build_dir_)s/bin/tfm_s.hex %(_tbm_build_dir_)s/bin/tfm_s_signed.hex;"
                                       "mv %(_tbm_build_dir_)s/bin/tfm_ns.hex %(_tbm_build_dir_)s/bin/tfm_ns_signed.hex;"
                                       "popd")]
                   },

    # (Optional) If set will fail if those artefacts are missing post build
    "required_artefacts": {"all": [
                           "%(_tbm_build_dir_)s/bin/"
                           "tfm_s.bin",
                           "%(_tbm_build_dir_)s/bin/"
                           "tfm_ns.bin"],
                           "arm/musca_b1": [
                           "%(_tbm_build_dir_)s/bin/"
                           "tfm.hex",
                           "%(_tbm_build_dir_)s/bin/"
                           "bl2.bin",
                           "%(_tbm_build_dir_)s/bin/"
                           "tfm_sign.bin"],
                           "arm/musca_s1": [
                           "%(_tbm_build_dir_)s/bin/"
                           "tfm.hex",
                           "%(_tbm_build_dir_)s/bin/"
                           "bl2.bin",
                           "%(_tbm_build_dir_)s/bin/"
                           "tfm_sign.bin"]
                           }
}

# List of all build configs that are impossible under all circumstances
_common_tfm_invalid_configs = [
    # LR_CODE size exceeds limit on MUSCA_B1 & MUSCA_S1 with regression tests in Debug mode built with ARMCLANG
    ("arm/musca_b1", "ARMCLANG_6_13", "*", "RegBL2, RegS, RegNS", "OFF", "Debug", "*", "", "*"),
    ("arm/musca_s1", "ARMCLANG_6_13", "*", "RegBL2, RegS, RegNS", "OFF", "Debug", "*", "", "*"),
    # Load range overlap on Musca for IPC Debug type: T895
    ("arm/musca_b1", "ARMCLANG_6_13", "*", "*", "IPC", "Debug", "*", "*", "*"),
    ("arm/musca_s1", "ARMCLANG_6_13", "*", "*", "IPC", "Debug", "*", "*", "*"),
    # FF does not support L3
    ("*", "*", "3", "*", "IPC", "*", "*", "*", "*"),
    # Musca requires BL2
    ("arm/musca_b1", "*", "*", "*", "*", "*", False, "*", "*"),
    ("arm/musca_s1", "*", "*", "*", "*", "*", False, "*", "*"),
    # Only AN521 and MUSCA_B1 support Isolation Level 3
    ("arm/mps2/an519", "*", "3", "*", "*", "*", "*", "*", "*"),
    ("arm/mps3/an524", "*", "3", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_s1", "*", "3", "*", "*", "*", "*", "*", "*"),
    ]

# Configure build manager to build several combinations
# Config group for per-patch job
config_pp_test = {"seed_params": {
                # AN519_ARMCLANG_IPC_1_RegBL2_RegS_RegNS_Debug_BL2
                "tfm_platform":     ["arm/mps2/an519"],
                "compiler":         ["ARMCLANG_6_13"],
                "isolation_level":  ["1"],
                "test_regression":  ["RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "valid": [
                    # AN519_ARMCLANG_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps2/an519", "ARMCLANG_6_13", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "",  ""),
                    # AN519_GCC_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps2/an519", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "",  ""),
                    # AN519_GCC_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps2/an519", "GCC_10_3", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # AN519_GCC_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps2/an519", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2_SMALL_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_13", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "profile_small", "PSOFF"),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_13", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # AN521_ARMCLANG_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_13", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # AN521_ARMCLANG_3_RegBL2_RegS_RegNS_Minsizerel_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_13", "3",
                     "RegBL2, RegS, RegNS", "OFF", "Minsizerel", True, "", ""),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2_SMALL_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_13", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "profile_small", "PSOFF"),
                    # AN521_GCC_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps2/an521", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # AN521_GCC_2_Debug_BL2_MEDIUM
                    ("arm/mps2/an521", "GCC_10_3", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "profile_medium", ""),
                    # AN521_GCC_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps2/an521", "GCC_10_3", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # AN521_GCC_3_RegBL2_RegS_RegNS_Minsizerel_BL2
                    ("arm/mps2/an521", "GCC_10_3", "3",
                     "RegBL2, RegS, RegNS", "OFF", "Minsizerel", True, "", ""),
                    # AN521_GCC_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps2/an521", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # AN552_GNUARM_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps3/an552", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # AN552_GNUARM_1_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps3/an552", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # MUSCA_B1_GCC_1_RegBL2_RegS_RegNS_Minsizerel_BL2
                    ("arm/musca_b1", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Minsizerel", True, "", ""),
                    # MUSCA_S1_ARMCLANG_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/musca_s1", "ARMCLANG_6_13", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # MUSCA_S1_GCC_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/musca_s1", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # MUSCA_S1_GCC_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/musca_s1", "GCC_10_3", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # MUSCA_S1_GCC_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/musca_s1", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # MUSCA_S1_GCC_1_RegBL2_RegS_RegNS_Release_BL2_CC_DRIVER_PSA
                    ("arm/musca_s1", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", "CC_DRIVER_PSA"),
                    # RSS_TC_GCC_2_Release_BL2_PSOFF
                    ("arm/rss/tc", "GCC_10_3", "2",
                     "RegS, RegNS", "OFF", "Release", True, "", "PSOFF"),
                    # stm32l562e_dk_ARMCLANG_1_RegS_RegNS_Release_BL2_CRYPTO_OFF
                    ("stm/stm32l562e_dk", "ARMCLANG_6_13", "1",
                     "RegS, RegNS", "OFF", "Release", True, "", "CRYPTO_OFF"),
                    # stm32l562e_dk_GCC_2_Release_BL2_CRYPTO_ON
                    ("stm/stm32l562e_dk", "GCC_10_3", "2",
                     "OFF", "OFF", "Release", True, "", "CRYPTO_ON"),
                    # stm32l562e_dk_GCC_3_RegS_RegNS_Release_BL2_CRYPTO_OFF
                    ("stm/stm32l562e_dk", "GCC_10_3", "3",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", "CRYPTO_OFF"),
                    # b_u585i_iot02a_GCC_1_RegS_RegNS_Release_BL2
                    ("stm/b_u585i_iot02a", "GCC_10_3", "1",
                     "RegS, RegNS", "OFF", "Release", True, "", ""),
                    # b_u585i_iot02a_ARMCLANG_2_RegS_RegNS_Release_BL2
                    ("stm/b_u585i_iot02a", "ARMCLANG_6_13", "2",
                     "RegS, RegNS", "OFF", "Release", True, "", ""),
                    # psoc64_GCC_2_RegS_RegNS_Release
                    ("cypress/psoc64", "GCC_10_3", "2",
                     "RegS, RegNS", "OFF", "Release", False, "", ""),
                ],
                "invalid": _common_tfm_invalid_configs + []
                }

# Config group for nightly job
config_nightly_test = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an519",
                                     "arm/mps2/an521",
                                     "arm/mps3/an524",
                                     "arm/musca_s1",
                                     "arm/musca_b1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

# Config group for release job
config_release_test = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519",
                                     "arm/mps2/an521",
                                     "arm/mps3/an524",
                                     "arm/musca_b1",
                                     "arm/musca_s1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["TEST_CBOR"]
                },
                "common_params": _common_tfm_builder_cfg,
                "valid": [
                    # sanity test for GCC v11.2
                    # AN521_GCC_3_RegBL2_RegS_RegNS_Relwithdebinfo_BL2
                    ("arm/mps2/an521", "GCC_11_2",
                     "3", "RegBL2, RegS, RegNS", "OFF", "Relwithdebinfo",
                     True, "", ""),
                ],
                "invalid": _common_tfm_invalid_configs + []
                }

# Config groups for TF-M features
config_profile_s = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519", "arm/mps2/an521"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          ["profile_small"],
                "extra_params":     ["PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "GCC_10_3", "*", "*",
                     "*", "Minsizerel", "*", "*", "*")
                ]
                }

config_profile_m = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519",
                                     "arm/mps2/an521",
                                     "arm/musca_b1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["2"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          ["profile_medium"],
                "extra_params":     ["", "PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_profile_m_debug = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["2"],
                "test_regression":  ["Regs, RegNS"],# , "OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          ["profile_medium"],
                "extra_params":     ["PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_profile_m_arotless = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          ["profile_medium_arotless"],
                "extra_params":     ["", "PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_profile_l = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["3"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          ["profile_large"],
                "extra_params":     ["", "PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_ipc_backend = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an519",
                                     "arm/mps2/an521",
                                     "arm/musca_s1",
                                     "arm/musca_b1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["IPC"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_cc_driver_psa = {"seed_params": {
               "tfm_platform":      ["arm/musca_b1",
                                     "arm/musca_s1"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["CC_DRIVER_PSA"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_fp = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521",
                                     "arm/mps3/an552"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["FPOFF", "FPON", "FPON, LZOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_psa_api = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521",
                                     "arm/musca_b1",
                                     "arm/musca_s1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["IPC",
                                     "CRYPTO",
                                     "INITIAL_ATTESTATION",
                                     "STORAGE"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nsce = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an521"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  ["RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSCE"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_mmio = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an521"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1"],
                "test_regression":  ["RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["MMIO"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

# Config groups for TF-M examples
config_example_vad = {"seed_params": {
                "tfm_platform":     ["arm/mps3/an552"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["2"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["EXAMPLE_VAD"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_example_dma350_ns = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["2"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["EXAMPLE_DMA350_NS"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_example_dma350_s = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["EXAMPLE_DMA350_S"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_example_dma350_trigger = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["2"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["EXAMPLE_DMA350_TRIGGER"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_misra = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          ["profile_small", "profile_medium_arotless", "profile_medium", "profile_large"],
                "extra_params":     ["PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "GCC_10_3", "*", "*",
                     "*", "Minsizerel", "*", "*", "*")
                ]
                }

# Config groups for code coverage
config_cov_profile_s = deepcopy(config_profile_s)
config_cov_profile_s["seed_params"]["tfm_platform"] = ["arm/mps2/an521"]
config_cov_profile_s["seed_params"]["compiler"] = ["GCC_10_3"]

config_cov_profile_m = deepcopy(config_profile_m)
config_cov_profile_m["seed_params"]["tfm_platform"] = ["arm/mps2/an521"]
config_cov_profile_m["seed_params"]["compiler"] = ["GCC_10_3"]

config_cov_profile_l = deepcopy(config_profile_l)
config_cov_profile_l["seed_params"]["tfm_platform"] = ["arm/mps2/an521"]
config_cov_profile_l["seed_params"]["compiler"] = ["GCC_10_3"]

config_cov_ipc_backend = deepcopy(config_ipc_backend)
config_cov_ipc_backend["seed_params"]["tfm_platform"] = ["arm/mps2/an521"]
config_cov_ipc_backend["seed_params"]["compiler"] = ["GCC_10_3"]

config_cov_nsce = deepcopy(config_nsce)
config_cov_nsce["seed_params"]["tfm_platform"] = ["arm/mps2/an521"]
config_cov_nsce["seed_params"]["compiler"] = ["GCC_10_3"]

config_cov_mmio = deepcopy(config_mmio)
config_cov_mmio["seed_params"]["tfm_platform"] = ["arm/mps2/an521"]
config_cov_mmio["seed_params"]["compiler"] = ["GCC_10_3"]

config_cov_fp = deepcopy(config_fp)
config_cov_fp["seed_params"]["tfm_platform"] = ["arm/mps2/an521"]
config_cov_fp["seed_params"]["compiler"] = ["GCC_10_3"]

# Config groups for platforms
config_an519 = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True, False],
                "profile":          [""],
                "extra_params":     ["", "NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_an521 = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True, False],
                "profile":          [""],
                "extra_params":     ["", "NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_an524 = {"seed_params": {
                "tfm_platform":     ["arm/mps3/an524"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True, False],
                "profile":          [""],
                "extra_params":     ["", "NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_an547 = {"seed_params": {
                "tfm_platform":     ["arm/mps3/an547"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_an552 = {"seed_params": {
                "tfm_platform":     ["arm/mps3/an552"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_musca_b1 = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["", "NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_musca_s1 = {"seed_params": {
                "tfm_platform":     ["arm/musca_s1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["", "NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_corstone310 = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_rss = {"seed_params": {
                "tfm_platform":     ["arm/rss/tc"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    # BL2 is too large for RSS in Debug builds with tests
                    ("arm/rss/tc", "GCC_10_3", "*", "RegBL2, RegS, RegNS", "*",
                     "Debug", True, "*", "*"),
                ]
                }

config_psoc64 = {"seed_params": {
                "tfm_platform":     ["cypress/psoc64"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [False],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_corstone1000 = {"seed_params": {
                "tfm_platform":     ["arm/corstone1000"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["RegBL2, RegS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["CS1K_TEST, FVP", "CS1K_TEST, FPGA"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_stm32l562e_dk = {"seed_params": {
                "tfm_platform":     ["stm/stm32l562e_dk"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  ["OFF", "RegBL2, RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["CRYPTO_OFF", "CRYPTO_ON"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    # Oversize issue on config stm32l562e_dk_ARMCLANG_1_RegBL2_RegS_RegNS_Release_BL2
                    ("stm/stm32l562e_dk", "ARMCLANG_6_13", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", "*"),
                    # all other tests are off when CRYPTO is ON
                    ("stm/stm32l562e_dk", "*", "*", "RegBL2, RegS, RegNS", "*",
                     "*", "*", "*", "CRYPTO_ON"),
                    # all other tests are ON when CRYPTO is OFF
                    ("stm/stm32l562e_dk", "*", "*", "OFF", "*",
                     "*", "*", "*", "CRYPTO_OFF"),
                ]
                }

config_b_u585i_iot02a = {"seed_params": {
                "tfm_platform":     ["stm/b_u585i_iot02a"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_13"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF", "RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nucleo_l552ze_q = {"seed_params": {
                "tfm_platform":     ["stm/nucleo_l552ze_q"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_lpcxpresso55s69 = {"seed_params": {
                "tfm_platform":     ["nxp/lpcxpresso55s69"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["2"],
                "test_regression":  ["OFF", "RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Relwithdebinfo"],
                "with_bl2":         [False],
                "profile":          ["profile_medium"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_bl5340 = {"seed_params": {
                "tfm_platform":     ["lairdconnectivity/bl5340_dvk_cpuapp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nrf5340dk = {"seed_params": {
                "tfm_platform":     ["nordic_nrf/nrf5340dk_nrf5340_cpuapp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nrf9160dk = {"seed_params": {
                "tfm_platform":     ["nordic_nrf/nrf9160dk_nrf9160"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_m2351 = {"seed_params": {
                "tfm_platform":     ["nuvoton/m2351"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_m2354 = {"seed_params": {
                "tfm_platform":     ["nuvoton/m2354"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

# Config groups for debug
config_debug = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_debug_regr = deepcopy(config_debug)
config_debug_regr["seed_params"]["test_regression"] = ["RegBL2, RegS, RegNS"]

config_debug_PSA_API = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "compiler":         ["ARMCLANG_6_13"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["CRYPTO",
                                     "INITIAL_ATTESTATION",
                                     "STORAGE",
                                     "IPC"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

_builtin_configs = {
                    # per-patch test groups
                    "pp_test": config_pp_test,
                    #"pp_corstone1000": config_corstone1000,

                    # nightly test groups
                    "nightly_test": config_nightly_test,
                    "nightly_profile_s": config_profile_s,
                    "nightly_profile_m": config_profile_m,
                    "nightly_profile_m_arotless": config_profile_m_arotless,
                    "nightly_profile_l": config_profile_l,
                    "nightly_ipc_backend": config_ipc_backend,
                    "nightly_cc_driver_psa": config_cc_driver_psa,
                    "nightly_fp":config_fp,
                    "nightly_psa_api": config_psa_api,
                    "nightly_nsce": config_nsce,
                    "nightly_mmio": config_mmio,
                    "nightly_an547": config_an547,
                    "nightly_an552": config_an552,
                    "nightly_corstone310": config_corstone310,
                    #"nightly_corstone1000": config_corstone1000,
                    "nightly_rss": config_rss,
                    "nightly_psoc64": config_psoc64,
                    "nightly_stm32l562e_dk": config_stm32l562e_dk,
                    "nightly_b_u585i_iot02a": config_b_u585i_iot02a,
                    "nightly_lpcxpresso55s69": config_lpcxpresso55s69,

                    # release test groups
                    "release_test": config_release_test,
                    "release_profile_s": config_profile_s,
                    "release_profile_m": config_profile_m,
                    "release_profile_m_arotless": config_profile_m_arotless,
                    "release_profile_l": config_profile_l,
                    "release_ipc_backend": config_ipc_backend,
                    "release_cc_driver_psa": config_cc_driver_psa,
                    "release_fp": config_fp,
                    "release_psa_api": config_psa_api,
                    "release_nsce": config_nsce,
                    "release_mmio": config_mmio,
                    "release_an547": config_an547,
                    "release_an552": config_an552,
                    "release_corstone310": config_corstone310,
                    "release_rss": config_rss,
                    "release_psoc64": config_psoc64,
                    "release_stm32l562e_dk": config_stm32l562e_dk,
                    "release_b_u585i_iot02a": config_b_u585i_iot02a,
                    "release_lpcxpresso55s69": config_lpcxpresso55s69,

                    # code coverage test groups
                    "coverage_profile_s": config_cov_profile_s,
                    "coverage_profile_m": config_cov_profile_m,
                    "coverage_profile_m_debug": config_profile_m_debug,
                    "coverage_profile_l": config_cov_profile_l,
                    "coverage_ipc_backend": config_cov_ipc_backend,
                    "coverage_nsce": config_cov_nsce,
                    "coverage_mmio": config_cov_mmio,
                    "coverage_fp": config_cov_fp,

                    # MISRA analysis
                    "misra": config_misra,

                    # platform groups
                    "an521": config_an521,
                    "an519": config_an519,
                    "an524": config_an524,
                    "an547": config_an547,
                    "an552": config_an552,
                    "musca_b1": config_musca_b1,
                    "musca_s1": config_musca_s1,
                    "corstone310": config_corstone310,
                    "rss": config_rss,
                    "cypress_psoc64": config_psoc64,
                    #"corstone1000": config_corstone1000,
                    "stm_stm32l562e_dk": config_stm32l562e_dk,
                    "stm_b_u585i_iot02a": config_b_u585i_iot02a,
                    "stm_nucleo_l552ze_q": config_nucleo_l552ze_q,
                    "nxp_lpcxpresso55s69": config_lpcxpresso55s69,
                    "laird_bl5340": config_bl5340,
                    "nordic_nrf5340dk": config_nrf5340dk,
                    "nordic_nrf9160dk": config_nrf9160dk,
                    "nuvoton_m2351": config_m2351,
                    "nuvoton_m2354": config_m2354,

                    # config groups for tf-m-extras examples
                    "example_vad": config_example_vad,
                    "example_dma350_trigger": config_example_dma350_trigger,
                    "example_dma350_ns": config_example_dma350_ns,
                    "example_dma350_s": config_example_dma350_s,

                    # config groups for debug
                    "debug": config_debug,
                    "debug_regr": config_debug_regr,
                    "debug_PSA_API": config_debug_PSA_API,
                }

if __name__ == '__main__':
    import os

    # Default behavior is to export refference config when called
    _dir = os.getcwd()
    from utils import save_json
    for _cname, _cfg in _builtin_configs.items():
        _fname = os.path.join(_dir, _cname + ".json")
        print("Exporting config %s" % _fname)
        save_json(_fname, _cfg)
