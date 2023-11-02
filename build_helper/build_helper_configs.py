#!/usr/bin/env python3

""" builtin_configs.py:

    Default configuration files used as reference """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2024, Arm Limited. All rights reserved.
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
        "-S %(spe_root_dir)s " + \
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
        "-S %(nspe_root_dir)s " + \
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
                    "arm/musca_b1": ("if [ -d \"%(ci_build_root_dir)s/nspe\" ]; then "
                                     "srec_cat "
                                     "%(ci_build_root_dir)s/spe/bin/"
                                     "bl2.bin "
                                     "-Binary -offset 0xA000000 "
                                     "-fill 0xFF 0xA000000 0xA020000 "
                                     "%(ci_build_root_dir)s/nspe/"
                                     "tfm_s_ns_signed.bin "
                                     "-Binary -offset 0xA020000 "
                                     "-fill 0xFF 0xA020000 0xA200000 "
                                     "-o %(ci_build_root_dir)s/"
                                     "spe/bin/tfm.hex -Intel;"
                                     "fi;"),
                   "arm/musca_s1": ("if [ -d \"%(ci_build_root_dir)s/nspe\" ]; then "
                                    "srec_cat "
                                    "%(ci_build_root_dir)s/spe/bin/"
                                    "bl2.bin "
                                    "-Binary -offset 0xA000000 "
                                    "-fill 0xFF 0xA000000 0xA020000 "
                                    "%(ci_build_root_dir)s/nspe/"
                                    "tfm_s_ns_signed.bin "
                                    "-Binary -offset 0xA020000 "
                                    "-fill 0xFF 0xA020000 0xA200000 "
                                    "-o %(ci_build_root_dir)s/"
                                    "spe/bin/tfm.hex -Intel; "
                                    "fi;"),
                    "arm/rse/tc/tc2": ("if [ -f \"%(ci_build_root_dir)s/spe/bin/rse_bl1_tests.bin\" ]; then "
                                   "srec_cat "
                                   "%(ci_build_root_dir)s/spe/bin/bl1_1.bin -Binary -offset 0x0 "
                                   "%(ci_build_root_dir)s/spe/bin/rse_bl1_tests.bin -Binary -offset 0x10000 "
                                   "%(ci_build_root_dir)s/spe/bin/rom_dma_ics.bin -Binary -offset 0x1F000 "
                                   "-o %(ci_build_root_dir)s/spe/bin/rom.bin -Binary;"
                                   "else "
                                   "srec_cat "
                                   "%(ci_build_root_dir)s/spe/bin/bl1_1.bin -Binary -offset 0x0 "
                                   "%(ci_build_root_dir)s/spe/bin/rom_dma_ics.bin -Binary -offset 0x1F000 "
                                   "-o %(ci_build_root_dir)s/spe/bin/rom.bin -Binary;"
                                   "fi;"
                                   "curl --fail --no-progress-meter --connect-timeout 10 --retry 6 -LS -o fiptool https://downloads.trustedfirmware.org/tf-m/rse/tc/fiptool;"
                                   "chmod 755 fiptool;"
                                   "curl --fail --no-progress-meter --connect-timeout 10 --retry 6 -LS -o fip.bin https://downloads.trustedfirmware.org/tf-m/rse/tc/fip.bin;"
                                   "./fiptool update "
                                   "--align 8192 --rss-bl2 %(ci_build_root_dir)s/spe/bin/bl2_signed.bin "
                                   "--align 8192 --rss-s %(ci_build_root_dir)s/spe/bin/tfm_s_encrypted.bin "
                                   "--align 8192 --rss-ns %(ci_build_root_dir)s/nspe/bin/tfm_ns_encrypted.bin "
                                   "--align 8192 --rss-sic-tables-s %(ci_build_root_dir)s/spe/bin/tfm_s_sic_tables_signed.bin "
                                   "--align 8192 --rss-sic-tables-ns %(ci_build_root_dir)s/nspe/bin/tfm_ns_sic_tables_signed.bin "
                                   "--out %(ci_build_root_dir)s/spe/bin/host_flash.bin "
                                   "fip.bin"),
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
                   "stm/stm32h573i_dk": ("echo 'STM32H573I-DK board post process';"
                                          "%(ci_build_root_dir)s/spe/api_ns/postbuild.sh;"
                                          "pushd %(ci_build_root_dir)s/spe/api_ns;"
                                          "mkdir -p image_signing/scripts ;"
                                          "cp %(ci_build_root_dir)s/nspe/bin/tfm_ns_signed.bin image_signing/scripts ;"
                                          "tar jcf ./bin/stm32h573i_dk-tfm.tar.bz2 regression.sh TFM_UPDATE.sh "
                                          "bin/bl2.bin "
                                          "bin/tfm_s_signed.bin "
                                          "image_signing/scripts/tfm_ns_signed.bin ;"
                                          "popd"),
                   "nxp/lpcxpresso55s69": ("echo 'LPCXpresso55S69 bo.ard post process\n';"
                                           "mkdir -p %(codebase_root_dir)s/build/bin ;"
                                           # Workaround for flash_JLink.py
                                           "cp %(ci_build_root_dir)s/spe/bin/tfm_s.hex %(codebase_root_dir)s/build/bin ;"
                                           "cp %(ci_build_root_dir)s/nspe/bin/tfm_ns.hex %(codebase_root_dir)s/build/bin ;"
                                           "cd %(codebase_root_dir)s/build/bin; "
                                           "rm -f flash.jlink; "
                                           "if [ -f \"%(ci_build_root_dir)s/spe/bin/bl2.hex\" ]; then "
                                           "echo r >> flash.jlink; "
                                           "echo erase >> flash.jlink; "
                                           "echo loadfile bl2.hex >> flash.jlink; "
                                           "echo loadfile tfm_s_ns_signed.bin -0x8000 >> flash.jlink; "
                                           "echo r >> flash.jlink; "
                                           "echo go >> flash.jlink; "
                                           "echo exit >> flash.jlink; "
                                           "else "
                                           "echo r >> flash.jlink; "
                                           "echo erase >> flash.jlink; "
                                           "echo loadfile tfm_s.hex >> flash.jlink; "
                                           "echo loadfile tfm_ns.hex >> flash.jlink; "
                                           "echo r >> flash.jlink; "
                                           "echo go >> flash.jlink; "
                                           "echo exit >> flash.jlink; "
                                           "fi;"
                                           "BIN_FILES=$(grep loadfile flash.jlink | awk '{print $2}');"
                                           "tar jcf lpcxpresso55s69-tfm.tar.bz2 flash.jlink ${BIN_FILES};"
                                           "mv lpcxpresso55s69-tfm.tar.bz2 %(ci_build_root_dir)s/nspe/bin ;"
                                           "BIN_FILES=$(grep loadfile flash.jlink | awk '{print $2}');"),
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
                           "tfm_sign.bin"],
                           "arm/rse/tc/tc2": [
                           "%(ci_build_root_dir)s/spe/bin/rom.bin",
                           "%(ci_build_root_dir)s/spe/bin/encrypted_cm_provisioning_bundle_0.bin",
                           "%(ci_build_root_dir)s/spe/bin/encrypted_dm_provisioning_bundle_0.bin",
                           "%(ci_build_root_dir)s/spe/bin/host_flash.bin"]
                           }
}

