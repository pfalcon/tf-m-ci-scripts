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

    "spe_config_template": "cmake -G Ninja " + \
        "-S %(tfm_tests_root_dir)s/%(test_root_dir)s/spe " + \
        "-B %(ci_build_root_dir)s/spe " + \
        "-DTFM_PLATFORM=%(tfm_platform)s " + \
        "-DTFM_TOOLCHAIN_FILE=%(codebase_root_dir)s/%(s_compiler)s " + \
        "-DTFM_ISOLATION_LEVEL=%(isolation_level)s " + \
        "%(test_regression)s " + \
        "-DCMAKE_BUILD_TYPE=%(cmake_build_type)s " + \
        "-DTEST_PSA_API=%(test_psa_api)s " + \
        "-DBL2=%(with_bl2)s " + \
        "-DTFM_PROFILE=%(profile)s " + \
        "%(extra_params)s " + \
        "-DCONFIG_TFM_SOURCE_PATH=%(codebase_root_dir)s " + \
        "-DMBEDCRYPTO_PATH=%(codebase_root_dir)s/../mbedtls " + \
        "-DPSA_ARCH_TESTS_PATH=%(codebase_root_dir)s/../psa-arch-tests " + \
        "-DMCUBOOT_PATH=%(codebase_root_dir)s/../mcuboot " + \
        "-DQCBOR_PATH=%(codebase_root_dir)s/../qcbor " + \
        "-DTFM_EXTRAS_REPO_PATH=%(codebase_root_dir)s/../tf-m-extras ",

    "nspe_config_template": "cmake -G Ninja " + \
        "-S %(tfm_tests_root_dir)s/%(test_root_dir)s " + \
        "-B %(ci_build_root_dir)s/nspe " + \
        "-DCONFIG_SPE_PATH=%(ci_build_root_dir)s/spe/api_ns " + \
        "-DTFM_TOOLCHAIN_FILE=%(ci_build_root_dir)s/spe/api_ns/cmake/%(ns_compiler)s " + \
        "%(extra_params)s " + \
        "-DQCBOR_PATH=%(codebase_root_dir)s/../qcbor ",

    # CMake build commands will be executed for every build.
    "spe_cmake_build":  "cmake --build %(ci_build_root_dir)s/spe -- install",
    "nspe_cmake_build": "cmake --build %(ci_build_root_dir)s/nspe --",

    "set_compiler_path": "export PATH=$PATH:$%(compiler)s_PATH",

    # A small subset of  string substitution params is allowed in commands.
    # tfm_build_manager will replace %(_tbm_build_dir_)s,  %(_tbm_code_dir_)s,
    # _tbm_target_platform_ with the  paths set when building

    "artifact_capture_rex": (r'%(ci_build_root_dir)s/nspe'
                             r'/(\w+\.(?:axf|bin|hex))$'),

    # Keys will append extra commands when matching target_platform
    "post_build": {"arm/corstone1000": ("dd conv=notrunc bs=1 if=%(ci_build_root_dir)s/spe/bin/bl1_1.bin of=%(ci_build_root_dir)s/spe/bin/bl1.bin seek=0;"
                                        "dd conv=notrunc bs=1 if=%(ci_build_root_dir)s/spe/bin/bl1_provisioning_bundle.bin of=%(ci_build_root_dir)s/spe/bin/bl1.bin seek=40960;"
                                        "%(codebase_root_dir)s/platform/ext/target/arm/corstone1000/create-flash-image.sh %(ci_build_root_dir)s/spe/bin/ cs1000.bin;"),
                    "arm/musca_b1": ("srec_cat "
                                     "%(ci_build_root_dir)s/spe/bin/"
                                     "bl2.bin "
                                     "-Binary -offset 0xA000000 "
                                     "-fill 0xFF 0xA000000 0xA020000 "
                                     "%(ci_build_root_dir)s/nspe/"
                                     "tfm_s_ns_signed.bin "
                                     "-Binary -offset 0xA020000 "
                                     "-fill 0xFF 0xA020000 0xA200000 "
                                     "-o %(ci_build_root_dir)s/"
                                     "spe/bin/tfm.hex -Intel"),
                   "arm/musca_s1": ("srec_cat "
                                    "%(ci_build_root_dir)s/spe/bin/"
                                    "bl2.bin "
                                    "-Binary -offset 0xA000000 "
                                    "-fill 0xFF 0xA000000 0xA020000 "
                                    "%(ci_build_root_dir)s/nspe/"
                                    "tfm_s_ns_signed.bin "
                                    "-Binary -offset 0xA020000 "
                                    "-fill 0xFF 0xA020000 0xA200000 "
                                    "-o %(ci_build_root_dir)s/"
                                    "spe/bin/tfm.hex -Intel"),
                   "stm/stm32l562e_dk": ("echo 'STM32L562E-DK board post process';"
                                          "%(ci_build_root_dir)s/spe/api_ns/postbuild.sh;"
                                          "pushd %(ci_build_root_dir)s/spe/api_ns;"
                                          "mkdir -p image_signing/scripts ;"
                                          "cp %(ci_build_root_dir)s/nspe/bin/tfm_ns_signed.bin image_signing/scripts ;"
                                          "tar jcf ./bin/stm32l562e-dk-tfm.tar.bz2 regression.sh TFM_UPDATE.sh "
                                          "bin/bl2.bin "
                                          "bin/tfm_s_signed.bin "
                                          "image_signing/scripts/tfm_ns_signed.bin ;"
                                          "popd"),
                   "stm/b_u585i_iot02a": ("echo 'STM32U5 board post process';"
                                          "%(ci_build_root_dir)s/spe/api_ns/postbuild.sh;"
                                          "pushd %(ci_build_root_dir)s/spe/api_ns;"
                                          "mkdir -p image_signing/scripts ;"
                                          "cp %(ci_build_root_dir)s/nspe/bin/tfm_ns_signed.bin image_signing/scripts ;"
                                          "tar jcf ./bin/b_u585i_iot02a-tfm.tar.bz2 regression.sh TFM_UPDATE.sh "
                                          "bin/bl2.bin "
                                          "bin/tfm_s_signed.bin "
                                          "image_signing/scripts/tfm_ns_signed.bin ;"
                                          "popd"),
                  "nxp/lpcxpresso55s69": ("echo 'LPCXpresso55S69 board post process\n';"
                                            "if [ -f \"%(ci_build_root_dir)s/spe/bin/bl2.hex\" ]; then FLASH_FILE='flash_bl2_JLink.py'; else FLASH_FILE='flash_JLink.py'; fi;"
                                            "mkdir -p %(codebase_root_dir)s/build/bin ;"
                                            # Workaround for flash_JLink.py
                                            "cp %(ci_build_root_dir)s/spe/bin/tfm_s.hex %(codebase_root_dir)s/build/bin ;"
                                            "cp %(ci_build_root_dir)s/nspe/bin/tfm_ns.hex %(codebase_root_dir)s/build/bin ;"
                                            "pushd %(codebase_root_dir)s/platform/ext/target/nxp/lpcxpresso55s69/scripts;"
                                            "LN=$(grep -n 'JLinkExe' ${FLASH_FILE}|awk -F: '{print $1}');"
                                            "sed -i \"${LN}s/.*/    print('flash.jlink generated')/\" ${FLASH_FILE};"
                                            "python3 ./${FLASH_FILE};"
                                            "cd %(codebase_root_dir)s/build/bin;"
                                            "BIN_FILES=$(grep loadfile flash.jlink | awk '{print $2}');"
                                            "tar jcf lpcxpresso55s69-tfm.tar.bz2 flash.jlink ${BIN_FILES};"
                                            "mv lpcxpresso55s69-tfm.tar.bz2 %(ci_build_root_dir)s/nspe/bin ;"
                                            "popd"),
                   "cypress/psoc64": ("echo 'Sign binaries for Cypress PSoC64 platform';"
                                       "pushd %(codebase_root_dir)s/;"
                                       "sudo /usr/local/bin/cysecuretools "
                                       "--policy platform/ext/target/cypress/psoc64/security/policy/policy_multi_CM0_CM4_tfm.json "
                                       "--target cy8ckit-064s0s2-4343w "
                                       "sign-image "
                                       "--hex %(ci_build_root_dir)s/spe/bin/tfm_s.hex "
                                       "--image-type BOOT --image-id 1;"
                                       "sudo /usr/local/bin/cysecuretools "
                                       "--policy platform/ext/target/cypress/psoc64/security/policy/policy_multi_CM0_CM4_tfm.json "
                                       "--target cy8ckit-064s0s2-4343w "
                                       "sign-image "
                                       "--hex %(ci_build_root_dir)s/nspe/bin/tfm_ns.hex "
                                       "--image-type BOOT --image-id 16;"
                                       "mv %(ci_build_root_dir)s/spe/bin/tfm_s.hex %(ci_build_root_dir)s/spe/bin/tfm_s_signed.hex;"
                                       "mv %(ci_build_root_dir)s/nspe/bin/tfm_ns.hex %(ci_build_root_dir)s/nspe/bin/tfm_ns_signed.hex;"
                                       "popd")
                   },

    # (Optional) If set will fail if those artefacts are missing post build
    "required_artefacts": {"all": [
                           "%(ci_build_root_dir)s/spe/bin/"
                           "tfm_s.bin",
                           "%(ci_build_root_dir)s/nspe/"
                           "tfm_ns.bin"],
                           "arm/musca_b1": [
                           "%(ci_build_root_dir)s/tfm.hex",
                           "%(ci_build_root_dir)s/spe/bin/"
                           "bl2.bin",
                           "%(ci_build_root_dir)s/spe/bin/"
                           "tfm_sign.bin"],
                           "arm/musca_s1": [
                           "%(ci_build_root_dir)s/tfm.hex",
                           "%(ci_build_root_dir)s/spe/bin/"
                           "bl2.bin",
                           "%(ci_build_root_dir)s/spe/bin/"
                           "tfm_sign.bin"]
                           }
}

