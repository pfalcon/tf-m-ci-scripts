#!/usr/bin/env python3

""" builtin_configs.py:

    Default configuration files used as reference """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2020, Arm Limited. All rights reserved.
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

# common parameters for tf-m build system
# This configuration template will be passed into the tfm-builder module after
# the template evaluation is converted to a command

_common_tfm_builder_cfg = {
    "config_type": "tf-m",
    "codebase_root_dir": "tf-m",
    # Order to which the variants are evaluated. This affects the name of
    # variant configuration and the wildcard replacement logic in invalid
    # configuration tuples
    "sort_order": ["target_platform",
                   "compiler",
                   "proj_config",
                   "psa_api_suit",
                   "with_OTP",
                   "cmake_build_type",
                   "with_mcuboot"],

    # Keys for the templace will come from the combinations of parameters
    # provided in the seed dictionary.

    "config_template": (
        "cmake -G \"Unix Makefiles\" "
        "-DPROJ_CONFIG=`"
        "readlink -f %(codebase_root_dir)s/configs/%(proj_config)s.cmake` "
        "-DTARGET_PLATFORM=%(target_platform)s "
        "-DCOMPILER=%(compiler)s "
        "-DCMAKE_BUILD_TYPE=%(cmake_build_type)s "
        "-DBL2=%(with_mcuboot)s "
        "%(codebase_root_dir)s"),

    "config_template_psa_api": (
        "cmake -G \"Unix Makefiles\" "
        "-DPROJ_CONFIG=`"
        "readlink -f %(codebase_root_dir)s/configs/%(proj_config)s.cmake` "
        "-DTARGET_PLATFORM=%(target_platform)s "
        "-DCOMPILER=%(compiler)s "
        "-DCMAKE_BUILD_TYPE=%(cmake_build_type)s "
#TODO: error when using this param
#        "-DPSA_API_TEST_BUILD_PATH=%(_tbm_build_dir_)s "
        "%(codebase_root_dir)s"),

    # A small subset of  string substitution params is allowed in commands.
    # tfm_build_manager will replace %(_tbm_build_dir_)s,  %(_tbm_code_dir_)s,
    # _tbm_target_platform_ with the  paths set when building

    "artifact_capture_rex": (r'%(_tbm_build_dir_)s/install/outputs/'
                             r'(?:fvp|AN521|AN519|MUSCA_A|MUSCA_B1)'
                             r'/(\w+\.(?:axf|bin|hex))$'),

    # ALL commands will be executed for every build.
    # Other keys will append extra commands when matching target_platform
    "build_cmds": {"all": ["cmake --build ./ -- install"],
                   "MUSCA_A": [("srec_cat "
                                "%(_tbm_build_dir_)s/install/outputs/"
                                "%(_tbm_target_platform_)s/mcuboot.bin "
                                "-Binary -offset 0x200000 "
                                "%(_tbm_build_dir_)s/install/outputs/"
                                "%(_tbm_target_platform_)s/tfm_sign.bin "
                                "-Binary -offset 0x220000 -o "
                                "%(_tbm_build_dir_)s/install/outputs/"
                                "%(_tbm_target_platform_)s"
                                "/tfm.hex -Intel")],
                   "MUSCA_B1": [("srec_cat "
                                 "%(_tbm_build_dir_)s/install/outputs/"
                                 "%(_tbm_target_platform_)s/mcuboot.bin "
                                 "-Binary -offset 0xA000000 "
                                 "%(_tbm_build_dir_)s/install/outputs/"
                                 "%(_tbm_target_platform_)s/tfm_sign.bin "
                                 "-Binary -offset 0xA020000 -o "
                                 "%(_tbm_build_dir_)s/install/outputs/"
                                 "%(_tbm_target_platform_)s"
                                 "/tfm.hex -Intel")]
                   },

    # (Optional) If set will fail if those artefacts are missing post build
    "required_artefacts": {"all": [
                           "%(_tbm_build_dir_)s/install/outputs/"
                           "%(_tbm_target_platform_)s/tfm_s.bin",
                           "%(_tbm_build_dir_)s/install/outputs/"
                           "%(_tbm_target_platform_)s/tfm_ns.bin"],
                           "MUSCA_A": [
                           "%(_tbm_build_dir_)s/install/outputs/"
                           "%(_tbm_target_platform_)s/tfm.hex",
                           "%(_tbm_build_dir_)s/install/outputs/"
                           "%(_tbm_target_platform_)s/mcuboot.bin",
                           "%(_tbm_build_dir_)s/install/outputs/"
                           "%(_tbm_target_platform_)s/tfm_sign.bin"],
                           "MUSCA_B1": [
                           "%(_tbm_build_dir_)s/install/outputs/"
                           "%(_tbm_target_platform_)s/tfm.hex",
                           "%(_tbm_build_dir_)s/install/outputs/"
                           "%(_tbm_target_platform_)s/mcuboot.bin",
                           "%(_tbm_build_dir_)s/install/outputs/"
                           "%(_tbm_target_platform_)s/tfm_sign.bin"]
                           }
}