# List of all build configs that are impossible under all circumstances
_common_tfm_invalid_configs = [
    # LR_CODE size exceeds limit on MUSCA_B1 & MUSCA_S1 with regression tests in Debug mode built with ARMCLANG
    ("arm/musca_b1", "ARMCLANG_6_21", "*", "RegBL2, RegS, RegNS", "OFF", "Debug", "*", "", "*"),
    ("arm/musca_s1", "ARMCLANG_6_21", "*", "RegBL2, RegS, RegNS", "OFF", "Debug", "*", "", "*"),
    # Load range overlap on Musca for IPC Debug type: T895
    ("arm/musca_b1", "ARMCLANG_6_21", "*", "*", "IPC", "Debug", "*", "*", "*"),
    ("arm/musca_s1", "ARMCLANG_6_21", "*", "*", "IPC", "Debug", "*", "*", "*"),
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
                "compiler":         ["ARMCLANG_6_21"],
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
                    ("arm/mps2/an519", "ARMCLANG_6_21", "2",
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
                    ("arm/mps2/an521", "ARMCLANG_6_21", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "profile_small", "PSOFF"),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_21", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2_IPC
                    ("arm/mps2/an521", "ARMCLANG_6_21", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", "IPC"),
                    # AN521_ARMCLANG_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_21", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # AN521_ARMCLANG_3_RegBL2_RegS_RegNS_Minsizerel_BL2
                    ("arm/mps2/an521", "ARMCLANG_6_21", "3",
                     "RegBL2, RegS, RegNS", "OFF", "Minsizerel", True, "", ""),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2_SMALL_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_21", "1",
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
                    ("arm/mps2/an521", "ARMCLANG_6_21", "2",
                     "OFF", "STORAGE", "Debug", True, "", ""),
                    # CS300_FVP_GNUARM_2_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps3/corstone300/fvp", "GCC_10_3", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # CS300_FVP_GNUARM_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/mps3/corstone300/fvp", "GCC_10_3", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "", ""),
                    # CS310_FVP_GCC_1_Debug_BL2_PACBTI_STD
                    ("arm/mps3/corstone310/fvp", "GCC_13_2", "1",
                     "OFF", "OFF", "Debug", True, "", "PACBTI_STD"),
                    # corstone1000_GCC_2_RegS_Debug_BL2_NSOFF_CS1K_TEST_FVP
                    ("arm/corstone1000", "GCC_10_3", "2",
                     "RegS", "OFF", "Debug", True, "", "NSOFF, CS1K_TEST, FVP"),
                    # corstone315_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2
                    ("arm/mps4/corstone315", "ARMCLANG_6_21", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # MUSCA_B1_GCC_1_RegBL2_RegS_RegNS_Minsizerel_BL2
                    ("arm/musca_b1", "GCC_10_3", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Minsizerel", True, "", ""),
                    # MUSCA_S1_ARMCLANG_2_RegBL2_RegS_RegNS_Release_BL2
                    ("arm/musca_s1", "ARMCLANG_6_21", "2",
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
                    # RSE_TC2_GCC_2_RegS_RegNS_Debug_BL2
                    ("arm/rse/tc/tc2", "GCC_10_3", "2",
                     "RegS, RegNS", "OFF", "Debug", True, "", ""),
                    # RSE_TC_GCC_2_RegBL1_1_RegBL1_2_Debug_BL2
                    ("arm/rse/tc/tc2", "GCC_10_3", "2",
                     "RegBL1_1", "OFF", "Debug", True, "", ""),
                    # RSE_RDFremont_GCC_2_Release_BL2_NSOFF_CFG0
                    ("arm/rse/rdfremont", "GCC_10_3", "2",
                     "OFF", "OFF", "Release", True, "", "NSOFF, CFG0"),
                    # RSE_RD1AE_GCC_2_Release_BL2_NSOFF
                    ("arm/rse/automotive_rd/rd1ae", "GCC_10_3", "2",
                     "OFF", "OFF", "Release", True, "", "NSOFF"),
                    # stm32l562e_dk_ARMCLANG_1_RegS_RegNS_Release_BL2_CRYPTO_OFF
                    ("stm/stm32l562e_dk", "ARMCLANG_6_21", "1",
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
                    ("stm/b_u585i_iot02a", "ARMCLANG_6_21", "2",
                     "RegS, RegNS", "OFF", "Release", True, "", ""),
                    # stm32h573i_dk_GCC_1_RegS_RegNS_Release_BL2
                    ("stm/stm32h573i_dk", "GCC_10_3", "1",
                     "RegS, RegNS", "OFF", "Release", True, "", ""),
                    # stm32h573i_dk_ARMCLANG_2_RegS_RegNS_Release_BL2
                    ("stm/stm32h573i_dk", "ARMCLANG_6_21", "2",
                     "RegS, RegNS", "OFF", "Release", True, "", ""),
                    # psoc64_GCC_2_RegS_RegNS_Release
                    ("cypress/psoc64", "GCC_10_3", "2",
                     "RegS, RegNS", "OFF", "Release", False, "", ""),
                ],
                "invalid": _common_tfm_invalid_configs + []
                }

config_pp_test_debug = {"seed_params": {
                # AN519_ARMCLANG_IPC_1_RegBL2_RegS_RegNS_Debug_BL2
                "tfm_platform":     ["arm/mps2/an519"],
                "compiler":         ["ARMCLANG_6_21"],
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
                    ("arm/mps2/an519", "ARMCLANG_6_21", "2",
                     "RegBL2, RegS, RegNS", "OFF", "Release", True, "",  ""),
                    # AN521_ARMCLANG_1_RegBL2_RegS_RegNS_Debug_BL2_SMALL_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_21", "1",
                     "RegBL2, RegS, RegNS", "OFF", "Debug", True, "profile_small", "PSOFF"),
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "extra_params":     ["EXTRAS_EXAMPLE_VAD"]
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
                "profile":          ["profile_medium"],
                "extra_params":     ["EXTRAS_EXAMPLE_DMA350_CLCD"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_example_dma350_s = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["RegS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["EXTRAS_EXAMPLE_DMA350_S"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_example_dma350_ns = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1"],
                "test_regression":  ["RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["EXTRAS_EXAMPLE_DMA350_NS"]
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
                "profile":          ["profile_medium"],
                "extra_params":     ["EXTRAS_EXAMPLE_DMA350_TRIGGER"]
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
                "profile":          ["profile_medium_arotless"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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

config_corstone310_pacbti = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone310/fvp"],
                "compiler":         ["GCC_13_2"],
                "isolation_level":  ["1"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["PACBTI_STD"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_corstone315 = {"seed_params": {
                "tfm_platform":     ["arm/mps4/corstone315"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
                "isolation_level":  ["1"],
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

config_rse = {"seed_params": {
                "tfm_platform":     ["arm/rse/tc/tc2"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF", "RegS, RegNS"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    # BL2 is too large for RSE in Debug builds with tests
                    ("arm/rse/tc/tc2", "GCC_10_3", "*", "RegBL2, RegS, RegNS", "*",
                     "Debug", True, "*", "*"),
                ]
                }

config_rse_rdfremont = {"seed_params": {
                "tfm_platform":     ["arm/rse/rdfremont"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF, CFG0"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_rse_rd1ae = {"seed_params": {
                "tfm_platform":     ["arm/rse/automotive_rd/rd1ae"],
                "compiler":         ["GCC_10_3"],
                "isolation_level":  ["1", "2"],
                "test_regression":  ["OFF"],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_bl2":         [True],
                "profile":          [""],
                "extra_params":     ["NSOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_psoc64 = {"seed_params": {
                "tfm_platform":     ["cypress/psoc64"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "isolation_level":  ["1", "2"],
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                    ("stm/stm32l562e_dk", "ARMCLANG_6_21", "1",
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
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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

config_stm32h573i_dk = {"seed_params": {
                "tfm_platform":     ["stm/stm32h573i_dk"],
                "compiler":         ["GCC_10_3", "ARMCLANG_6_21"],
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
                "compiler":         ["ARMCLANG_6_21"],
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
                    ("arm/mps2/an521", "ARMCLANG_6_21", "1",
                     "OFF", "OFF", "Minsizerel", True, "profile_small", "PSOFF"),
                    # AN521_ARMCLANG_2_Minsizerel_BL2_MEDIUM_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_21", "2",
                     "OFF", "OFF", "Minsizerel", True, "profile_medium", "PSOFF"),
                    # AN521_ARMCLANG_3_Minsizerel_BL2_LARGE_PSOFF
                    ("arm/mps2/an521", "ARMCLANG_6_21", "3",
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
                "compiler":         ["ARMCLANG_6_21"],
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
                    # per-patch test group
                    "pp_test": config_pp_test,
                    "pp_test_debug": config_pp_test_debug,

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
                    "nightly_corstone310_pacbti" : config_corstone310_pacbti,
                    "nightly_corstone315": config_corstone315,
                    "nightly_corstone1000": config_corstone1000,
                    "nightly_rse": config_rse,
                    "nightly_rse_rdfremont": config_rse_rdfremont,
                    "nightly_rse_rd1ae": config_rse_rd1ae,
                    "nightly_psoc64": config_psoc64,
                    "nightly_stm32l562e_dk": config_stm32l562e_dk,
                    "nightly_b_u585i_iot02a": config_b_u585i_iot02a,
                    "nightly_stm32h573i_dk": config_stm32h573i_dk,
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
                    "release_corstone315": config_corstone315,
                    "release_rse": config_rse,
                    "release_rse_rdfremont": config_rse_rdfremont,
                    "release_rse_rd1ae": config_rse_rd1ae,
                    "release_psoc64": config_psoc64,
                    "release_stm32l562e_dk": config_stm32l562e_dk,
                    "release_b_u585i_iot02a": config_b_u585i_iot02a,
                    "release_stm32h573i_dk": config_stm32h573i_dk,
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
                    "corstone315": config_corstone315,
                    "rse": config_rse,
                    "rse_rdfremont": config_rse_rdfremont,
                    "rse_rd1ae": config_rse_rd1ae,
                    "cypress_psoc64": config_psoc64,
                    "corstone1000": config_corstone1000,
                    "stm_stm32l562e_dk": config_stm32l562e_dk,
                    "stm_b_u585i_iot02a": config_b_u585i_iot02a,
                    "stm_stm32h573i_dk": config_stm32h573i_dk,
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