# List of all build configs that are impossible under all circumstances
_common_tfm_invalid_configs = [
    # LR_CODE size exceeds limit on MUSCA_B1 & MUSCA_S1 with regression tests in Debug mode built with ARMCLANG
    ("arm/musca_b1", "ARMCLANG_6_18", "*", "RegBL2, RegS, RegNS", "OFF", "Debug", "*", "", "*"),
    ("arm/musca_s1", "ARMCLANG_6_18", "*", "RegBL2, RegS, RegNS", "OFF", "Debug", "*", "", "*"),
    # Load range overlap on Musca for IPC Debug type: T895
    ("arm/musca_b1", "ARMCLANG_6_18", "*", "*", "IPC", "Debug", "*", "*", "*"),
    ("arm/musca_s1", "ARMCLANG_6_18", "*", "*", "IPC", "Debug", "*", "*", "*"),
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
                "compiler":         ["ARMCLANG_6_18"],
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
                    ("arm/mps2/an519", "ARMCLANG_6_18", "2",
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
                    ("arm/mps2/an521", "ARMCLANG_6_18", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "profile_small", "PSOFF"),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_18", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2_IPC
                    ("arm/mps2/an521", "ARMCLANG_6_18", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", "IPC"),
                    # AN521_ARMCLANG_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_18", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # AN521_ARMCLANG_3_RegBL2_RegS_RegNS_Minsizerel_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_18", "3",
                     "RegBL2, RegS, RegNS", "OFF", "Minsizerel", True, "", ""),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2_SMALL_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_18", "1",
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
                    # AN521_GCC_1_FF_Release_BL2
                    ("arm/mps2/an521", "GCC_10_3", "1",
                     "OFF", "IPC", "Release", True, "", ""),
                    # AN521_ARMCLANG_2_STORAGE_Debug_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_18", "2",
                     "OFF", "STORAGE", "Debug", True, "", ""),
                    # CS300_FVP_GNUARM_2_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps3/corstone300/fvp", "GCC_10_3", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # CS300_FVP_GNUARM_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps3/corstone300/fvp", "GCC_10_3", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # MUSCA_B1_GCC_1_RegBL2_RegS_RegNS_Minsizerel_BL2
                    ("arm/musca_b1", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Minsizerel", True, "", ""),
                    # MUSCA_S1_ARMCLANG_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/musca_s1", "ARMCLANG_6_18", "2",
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
                    # stm32l562e_dk_ARMCLANG_1_RegS_RegNS_Release_BL2_CRYPTO_OFF
                    ("stm/stm32l562e_dk", "ARMCLANG_6_18", "1",
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
                    ("stm/b_u585i_iot02a", "ARMCLANG_6_18", "2",
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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

config_profile_m_arotless = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                                     "arm/mps3/corstone300/an552",
                                     "arm/mps3/corstone300/fvp"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "tfm_platform":     ["arm/mps3/corstone300/an552"],
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

config_example_dma350_clcd = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["2"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["EXAMPLE_DMA350_CLCD"]
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

config_example_dma350_ns = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
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
                "tfm_platform":     ["arm/musca_b1"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          ["profile_small", "profile_medium_arotless"],
                "extra_params":     ["PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "valid": [
                    # MUSCA_B1_GCC_2_Debug_BL2_MEDIUM_PSOFF
                    ("arm/musca_b1", "GCC_10_3", "2", "OFF",
                     "OFF", "Debug", True, "profile_medium", "PSOFF"),
                    # MUSCA_B1_GCC_3_Debug_BL2_LARGE_PSOFF
                    ("arm/musca_b1", "GCC_10_3", "3", "OFF",
                     "OFF", "Debug", True, "profile_large", "PSOFF"),
                ],
                "invalid": _common_tfm_invalid_configs + []
                }

config_misra_debug = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          ["profile_small"],
                "extra_params":     ["PSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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

config_cs300_an547 = {"seed_params": {
                      "tfm_platform":     ["arm/mps3/corstone300/an547"],
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

config_cs300_an552 = {"seed_params": {
                      "tfm_platform":     ["arm/mps3/corstone300/an552"],
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

config_cs300_fvp = {"seed_params": {
                    "tfm_platform":     ["arm/mps3/corstone300/fvp"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                "test_regression":  ["RegS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF, CS1K_TEST, FVP", "NSOFF, CS1K_TEST, FPGA"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_stm32l562e_dk = {"seed_params": {
                "tfm_platform":     ["stm/stm32l562e_dk"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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
                    ("stm/stm32l562e_dk", "ARMCLANG_6_18", "1",
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_18"],
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

config_mem_footprint = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an521"],
                "compiler":         ["ARMCLANG_6_18"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Minsizerel"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "valid": [
                    # AN521_ARMCLANG_1_Minsizerel_BL2_SMALL_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_18", "1",
                     "OFF", "OFF", "Minsizerel", True, "profile_small", "PSOFF"),
                    # AN521_ARMCLANG_2_Minsizerel_BL2_MEDIUM_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_18", "2",
                     "OFF", "OFF", "Minsizerel", True, "profile_medium", "PSOFF"),
                    # AN521_ARMCLANG_3_Minsizerel_BL2_LARGE_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_18", "3",
                     "OFF", "OFF", "Minsizerel", True, "profile_large", "PSOFF"),
                ],
                "invalid": _common_tfm_invalid_configs + []
                }

config_prof = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an521"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["PROF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "valid": [
                    # AN521_GNUARM_1_Release_BL2_IPC_PROF
                    ("arm/mps2/an521", "GCC_10_3", "1",
                     "OFF", "OFF", "Release", True, "", "IPC, PROF"),
                    # AN521_GNUARM_2_Release_BL2_PROF
                    ("arm/mps2/an521", "GCC_10_3", "2",
                     "OFF", "OFF", "Release", True, "", "PROF"),
                    # AN521_GNUARM_3_Release_BL2_PROF
                    ("arm/mps2/an521", "GCC_10_3", "3",
                     "OFF", "OFF", "Release", True, "", "PROF"),
                ],
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
                "compiler":         ["ARMCLANG_6_18"],
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
                    "pp_corstone1000": config_corstone1000,

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
                    "nightly_cs300_an547": config_cs300_an547,
                    "nightly_cs300_an552": config_cs300_an552,
                    "nightly_cs300_fvp": config_cs300_fvp,
                    "nightly_corstone310": config_corstone310,
                    "nightly_corstone1000": config_corstone1000,
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
                    "release_cs300_an547": config_cs300_an547,
                    "release_cs300_an552": config_cs300_an552,
                    "release_cs300_fvp": config_cs300_fvp,
                    "release_corstone310": config_corstone310,
                    "release_rss": config_rss,
                    "release_psoc64": config_psoc64,
                    "release_stm32l562e_dk": config_stm32l562e_dk,
                    "release_b_u585i_iot02a": config_b_u585i_iot02a,
                    "release_lpcxpresso55s69": config_lpcxpresso55s69,

                    # code coverage test groups
                    "coverage_profile_s": config_cov_profile_s,
                    "coverage_profile_m": config_cov_profile_m,
                    "coverage_profile_l": config_cov_profile_l,
                    "coverage_ipc_backend": config_cov_ipc_backend,
                    "coverage_nsce": config_cov_nsce,
                    "coverage_mmio": config_cov_mmio,
                    "coverage_fp": config_cov_fp,

                    # MISRA analysis
                    "misra": config_misra,
                    "misra_debug": config_misra_debug,

                    # platform groups
                    "an521": config_an521,
                    "an519": config_an519,
                    "an524": config_an524,
                    "cs300_an547": config_cs300_an547,
                    "cs300_an552": config_cs300_an552,
                    "cs300_fvp": config_cs300_fvp,
                    "musca_b1": config_musca_b1,
                    "musca_s1": config_musca_s1,
                    "corstone310": config_corstone310,
                    "rss": config_rss,
                    "cypress_psoc64": config_psoc64,
                    "corstone1000": config_corstone1000,
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
                    "example_dma350_clcd": config_example_dma350_clcd,
                    "example_dma350_s": config_example_dma350_s,
                    "example_dma350_ns": config_example_dma350_ns,

                    # config groups for tf-m performance monitor
                    "mem_footprint": config_mem_footprint,
                    "profiling": config_prof,

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
