#!/usr/bin/env python3

""" builtin_configs.py:

    Default configuration files used as reference """

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
                   "toolchain_file",
                   "lib_model",
                   "isolation_level",
                   "test_regression",
                   "test_psa_api",
                   "cmake_build_type",
                   "with_otp",
                   "with_bl2",
                   "with_ns",
                   "profile",
                   "partition_ps",
                   "extra_params"],

    # Keys for the templace will come from the combinations of parameters
    # provided in the seed dictionary.

    "config_template": "cmake -G Ninja " + \
        "-DTFM_PLATFORM=%(tfm_platform)s " + \
        "-DTFM_TOOLCHAIN_FILE=%(codebase_root_dir)s/%(toolchain_file)s " + \
        "-DTFM_LIB_MODEL=%(lib_model)s " + \
        "-DTFM_ISOLATION_LEVEL=%(isolation_level)s " + \
        "-DTEST_NS=%(test_regression)s -DTEST_S=%(test_regression)s " + \
        "-DTEST_BL2=%(test_regression)s " + \
        "-DTEST_PSA_API=%(test_psa_api)s " + \
        "-DCMAKE_BUILD_TYPE=%(cmake_build_type)s " + \
        "-DCRYPTO_HW_ACCELERATOR_OTP_STATE=%(with_otp)s " + \
        "-DBL2=%(with_bl2)s " + \
        "-DNS=%(with_ns)s " + \
        "-DTFM_TEST_REPO_PATH=%(codebase_root_dir)s/../tf-m-tests " + \
        "-DMBEDCRYPTO_PATH=%(codebase_root_dir)s/../mbedtls " + \
        "-DPSA_ARCH_TESTS_PATH=%(codebase_root_dir)s/../psa-arch-tests " + \
        "-DMCUBOOT_PATH=%(codebase_root_dir)s/../mcuboot " + \
        "-DTFM_PROFILE=%(profile)s " + \
        "-DTFM_PARTITION_PROTECTED_STORAGE=%(partition_ps)s " + \
        "%(extra_params)s " + \
        "%(codebase_root_dir)s",

    # A small subset of  string substitution params is allowed in commands.
    # tfm_build_manager will replace %(_tbm_build_dir_)s,  %(_tbm_code_dir_)s,
    # _tbm_target_platform_ with the  paths set when building

    "artifact_capture_rex": (r'%(_tbm_build_dir_)s/bin'
                             r'/(\w+\.(?:axf|bin|hex))$'),

    # ALL commands will be executed for every build.
    # Other keys will append extra commands when matching target_platform
    "build_cmds": {"all": ["cmake --build ./ -- install"],
                   "arm/musca_b1/sse_200": [("srec_cat "
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
                   "nxp/lpcxpresso55s69": [("echo 'LPCXpresso55S69 board post process\n';"
                                            "if [ -f \"%(_tbm_build_dir_)s/bin/bl2.hex\" ]; then FLASH_FILE='flash_bl2_JLink.py'; else FLASH_FILE='flash_JLink.py'; fi;"
                                            "pushd %(_tbm_build_dir_)s/../platform/ext/target/nxp/lpcxpresso55s69/scripts;"
                                            "LN=$(grep -n 'JLinkExe' ${FLASH_FILE}|awk -F: '{print $1}');"
                                            "sed -i \"${LN}s/.*/    print('flash.jlink generated')/\" ${FLASH_FILE};"
                                            "python3 ./${FLASH_FILE};"
                                            "cd %(_tbm_build_dir_)s/bin;"
                                            "BIN_FILES=$(grep loadfile flash.jlink | awk '{print $2}');"
                                            "tar jcf lpcxpresso55s69-tfm.tar.bz2 flash.jlink ${BIN_FILES};"
                                            "popd")]
                   },

    # (Optional) If set will fail if those artefacts are missing post build
    "required_artefacts": {"all": [
                           "%(_tbm_build_dir_)s/bin/"
                           "tfm_s.bin",
                           "%(_tbm_build_dir_)s/bin/"
                           "tfm_ns.bin"],
                           "arm/musca_b1/sse_200": [
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
    ("arm/musca_b1/sse_200", "toolchain_ARMCLANG.cmake", "*", "*", True, "OFF", "Debug", "*", "*", "*", "", "*", "*"),
    ("arm/musca_s1", "toolchain_ARMCLANG.cmake", "*", "*", True, "OFF", "Debug", "*", "*", "*", "", "*", "*"),
    # Load range overlap on Musca for IPC Debug type: T895
    ("arm/musca_b1/sse_200", "toolchain_ARMCLANG.cmake", "*", "*", "*", "IPC", "Debug", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_s1", "toolchain_ARMCLANG.cmake", "*", "*", "*", "IPC", "Debug", "*", "*", "*", "*", "*", "*"),
    # Oversize issue on config lpcxpresso55s69_GNUARM_IPC_2_Relwithdebinfo_BL2_NS_MEDIUM
    ("nxp/lpcxpresso55s69", "toolchain_GNUARM.cmake", False, "2", False, "OFF",
     "Relwithdebinfo", "off", True, True, "profile_medium", "ON", "*"),
    # Oversize issue on config stm32l562e_dk_ARMCLANG_LIB_1_REG_Release_BL2_NS
    ("stm/stm32l562e_dk", "toolchain_ARMCLANG.cmake", True, "1", True, "OFF",
     "Release", "off", True, True, "", "ON", "*"),
    # LVL2 and LVL3 requires IPC model
    ("*", "*", True, "2", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    ("*", "*", True, "3", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    # Regression requires NS
    ("*", "*", "*", "*", True, "*", "*", "*", "*", False, "*", "*", "*"),
    # psoc64 requires IPC model
    ("cypress/psoc64", "*", True, "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    # No PSA_ACK with regression
    ("*", "*", "*", "*", True, "IPC", "*", "*", "*", "*", "*", "*", "*"),
    ("*", "*", "*", "*", True, "CRYPTO", "*", "*", "*", "*", "*", "*", "*"),
    ("*", "*", "*", "*", True, "INITIAL_ATTESTATION", "*", "*", "*", "*", "*", "*", "*"),
    ("*", "*", "*", "*", True, "STORAGE", "*", "*", "*", "*", "*", "*", "*"),
    # PSA_ACK requires NS
    ("*", "*", "*", "*", "*", "IPC", "*", "*", "*", False, "*", "*", "*"),
    ("*", "*", "*", "*", "*", "CRYPTO", "*", "*", "*", False, "*", "*", "*"),
    ("*", "*", "*", "*", "*", "INITIAL_ATTESTATION", "*", "*", "*", False, "*", "*", "*"),
    ("*", "*", "*", "*", "*", "STORAGE", "*", "*", "*", False, "*", "*", "*"),
    # PSA_ACK IPC (FF) does not support LVL3
    ("*", "*", "*", "3", "*", "IPC", "*", "*", "*", "*", "*", "*", "*"),
    # Musca requires BL2
    ("arm/musca_b1/sse_200", "*", "*", "*", "*", "*", "*", "*", False, "*", "*", "*", "*"),
    ("arm/musca_s1", "*", "*", "*", "*", "*", "*", "*", False, "*", "*", "*", "*"),
    # psoc64 cannot use BL2
    ("cypress/psoc64", "*", "*", "*", "*", "*", "*", "*", True, "*", "*", "*", "*"),
    # psoc64 does not support Debug build type
    ("cypress/psoc64", "*", "*", "*", "*", "*", "Debug", "*", "*", "*", "*", "*", "*"),
    # Musca b1 SSE 200 does not support Profile S
    ("arm/musca_b1/sse_200", "*", "*", "*", "*", "*", "*", "*", "*", "*", "profile_small", "*", "*"),
    # Musca B1 Secure Enclave requires IPC model, BL2, and supports only Isolation Level 1
    ("arm/musca_b1/secure_enclave", "*", True, "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "*", "*", "*", False, "*", "*", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "2", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    # Musca B1 Secure Enclave does not support tests, profiles, NS side building
    ("arm/musca_b1/secure_enclave", "*", "*", "*", True, "*", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "IPC", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "CRYPTO", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "INITIAL_ATTESTATION", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "STORAGE", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "*", "*", "*", "*", "*", "profile_small", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "*", "*", "*", "*", "*", "profile_medium", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "*", "*", "*", "*", "*", "profile_large", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "*", "*", "*", "*", "*", "*", True, "*", "*", "*"),
    # PARTITION_PS could be OFF only for Profile S and M
    ("*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "", "OFF", "*"),
    ("*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "profile_large", "OFF", "*"),
    # PARTITION_PS should be OFF for Profile S
    ("*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "profile_small", "ON", "*"),
    # Proile M only support for IPC model
    ("*", "*", True, "*", "*", "*", "*", "*", "*", "*", "profile_medium", "*", "*"),
    # Profile M only support for Isolation Level 2
    ("*", "*", "*", "1", "*", "*", "*", "*", "*", "*", "profile_medium", "*", "*"),
    ("*", "*", "*", "3", "*", "*", "*", "*", "*", "*", "profile_medium", "*", "*"),
    # Profile L only support for Isolation Level 3
    ("*", "*", "*", "1", "*", "*", "*", "*", "*", "*", "profile_large", "*", "*"),
    ("*", "*", "*", "2", "*", "*", "*", "*", "*", "*", "profile_large", "*", "*"),
    # Profile S does not support IPC model
    ("*", "*", False, "*", "*", "*", "*", "*", "*", "*", "profile_small", "*", "*"),
    # Profile S only supports Isolation Level 1
    ("*", "*", "*", "2", "*", "*", "*", "*", "*", "*", "profile_small", "*", "*"),
    ("*", "*", "*", "3", "*", "*", "*", "*", "*", "*", "profile_small", "*", "*"),
    # Only AN521 and MUSCA_B1 support Isolation Level 3
    ("arm/mps2/an519", "*", "*", "3", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/mps3/an524", "*", "*", "3", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_s1", "*", "*", "3", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    ("cypress/psoc64", "*", "*", "3", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    ("arm/musca_b1/secure_enclave", "*", "*", "3", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    # stm/stm32l562e_dk uses BL2
    ("stm/stm32l562e_dk", "*", "*", "*", "*", "*", "*", "*", False, "*", "*", "*", "*"),
    # stm/stm32l562e_dk does not support Debug build type
    ("stm/stm32l562e_dk", "*", "*", "*", "*", "*", "Debug", "*", "*", "*", "*", "*", "*"),
    # nxp/lpcxpresso55s69 only build with GCC
    ("nxp/lpcxpresso55s69", "toolchain_ARMCLANG.cmake", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"),
    # nxp/lpcxpresso55s69 only build Profile M
    ("nxp/lpcxpresso55s69", "*", "*", "*", "*", "*", "*", "*", "*", "*", "profile_small", "*", "*"),
    ("nxp/lpcxpresso55s69", "*", "*", "*", "*", "*", "*", "*", "*", "*", "profile_large", "*", "*"),
    # nxp/lpcxpresso55s69 have to turn off BL2 when build regression test
    ("nxp/lpcxpresso55s69", "*", "*", "*", True, "*", "*", "*", True, "*", "*", "*", "*"),
    # nxp/lpcxpresso55s69 turn off BL2 temporary, due to the oversize error
    ("nxp/lpcxpresso55s69", "*", "*", "*", "*", "*", "*", "*", True, "*", "*", "*", "*")
    ]

# Configure build manager to build several combinations
config_AN524 = {"seed_params": {
                "tfm_platform":     ["arm/mps3/an524"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True, False],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_AN521 = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True, False],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_PSA_API = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/musca_b1/sse_200",
                                     "arm/musca_s1"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [False],
                "test_psa_api":     ["CRYPTO",
                                     "INITIAL_ATTESTATION",
                                     "STORAGE"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_PSA_FF = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/musca_b1/sse_200",
                                     "arm/musca_s1"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [False],
                "test_psa_api":     ["IPC"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_PSA_API_OTP = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [False],
                "test_psa_api":     ["CRYPTO",
                                     "INITIAL_ATTESTATION",
                                     "STORAGE"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["ENABLED"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_PSA_FF_OTP = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [False],
                "test_psa_api":     ["IPC"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["ENABLED"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_PSOC64 = {"seed_params": {
                "tfm_platform":     ["cypress/psoc64"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [False],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_STM32L562E_DK = {"seed_params": {
                "tfm_platform":     ["stm/stm32l562e_dk"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     ["CRYPTO_OFF", "CRYPTO_ON"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    # all other tests are off when CRYPTO is ON
                    ("stm/stm32l562e_dk", "*", "*", "*", True, "*", "*", "*",
                     "*", "*", "*", "*", "CRYPTO_ON"),
                    # all other tests are ON when CRYPTO is OFF
                    ("stm/stm32l562e_dk", "*", "*", "*", False, "*", "*", "*",
                     "*", "*", "*", "*", "CRYPTO_OFF"),
                ]
                }

config_LPCXPRESSO55S69 = {"seed_params": {
                "tfm_platform":     ["nxp/lpcxpresso55s69"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["2"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Relwithdebinfo"],
                "with_otp":         ["off"],
                "with_bl2":         [False],
                "with_ns":          [True],
                "profile":          ["profile_medium"],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_FP = {"seed_params": {
                "tfm_platform":     ["arm/musca_s1"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     ["FPSOFT", "FPHARD", "FPHARD_LOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_corstone1000 = {"seed_params": {
                "tfm_platform":     ["arm/corstone1000"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     ["FVP", "FPGA"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_AN519 = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True, False],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_IPC =  {"seed_params": {
               "tfm_platform":     ["arm/mps2/an521", "arm/mps2/an519",
                                    "arm/musca_b1/sse_200"],
               "toolchain_file":   ["toolchain_GNUARM.cmake",
                                    "toolchain_ARMCLANG.cmake"],
               "lib_model":        [False],
               "isolation_level":  ["1", "2"],
               "test_regression":  [True, False],
               "test_psa_api":     ["OFF"],
               "cmake_build_type": ["Debug", "Release"],
               "with_otp":         ["off"],
               "with_bl2":         [True, False],
               "with_ns":          [True, False],
               "profile":          [""],
               "partition_ps":     ["ON"],
               "extra_params":     [""]
               },
              "common_params": _common_tfm_builder_cfg,
              "invalid": _common_tfm_invalid_configs + []
              }

config_full = {"seed_params": {
               "tfm_platform":     ["arm/mps2/an521", "arm/mps2/an519",
                                    "arm/musca_b1/sse_200",
                                    "arm/mps3/an524", "cypress/psoc64",
                                    "arm/musca_b1/secure_enclave",
                                    "stm/stm32l562e_dk",
                                    "nxp/lpcxpresso55s69"],
               "toolchain_file":   ["toolchain_GNUARM.cmake",
                                    "toolchain_ARMCLANG.cmake"],
               "lib_model":        [True, False],
               "isolation_level":  ["1", "2"],
               "test_regression":  [True, False],
               "test_psa_api":     ["OFF"],
               "cmake_build_type": ["Debug", "Release", "RelWithDebInfo"],
               "with_otp":         ["off"],
               "with_bl2":         [True, False],
               "with_ns":          [True, False],
               "profile":          [""],
               "partition_ps":     ["ON"],
               "extra_params":     [""]
               },
               "common_params": _common_tfm_builder_cfg,
               "invalid": _common_tfm_invalid_configs + [
                   ("cypress/psoc64", "*", "*", "*", "*", "*", "Debug", "*",
                    "*", "*", "*", "*", "*"),
                   ("cypress/psoc64", "*", "*", "*", "*", "*", "*", "*", True,
                    True, "*", "*", "*"),
                   ("arm/mps2/an521", "*", "*", "*", "*", "*", "RelWithDebInfo",
                    "*", "*", "*", "*", "*", "*"),
                   ("arm/mps2/an519", "*", "*", "*", "*", "*", "RelWithDebInfo",
                    "*", "*", "*", "*", "*", "*"),
                   ("arm/musca_b1/sse_200", "*", "*", "*", "*", "*", "RelWithDebInfo",
                    "*", "*", "*", "*", "*", "*"),
                   ("arm/mps3/an524", "*", "*", "*", "*", "*", "RelWithDebInfo",
                    "*", "*", "*", "*", "*", "*"),
               ]
               }

config_tfm_test = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521",
                                     "arm/musca_b1/sse_200", "arm/musca_s1"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_tfm_test2 = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519", "arm/mps3/an524"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "toolchain_GNUARM.cmake", "*", "*", "*",
                     "*", "Minsizerel", "*", "*", "*", "*", "*", "*"),
                ]
                }

config_tfm_profile = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519", "arm/mps2/an521",
                                     "arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          ["profile_small", "profile_medium", "profile_large"],
                "partition_ps":     ["ON", "OFF"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "toolchain_GNUARM.cmake", "*", "*", "*",
                     "*", "Minsizerel", "*", "*", "*", "*", "*", "*"),
                    # Profile Large is only supported by AN521
                    ("arm/mps2/an519", "*", "*", "*", "*", "*", "*", "*", "*",
                     "*", "profile_large", "*", "*"),
                    ("arm/musca_b1/sse_200", "*", "*", "*", "*", "*", "*", "*",
                     "*", "*", "profile_large", "*", "*"),
                ]
                }

config_tfm_test_OTP = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["ENABLED"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_MUSCA_B1 = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_MUSCA_B1_SE = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1/secure_enclave"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_MUSCA_S1 = {"seed_params": {
                "tfm_platform":     ["arm/musca_s1"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_release = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/mps2/an519",
                                     "arm/musca_b1/sse_200", "arm/musca_s1",
                                     "arm/mps3/an524"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True, False],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "toolchain_GNUARM.cmake", "*", "*", "*",
                     "*", "Minsizerel", "*", "*", "*", "*", "*", "*"),
                ]
                }

# Configure build manager to build several combinations
config_AN521_PSA_API = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/mps2/an519",
                                     "arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [False],
                "test_psa_api":     ["IPC",
                                     "CRYPTO",
                                     "INITIAL_ATTESTATION",
                                     "STORAGE"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "toolchain_GNUARM.cmake", "*", "*", "*",
                     "*", "Minsizerel", "*", "*", "*", "*", "*", "*"),
                ]
                }

config_AN521_PSA_IPC = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/mps2/an519",
                                     "arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [False],
                "test_psa_api":     ["IPC"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["ENABLED"],
                "with_bl2":         [True],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "toolchain_GNUARM.cmake", "*", "*", "*",
                     "*", "Minsizerel", "*", "*", "*", "*", "*", "*"),
                ]
                }

config_nightly = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an521", "arm/mps2/an519",
                                     "arm/musca_b1/sse_200", "arm/musca_s1",
                                     "arm/mps3/an524", "arm/musca_b1/secure_enclave"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel", "RelWithDebInfo"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "valid": [
                    # MUSCA_B1_GNUARM_IPC_1_REG_Release_BL2_NS_CC_DRIVER_PSA
                    ("arm/musca_b1/sse_200", "toolchain_GNUARM.cmake",
                     False, "1", True, "OFF", "Release",
                     "off", True, True, "", "ON", "CC_DRIVER_PSA"),
                    # MUSCA_S1_GNUARM_IPC_1_REG_Release_BL2_NS_CC_DRIVER_PSA
                    ("arm/musca_s1", "toolchain_GNUARM.cmake",
                     False, "1", True, "OFF", "Release",
                     "off", True, True, "", "ON", "CC_DRIVER_PSA"),
                ],
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "toolchain_GNUARM.cmake", "*", "*", "*",
                     "*", "Minsizerel", "*", "*", "*", "*", "*", "*"),
                    ("cypress/psoc64", "*", "*", "*", "*", "*", "Debug", "*",
                     "*", "*", "*", "*", "*"),
                    ("cypress/psoc64", "*", "*", "*", "*", "*", "*", "*", True,
                     True, "*", "*", "*"),
                    ("arm/mps2/an521", "*", "*", "*", "*", "*", "RelWithDebInfo",
                     "*", "*", "*", "*", "*", "*"),
                    ("arm/mps2/an519", "*", "*", "*", "*", "*", "RelWithDebInfo",
                     "*", "*", "*", "*", "*", "*"),
                    ("arm/musca_b1/sse_200", "*", "*", "*", "*", "*",
                     "RelWithDebInfo", "*", "*", "*", "*", "*", "*"),
                    ("arm/musca_s1", "*", "*", "*", "*", "*", "RelWithDebInfo",
                     "*", "*", "*", "*", "*", "*"),
                    ("arm/mps3/an524", "*", "*", "*", "*", "*", "RelWithDebInfo",
                     "*", "*", "*", "*", "*", "*"),
                ]
                }

config_nsce = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an521"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     ["NSCE"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_mmio = {"seed_params": {
               "tfm_platform":      ["arm/mps2/an521"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     ["MMIO"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nightly_profile = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519", "arm/mps2/an521",
                                     "arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          ["profile_small", "profile_medium", "profile_large"],
                "partition_ps":     ["ON", "OFF"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an519", "toolchain_GNUARM.cmake", "*", "*", "*",
                     "*", "Minsizerel", "*", "*", "*", "*", "*", "*"),
                    # Profile Large is only supported by AN521
                    ("arm/mps2/an519", "*", "*", "*", "*", "*", "*", "*", "*",
                     "*", "profile_large", "*", "*"),
                    ("arm/musca_b1/sse_200", "*", "*", "*", "*", "*", "*", "*",
                     "*", "*", "profile_large", "*", "*"),
                ]
                }

config_nightly_PSA_API = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/musca_b1/sse_200",
                                     "arm/musca_s1"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [False],
                "test_psa_api":     ["CRYPTO",
                                     "INITIAL_ATTESTATION",
                                     "STORAGE"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nightly_PSA_FF = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/musca_b1/sse_200",
                                     "arm/musca_s1"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [False],
                "test_psa_api":     ["IPC"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nightly_OTP = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["ENABLED"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nightly_psoc64 = {"seed_params": {
                "tfm_platform":     ["cypress/psoc64"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [False],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nightly_LPCXPRESSO55S69 = {"seed_params": {
                "tfm_platform":     ["nxp/lpcxpresso55s69"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["2"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Relwithdebinfo"],
                "with_otp":         ["off"],
                "with_bl2":         [False],
                "with_ns":          [True],
                "profile":          ["profile_medium"],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nightly_FP = {"seed_params": {
                "tfm_platform":     ["arm/musca_s1"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     ["FPSOFT", "FPHARD", "FPHARD_LOFF"]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_pp_test = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/mps2/an519",
                                     "arm/musca_s1"],
                "toolchain_file":   ["toolchain_GNUARM.cmake",
                                     "toolchain_ARMCLANG.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True, False],
                "profile":          ["", "profile_small", "profile_medium"],
                "partition_ps":     ["ON", "OFF"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "valid": [
                    ("arm/mps2/an521", "toolchain_GNUARM.cmake",
                     True, "1", False, "OFF", "Debug",
                     "off", True, True, "", "ON", ""),
                    ("arm/mps2/an521", "toolchain_ARMCLANG.cmake",
                     False, "2", False, "OFF", "Debug",
                     "off", True, True, "", "ON", ""),
                    ("arm/mps2/an521", "toolchain_ARMCLANG.cmake",
                     False, "3", False, "OFF", "Release",
                     "off", True, True, "", "ON", ""),
                    ("arm/mps2/an521", "toolchain_GNUARM.cmake",
                     False, "2", False, "OFF", "Debug",
                     "off", True, True, "profile_medium", "ON", ""),
                    ("arm/mps2/an521", "toolchain_GNUARM.cmake",
                     False, "3", False, "OFF", "Debug",
                     "off", True, True, "profile_large", "ON", ""),
                    # AN521_GNUARM_IPC_2_REG_Release_BL2_NS_MEDIUM_PSOFF
                    ("arm/mps2/an521", "toolchain_GNUARM.cmake",
                     False, "2", True, "OFF", "Release",
                     "off", True, True, "profile_medium", "OFF", ""),
                    # MUSCA_B1_GNUARM_LIB_1_REG_Minsizerel_BL2_NS
                    ("arm/musca_b1/sse_200", "toolchain_GNUARM.cmake",
                     True, "1", True, "OFF", "Minsizerel",
                     "off", True, True, "", "ON", ""),
                    # stm32l562e_dk_ARMCLANG_IPC_1_REG_Release_BL2_NS
                    ("stm/stm32l562e_dk", "toolchain_ARMCLANG.cmake",
                     False, "1", True, "OFF", "Release",
                     "off", True, True, "", "ON", "CRYPTO_OFF"),
                    # stm32l562e_dk_GNUARM_IPC_2_REG_Release_BL2_NS
                    ("stm/stm32l562e_dk", "toolchain_GNUARM.cmake",
                     False, "2", False, "OFF", "Release",
                     "off", True, True, "", "ON", "CRYPTO_ON"),
                    # stm32l562e_dk_GNUARM_IPC_3_REG_Release_BL2_NS
                    ("stm/stm32l562e_dk", "toolchain_GNUARM.cmake",
                     False, "3", True, "OFF", "Release",
                     "off", True, True, "", "ON", "CRYPTO_OFF"),
                    # MUSCA_S1_GNUARM_IPC_2_REG_Release_BL2_NS_FPHARD
                    ("arm/musca_s1", "toolchain_GNUARM.cmake",
                     False, "2", True, "OFF", "Release",
                     "off", True, True, "", "ON", "FPHARD"),
                    # MUSCA_S1_GNUARM_IPC_1_REG_Release_BL2_NS_CC_DRIVER_PSA
                    ("arm/musca_s1", "toolchain_GNUARM.cmake",
                     False, "1", True, "OFF", "Release",
                     "off", True, True, "", "ON", "CC_DRIVER_PSA"),
                ],
                "invalid": _common_tfm_invalid_configs + [
                    # invalid configs that are not supported by TF-M
                    ("arm/musca_s1", "*", "*", "*", "*", "*",
                     "*", "*", "*", "*", "profile_medium", "*", "*"),
                    # valid configs supported by TF-M but not needed in per-patch
                    ("*", "*", "*", "1", "*", "*", "Release",
                     "*", "*", "*", "*", "*", "*"),
                    ("*", "*", "*", "1", "*", "*", "Minsizerel",
                     "*", "*", "*", "*", "*", "*"),
                    ("*", "*", "*", "2", "*", "*", "Debug",
                     "*", "*", "*", "*", "*", "*"),
                    ("*", "*", "*", "2", "*", "*", "Minsizerel",
                     "*", "*", "*", "*", "*", "*"),
                    ("*", "*", "*", "3", "*", "*", "Debug",
                     "*", "*", "*", "*", "*", "*"),
                    ("*", "*", "*", "3", "*", "*", "Release",
                     "*", "*", "*", "*", "*", "*"),
                    ("arm/mps2/an519", "*", "*", "*", "*", "*",
                     "*", "*", "*", "*", "profile_small", "*", "*"),
                    ("arm/musca_s1", "*", "*", "*", "*", "*",
                     "*", "*", "*", "*", "profile_small", "*", "*"),
                    ("arm/mps2/an519", "*", "*", "*", "*", "*",
                     "*", "*", "*", "*", "profile_medium", "*", "*"),
                    ("arm/mps2/an521", "*", "*", "*", "*", "*",
                     "*", "*", "*", "*", "profile_medium", "*", "*"),
                    ("*", "toolchain_GNUARM.cmake", "*", "*", "*", "*",
                     "*", "*", "*", "*", "profile_small", "*", "*"),
                    ("*", "toolchain_ARMCLANG.cmake", "*", "*", "*", "*",
                     "*", "*", "*", "*", "profile_medium", "*", "*"),
                    ("*", "toolchain_ARMCLANG.cmake", True, "*", "*", "*",
                     "*", "*", "*", "*", "*", "*", "*"),
                ]
                }

config_pp_OTP = {"seed_params": {
                "tfm_platform":     ["arm/musca_b1/sse_200"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["ENABLED"],
                "with_bl2":         [True],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

# Configure build manager to build several combinations
config_pp_PSA_API = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["2"],
                "test_regression":  [False],
                "test_psa_api":     ["IPC",
                                     "CRYPTO",
                                     "INITIAL_ATTESTATION",
                                     "STORAGE"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_pp_PSoC64 = {"seed_params": {
                "tfm_platform":     ["cypress/psoc64"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["2"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [False],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_cov_an519 = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an519"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          ["", "profile_small", "profile_medium"],
                "partition_ps":     ["ON", "OFF"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_cov_an521 = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2", "3"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          ["", "profile_small", "profile_medium", "profile_large"],
                "partition_ps":     ["ON", "OFF"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

# Configruation used for document building
config_doxygen = {"common_params": {
                  "config_type": "tf-m_documents",
                  "codebase_root_dir": "tf-m",
                  "build_cmds": {"all": ["-DTFM_PLATFORM=arm/mps2/an521 "
                                         "-DTFM_TOOLCHAIN_FILE=%(_tfm_code_dir_)s/toolchain_GNUARM.cmake"
                                         "-DCMAKE_BUILD_TYPE=Debug "
                                         "%(_tbm_code_dir_)s/",
                                         "cmake --build ./ -- docs"]},
                  "artifact_capture_rex": r'%(_tbm_build_dir_)s/docs/'
                                          r'reference_manual/(?:latex|html)'
                                          r'/(\w+\.(?:html|md|pdf))$',
                  },
                  "invalid": _common_tfm_invalid_configs + []
                  }

# Configuration used in testing
config_debug = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake"],
                "lib_model":        [True],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_debug_PSA_API = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake"],
                "lib_model":        [True],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["CRYPTO",
                                     "INITIAL_ATTESTATION",
                                     "STORAGE"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

# Configuration used in CI
config_ci = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521"],
                "toolchain_file":   ["toolchain_ARMCLANG.cmake",
                                     "toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True, False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True, False],
                "with_ns":          [True],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("*", "toolchain_ARMCLANG.cmake", False, "*", "*", "*",
                     "*", "*", "*", "*", "*", "*", "*"),
                    ("*", "toolchain_ARMCLANG.cmake", True, "1", "*", "*",
                     "*", "*", False, "*", "*", "*", "*"),
                ]
                }

config_lava_debug = {"seed_params": {
                "tfm_platform":     ["arm/mps2/an521", "arm/mps2/an519"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [True, False],
                "isolation_level":  ["1", "2"],
                "test_regression":  [True],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True, False],
                "with_ns":          [True, False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + [
                    ("arm/mps2/an521", "toolchain_GNUARM.cmake", False, "2", "*", "*",
                     "*", "*", True, "*", "*", "*", "*")
                ]
                }

config_an547 = {"seed_params": {
                "tfm_platform":     ["arm/mps3/an547"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_corstone_polaris = {"seed_params": {
                "tfm_platform":     ["arm/mps3/corstone_polaris"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_bl5340 = {"seed_params": {
                "tfm_platform":     ["lairdconnectivity/bl5340_dvk_cpuapp"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nrf5340dk = {"seed_params": {
                "tfm_platform":     ["nordic_nrf/nrf5340dk_nrf5340_cpuapp"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nrf9160dk = {"seed_params": {
                "tfm_platform":     ["nordic_nrf/nrf9160dk_nrf9160"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_m2351 = {"seed_params": {
                "tfm_platform":     ["nuvoton/m2351"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_m2354 = {"seed_params": {
                "tfm_platform":     ["nuvoton/m2354"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Debug"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_b_u585i_iot02a = {"seed_params": {
                "tfm_platform":     ["stm/b_u585i_iot02a"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

config_nucleo_l552ze_q = {"seed_params": {
                "tfm_platform":     ["stm/nucleo_l552ze_q"],
                "toolchain_file":   ["toolchain_GNUARM.cmake"],
                "lib_model":        [False],
                "isolation_level":  ["1"],
                "test_regression":  [False],
                "test_psa_api":     ["OFF"],
                "cmake_build_type": ["Release"],
                "with_otp":         ["off"],
                "with_bl2":         [True],
                "with_ns":          [False],
                "profile":          [""],
                "partition_ps":     ["ON"],
                "extra_params":     [""]
                },
                "common_params": _common_tfm_builder_cfg,
                "invalid": _common_tfm_invalid_configs + []
                }

_builtin_configs = {
                    #release test group
                    "tfm_test": config_tfm_test,
                    "tfm_test2": config_tfm_test2,
                    "tfm_profile": config_tfm_profile,
                    "tfm_test_otp": config_tfm_test_OTP,
                    "tfm_nsce": config_nsce,
                    "tfm_mmio": config_mmio,
                    "psa_api": config_PSA_API,
                    "psa_api_otp": config_PSA_API_OTP,
                    "psa_ff": config_PSA_FF,
                    "psa_ff_otp": config_PSA_FF_OTP,
                    "tfm_psoc64": config_PSOC64,
                    "tfm_stm32l562e_dk": config_STM32L562E_DK,
                    "tfm_lpcxpresso55s69": config_LPCXPRESSO55S69,
                    "tfm_fp": config_FP,

                    #nightly test group
                    "nightly_test": config_nightly,
                    "nightly_nsce": config_nsce,
                    "nightly_mmio": config_mmio,
                    "nightly_profile": config_nightly_profile,
                    "nightly_psa_api": config_nightly_PSA_API,
                    "nightly_ff": config_nightly_PSA_FF,
                    "nightly_otp": config_nightly_OTP,
                    "nightly_psoc64": config_nightly_psoc64,
                    "nightly_stm32l562e_dk": config_STM32L562E_DK,
                    "nightly_lpcxpresso55s69": config_nightly_LPCXPRESSO55S69,
                    "nightly_fp":config_nightly_FP,

                    #per patch test group
                    "pp_test": config_pp_test,
                    "pp_OTP": config_pp_OTP,
                    "pp_PSA_API": config_pp_PSA_API,
                    "pp_psoc64": config_pp_PSoC64,

                    #code coverage test group
                    "coverage_an519": config_cov_an519,
                    "coverage_an521": config_cov_an521,

                    #extra build group
                    "arm_corstone1000": config_corstone1000,
                    "arm_an547": config_an547,
                    "arm_corstone_polaris": config_corstone_polaris,
                    "cypress_psoc64": config_PSOC64,
                    "laird_bl5340": config_bl5340,
                    "nordic_nrf5340dk": config_nrf5340dk,
                    "nordic_nrf9160dk": config_nrf9160dk,
                    "nuvoton_m2351": config_m2351,
                    "nuvoton_m2354": config_m2354,
                    "nxp_lpcxpresso55s69": config_LPCXPRESSO55S69,
                    "stm_b_u585i_iot02a": config_b_u585i_iot02a,
                    "stm_nucleo_l552ze_q": config_nucleo_l552ze_q,
                    "stm_stm32l562e_dk": config_STM32L562E_DK,

                    #full test group in the old CI
                    "full": config_full,

                    #specific test group
                    "an524": config_AN524,
                    "an521": config_AN521,
                    "an521_psa_api": config_AN521_PSA_API,
                    "an521_psa_ipc": config_AN521_PSA_IPC,
                    "an519": config_AN519,
                    "musca_b1": config_MUSCA_B1,
                    "musca_b1_se": config_MUSCA_B1_SE,
                    "musca_s1": config_MUSCA_S1,
                    "psoc64": config_PSOC64,
                    "corstone1000": config_corstone1000,
                    "ipc": config_IPC,
                    "doxygen": config_doxygen,
                    "debug": config_debug,
                    "debug_PSA_API": config_debug_PSA_API,
                    "release": config_release,

                    #DevOps team test group
                    "lava_debug": config_lava_debug,
                    "ci": config_ci}

if __name__ == '__main__':
    import os

    # Default behavior is to export refference config when called
    _dir = os.getcwd()
    from utils import save_json
    for _cname, _cfg in _builtin_configs.items():
        _fname = os.path.join(_dir, _cname + ".json")
        print("Exporting config %s" % _fname)
        save_json(_fname, _cfg)