# Configure build manager to build several combinations
config_AN539 = {"seed_params": {
                "target_platform": ["AN539"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigRegression",
                                "ConfigRegressionIPC",
                                "ConfigRegressionIPCTfmLevel2",
                                "ConfigCoreIPC",
                                "ConfigCoreIPCTfmLevel2",
                                "ConfigDefault"],
                "cmake_build_type": ["Debug", "Release"],
                "with_mcuboot": [True, False],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configure build manager to build several combinations
config_AN524 = {"seed_params": {
                "target_platform": ["AN524"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigRegression",
                                "ConfigRegressionIPC",
                                "ConfigRegressionIPCTfmLevel2",
                                "ConfigCoreIPC",
                                "ConfigCoreIPCTfmLevel2",
                                "ConfigDefault"],
                "cmake_build_type": ["Debug", "Release"],
                "with_mcuboot": [True, False],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configure build manager to build several combinations
config_AN521 = {"seed_params": {
                "target_platform": ["AN521"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigRegression",
                                "ConfigRegressionIPC",
                                "ConfigRegressionIPCTfmLevel2",
                                "ConfigCoreIPC",
                                "ConfigCoreIPCTfmLevel2",
                                "ConfigDefault"],
                "cmake_build_type": ["Debug", "Release"],
                "with_mcuboot": [True, False],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configure build manager to build several combinations
config_PSA_API = {"seed_params": {
                "target_platform": ["AN521", "MUSCA_B1"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigPsaApiTest",
                                "ConfigPsaApiTestIPC",
                                "ConfigPsaApiTestIPCTfmLevel2"],
                "psa_api_suit": ["CRYPTO",
                                 "PROTECTED_STORAGE",
                                 "INITIAL_ATTESTATION",
                                 "INTERNAL_TRUSTED_STORAGE"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_mcuboot": [True],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configure build manager to build several combinations
config_PSA_FF = {"seed_params": {
                "target_platform": ["AN521", "MUSCA_B1"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigPsaApiTestIPC",
                                "ConfigPsaApiTestIPCTfmLevel2"],
                # Prefer to use "IPC" from compile command perspective
                # But the name style is prefer "FF"
                "psa_api_suit": ["FF"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_mcuboot": [True],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configure build manager to build several combinations
config_PSA_API_OTP = {"seed_params": {
                "target_platform": ["MUSCA_B1"],#
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigPsaApiTest",
                                "ConfigPsaApiTestIPC",
                                "ConfigPsaApiTestIPCTfmLevel2"],
                "psa_api_suit": ["CRYPTO",
                                 "PROTECTED_STORAGE",
                                 "INITIAL_ATTESTATION",
                                 "INTERNAL_TRUSTED_STORAGE"],
                "with_OTP": ["OTP"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],#
                "with_mcuboot": [True],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configure build manager to build several combinations
config_PSA_FF_OTP = {"seed_params": {
                "target_platform": ["MUSCA_B1"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigPsaApiTestIPC",
                                "ConfigPsaApiTestIPCTfmLevel2"],
                # Prefer to use "IPC" from compile command perspective
                # But the name style is prefer "FF"
                "psa_api_suit": ["FF"],
                "with_OTP": ["OTP"],
                "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                "with_mcuboot": [True],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configure build manager to build several combinations
config_PSOC64 = {"seed_params": {
                "target_platform": ["psoc64"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigRegressionIPC",
                                "ConfigRegressionIPCTfmLevel2"],
                "cmake_build_type": ["Release"],
                "with_mcuboot": [False],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configure build manager to build several combinations
config_AN519 = {"seed_params": {
                "target_platform": ["AN519"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigRegression",
                                "ConfigRegressionIPC",
                                "ConfigRegressionIPCTfmLevel2",
                                "ConfigCoreIPC",
                                "ConfigCoreIPCTfmLevel2",
                                "ConfigDefault"],
                "cmake_build_type": ["Debug", "Release"],
                "with_mcuboot": [True, False],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

config_IPC = {"seed_params": {
              "target_platform": ["AN521", "AN519", "MUSCA_A", "MUSCA_B1"],
              "compiler": ["ARMCLANG", "GNUARM"],
              "proj_config": ["ConfigCoreIPC",
                              "ConfigCoreIPCTfmLevel2",
                              "ConfigRegressionIPC",
                              "ConfigRegressionIPCTfmLevel2"],
              "cmake_build_type": ["Debug", "Release"],
              "with_mcuboot": [True, False],
              },
              "common_params": _common_tfm_builder_cfg,
              # invalid configuations can be added as tuples of adjustable
              # resolution "AN521" will reject all combinations for that
              # platform while ("AN521", "GNUARM") will only reject GCC
              "invalid": [("MUSCA_B1", "*", "*", "*", False)]
              }

# Configure build manager to build the maximum number of configurations
config_full = {"seed_params": {
               "target_platform": ["AN521", "AN519",
                                   "MUSCA_A", "MUSCA_B1",
                                   "AN524", "AN539",
                                   "psoc64"],
               "compiler": ["ARMCLANG", "GNUARM"],
               "proj_config": ["ConfigRegression",
                               "ConfigRegressionIPC",
                               "ConfigRegressionIPCTfmLevel2",
                               "ConfigCoreIPC",
                               "ConfigCoreIPCTfmLevel2",
                               "ConfigDefault"],
               "cmake_build_type": ["Debug", "Release"],
               "with_mcuboot": [True, False],
               },
               "common_params": _common_tfm_builder_cfg,
               # invalid configuations can be added as tuples of adjustable
               # resolution "AN521" will reject all combinations for that
               # platform while ("AN521", "GNUARM") will only reject GCC ones
               "invalid": [("MUSCA_A", "*", "*", "*", False),
                           ("MUSCA_B1", "*", "*", "*", False),
                           ("psoc64", "*", "*", "*", True),
                           ("psoc64", "*", "*", "Debug", "*"),
                           ("psoc64", "*", "ConfigRegression", "*", "*"),
                           ("psoc64", "*", "ConfigCoreIPC", "*", "*"),
                           ("psoc64", "*", "ConfigCoreIPCTfmLevel2", "*", "*"),
                           ("psoc64", "*", "ConfigDefault", "*", "*")]
               }

# Configure build manager to build the maximum number of configurations
config_full_gnuarm = {"seed_params": {
               "target_platform": ["AN521", "AN519",
                                   "MUSCA_A", "MUSCA_B1",
                                   "AN524", "AN539",
                                   "psoc64"],
               "compiler": ["GNUARM"],
               "proj_config": ["ConfigRegression",
                               "ConfigRegressionIPC",
                               "ConfigRegressionIPCTfmLevel2",
                               "ConfigCoreIPC",
                               "ConfigCoreIPCTfmLevel2",
                               "ConfigDefault"],
               "cmake_build_type": ["Debug", "Release"],
               "with_mcuboot": [True, False],
               },
               "common_params": _common_tfm_builder_cfg,
               # invalid configuations can be added as tuples of adjustable
               # resolution "AN521" will reject all combinations for that
               # platform while ("AN521", "GNUARM") will only reject GCC ones
               "invalid": [("MUSCA_A", "*", "*", "*", False),
                           ("MUSCA_B1", "*", "*", "*", False),
                           ("psoc64", "*", "*", "*", True),
                           ("psoc64", "*", "*", "Debug", "*"),
                           ("psoc64", "*", "ConfigRegression", "*", "*"),
                           ("psoc64", "*", "ConfigCoreIPC", "*", "*"),
                           ("psoc64", "*", "ConfigCoreIPCTfmLevel2", "*", "*"),
                           ("psoc64", "*", "ConfigDefault", "*", "*")]
               }

# Configure build manager to build the maximum number of configurations
config_tfm_test = {"seed_params": {
                  "target_platform": ["AN521", "MUSCA_A", "MUSCA_B1", "MUSCA_S1"],
                  "compiler": ["ARMCLANG", "GNUARM"],
                  "proj_config": ["ConfigRegression",
                                  "ConfigRegressionIPC",
                                  "ConfigRegressionIPCTfmLevel2",
                                  "ConfigCoreIPC",
                                  "ConfigCoreIPCTfmLevel2",
                                  "ConfigDefault"],
                  "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                  "with_mcuboot": [True, False],
                  },
                  "common_params": _common_tfm_builder_cfg,
                  # invalid configuations can be added as tuples of adjustable
                  # resolution "AN521" will reject all combinations for that
                  # platform while ("AN521", "GNUARM") will only reject GCC ones
                  "invalid": [("MUSCA_A", "*", "*", "*", False),
                              ("MUSCA_S1", "*", "*", "*", False),
                              ("MUSCA_B1", "*", "*", "*", False)]
                  }
# Configure build manager to build the maximum number of configurations
config_tfm_test2 = {"seed_params": {
                  "target_platform": ["AN519", "AN524", "AN539", "SSE-200_AWS"],
                  "compiler": ["ARMCLANG", "GNUARM"],
                  "proj_config": ["ConfigRegression",
                                  "ConfigRegressionIPC",
                                  "ConfigRegressionIPCTfmLevel2",
                                  "ConfigCoreIPC",
                                  "ConfigCoreIPCTfmLevel2",
                                  "ConfigDefault"],
                  "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                  "with_mcuboot": [True, False],
                  },
                  "common_params": _common_tfm_builder_cfg,
                  # invalid configuations can be added as tuples of adjustable
                  # resolution "AN521" will reject all combinations for that
                  # platform while ("AN521", "GNUARM") will only reject GCC ones
                  "invalid": []
                  }

# Configure build manager to build the maximum number of configurations
config_tfm_test_OTP = {"seed_params": {
                  "target_platform": ["MUSCA_B1"],
                  "compiler": ["ARMCLANG", "GNUARM"],
                  "proj_config": ["ConfigRegression",
                                  "ConfigRegressionIPC",
                                  "ConfigRegressionIPCTfmLevel2",
                                  "ConfigCoreIPC",
                                  "ConfigCoreIPCTfmLevel2",
                                  "ConfigDefault"],
                  "with_OTP": ["OTP"],
                  "cmake_build_type": ["Debug", "Release", "Minsizerel"],
                  "with_mcuboot": [True],
                  },
                  "common_params": _common_tfm_builder_cfg,
                  # invalid configuations can be added as tuples of adjustable
                  # resolution "AN521" will reject all combinations for that
                  # platform while ("AN521", "GNUARM") will only reject GCC ones
                  "invalid": []
                  }

config_MUSCA_A = {"seed_params": {
                  "target_platform": ["MUSCA_A"],
                  "compiler": ["ARMCLANG", "GNUARM"],
                  "proj_config": ["ConfigRegression",
                                  "ConfigRegressionIPC",
                                  "ConfigRegressionIPCTfmLevel2",
                                  "ConfigCoreIPC",
                                  "ConfigCoreIPCTfmLevel2",
                                  "ConfigDefault"],
                  "cmake_build_type": ["Debug", "Release"],
                  "with_mcuboot": [True],
                  },
                  "common_params": _common_tfm_builder_cfg,
                  # invalid configuations can be added as tuples of adjustable
                  # resolution "AN521" will reject all combinations for that
                  # platform while ("AN521", "GNUARM") will only reject GCC
                  "invalid": [("MUSCA_A", "*", "*", "*", False)]
                  }

config_MUSCA_B1 = {"seed_params": {
                   "target_platform": ["MUSCA_B1"],
                   "compiler": ["ARMCLANG", "GNUARM"],
                   "proj_config": ["ConfigRegression",
                                   "ConfigRegressionIPC",
                                   "ConfigRegressionIPCTfmLevel2",
                                   "ConfigCoreIPC",
                                   "ConfigCoreIPCTfmLevel2",
                                   "ConfigDefault"],
                   "cmake_build_type": ["Debug", "Release"],
                   "with_mcuboot": [True],
                   },
                   "common_params": _common_tfm_builder_cfg,
                   # invalid configuations can be added as tuples of adjustable
                   # resolution "AN521" will reject all combinations for that
                   # platform while ("AN521", "GNUARM") will only reject GCC
                   "invalid": [("MUSCA_B1", "*", "*", "*", False)]
                   }

# Configure build manager to build the maximum number of configurations
config_release = {"seed_params": {
                  "target_platform": ["AN521", "AN519",
                                      "MUSCA_A", "MUSCA_B1", "MUSCA_S1",
                                      "AN524", "AN539"],
                  "compiler": ["ARMCLANG", "GNUARM"],
                  "proj_config": ["ConfigRegression",
                                  "ConfigRegressionIPC",
                                  "ConfigRegressionIPCTfmLevel2",
                                  "ConfigCoreIPC",
                                  "ConfigCoreIPCTfmLevel2",
                                  "ConfigDefault"],
                  "cmake_build_type": ["Debug", "Release", "MINSIZEREL"],
                  "with_mcuboot": [True, False],
                  },
                  "common_params": _common_tfm_builder_cfg,
                  # invalid configuations can be added as tuples of adjustable
                  # resolution "AN521" will reject all combinations for that
                  # platform while ("AN521", "GNUARM") will only reject GCC ones
                  "invalid": [("MUSCA_A", "*", "*", "*", False),
                              ("MUSCA_S1", "*", "*", "*", False),
                              ("MUSCA_B1", "*", "*", "*", False)]
                  }

# Configure build manager to build several combinations
config_AN521_PSA_API = {"seed_params": {
                "target_platform": ["AN521", "AN519", "MUSCA_B1"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigPsaApiTest",
                                "ConfigPsaApiTestIPC",
                                "ConfigPsaApiTestIPCTfmLevel2"],
                "psa_api_suit": ["CRYPTO",
                                 "PROTECTED_STORAGE",
                                 "INITIAL_ATTESTATION",
                                 "INTERNAL_TRUSTED_STORAGE",
                                 "IPC"],
                "cmake_build_type": ["Debug", "Release", "MINSIZEREL"],
                "with_mcuboot": [True],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": [("*", "*", "*", "IPC", "*", "*")]
                }

# Configure build manager to build several combinations
config_AN521_PSA_IPC = {"seed_params": {
                "target_platform": ["AN521", "AN519", "MUSCA_B1"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigPsaApiTestIPC",
                                "ConfigPsaApiTestIPCTfmLevel2"],
                "psa_api_suit": ["IPC"],
                "cmake_build_type": ["Debug", "Release", "MINSIZEREL"],
                "with_mcuboot": [True],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": []
                }

# Configruation used for document building
config_doxygen = {"common_params": {
                  "config_type": "tf-m_documents",
                  "codebase_root_dir": "tf-m",
                  "build_cmds": {"all": ["cmake -G \"Unix Makefiles\" "
                                         "-DPROJ_CONFIG=`readlink -f "
                                         "%(_tbm_code_dir_)s/"
                                         "configs/ConfigDefault.cmake` "
                                         "-DTARGET_PLATFORM=AN521 "
                                         "-DCOMPILER=GNUARM "
                                         "-DCMAKE_BUILD_TYPE=Debug "
                                         "-DBL2=True "
                                         "%(_tbm_code_dir_)s/",
                                         "cmake --build ./ -- install_doc",
                                         "cmake --build ./ "
                                         "-- install_userguide"]},
                  "artifact_capture_rex": r'%(_tbm_build_dir_)s/install/'
                                          r'doc/reference_manual/(?:pdf|html)'
                                          r'/(\w+\.(?:html|md|pdf))$',
                  },
                  "invalid": []
                  }

# Configuration used in testing
config_debug = {"seed_params": {
                "target_platform": ["AN521"],
                "compiler": ["ARMCLANG"],
                "proj_config": ["ConfigDefault"],
                "cmake_build_type": ["Debug"],
                "with_mcuboot": [True],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configurations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": [("*", "GNUARM", "*", "*", False),
                            ("AN521", "ARMCLANG", "ConfigRegression",
                             "Release", False),
                            ]
                }

# Configuration used in CI
config_ci = {
    "seed_params": {
        "target_platform": ["AN521"],
        "compiler": ["ARMCLANG", "GNUARM"],
        "proj_config": ["ConfigDefault", "ConfigCoreIPCTfmLevel2", "ConfigCoreIPC", "ConfigRegression"],
        "cmake_build_type": ["Release"],
        "with_mcuboot": [True, False],
    },
    "common_params": _common_tfm_builder_cfg,
    "invalid": [
        ("AN521", "ARMCLANG", "ConfigDefault", "Release", False),
        ("AN521", "ARMCLANG", "ConfigCoreIPCTfmLevel2", "Release", False),
        ("AN521", "ARMCLANG", "ConfigCoreIPCTfmLevel2", "Release", True),
        ("AN521", "ARMCLANG", "ConfigCoreIPC", "Release", False),
        ("AN521", "ARMCLANG", "ConfigCoreIPC", "Release", True),
        ("AN521", "ARMCLANG", "ConfigRegression", "Release", False),
        ("AN521", "ARMCLANG", "ConfigRegression", "Release", True),
    ],
}

# Configuration used in CI if armclang not available
config_ci_gnuarm = {
    "seed_params": {
        "target_platform": ["AN521"],
        "compiler": ["ARMCLANG", "GNUARM"],
        "proj_config": ["ConfigDefault", "ConfigCoreIPCTfmLevel2", "ConfigCoreIPC", "ConfigRegression"],
        "cmake_build_type": ["Release"],
        "with_mcuboot": [True, False],
    },
    "common_params": _common_tfm_builder_cfg,
    "invalid": [
        ("AN521", "ARMCLANG", "ConfigDefault", "Release", False),
        ("AN521", "ARMCLANG", "ConfigCoreIPCTfmLevel2", "Release", False),
        ("AN521", "ARMCLANG", "ConfigCoreIPCTfmLevel2", "Release", True),
        ("AN521", "ARMCLANG", "ConfigCoreIPC", "Release", False),
        ("AN521", "ARMCLANG", "ConfigCoreIPC", "Release", True),
        ("AN521", "ARMCLANG", "ConfigRegression", "Release", False),
        ("AN521", "ARMCLANG", "ConfigRegression", "Release", True),
        ("*", "ARMCLANG", "*", "*", "*"),  # Disable ARMCLANG for now
    ],
}


config_lava_debug = {
    "seed_params": {
        "target_platform": ["AN521", "AN519"],
        "compiler": ["GNUARM"],
        "proj_config": ["ConfigRegressionIPC", "ConfigRegressionIPCTfmLevel2", "ConfigRegression"],
        "cmake_build_type": ["Release"],
        "with_mcuboot": [True, False],
    },
    "common_params": _common_tfm_builder_cfg,
    "invalid": [
        ("AN521", "ARMCLANG", "ConfigDefault", "Release", True),
        ("AN521", "GNUARM", "ConfigCoreIPCTfmLevel2", "Release", True),
    ],
}

_builtin_configs = {
                    "tfm_test": config_tfm_test,
                    "tfm_test2": config_tfm_test2,
                    "tfm_test_otp": config_tfm_test_OTP,
                    "psa_api": config_PSA_API,
                    "psa_api_otp": config_PSA_API_OTP,
                    "psa_ff": config_PSA_FF,
                    "psa_ff_otp": config_PSA_FF_OTP,
                    "full": config_full,
                    "full_gnuarm": config_full_gnuarm,
                    "an539": config_AN539,
                    "an524": config_AN524,
                    "an521": config_AN521,
                    "an519": config_AN519,
                    "musca_a": config_MUSCA_A,
                    "musca_b1": config_MUSCA_B1,
                    "psoc64": config_PSOC64,
                    "ipc": config_IPC,
                    "doxygen": config_doxygen,
                    "debug": config_debug,
                    "release": config_release,
                    "an521_psa_api": config_AN521_PSA_API,
                    "an521_psa_ipc": config_AN521_PSA_IPC,
                    "debug": config_debug,
                    "lava_debug": config_lava_debug,
                    "ci": config_ci,
                    "ci_gnuarm": config_ci_gnuarm}

if __name__ == '__main__':
    import os

    # Default behavior is to export refference config when called
    _dir = os.getcwd()
    from utils import save_json
    for _cname, _cfg in _builtin_configs.items():
        _fname = os.path.join(_dir, _cname + ".json")
        print("Exporting config %s" % _fname)
        save_json(_fname, _cfg)
