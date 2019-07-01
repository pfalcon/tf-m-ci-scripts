#!/usr/bin/env python3

""" builtin_configs.py:

    Default configuration files used as reference """

from __future__ import print_function

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

    # A small subset of  string substitution params is allowed in commands.
    # tfm_build_manager will replace %(_tbm_build_dir_)s,  %(_tbm_code_dir_)s,
    # _tbm_target_platform_ with the  paths set when building

    "artifact_capture_rex": (r'%(_tbm_build_dir_)s/install/outputs/'
                             r'(?:fvp|AN521|AN519|MUSCA_A|MUSCA_B1)'
                             r'/(\w+\.(?:axf|bin|hex))$'),

    # ALL commands will be executed for every build.
    # Other keys will append extra commands when matching target_platform
    "build_cmds": {"all": ["cmake --build ./ -- -j 2 install"],
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
                                 "-Binary -offset 0x200000 "
                                 "%(_tbm_build_dir_)s/install/outputs/"
                                 "%(_tbm_target_platform_)s/tfm_sign.bin "
                                 "-Binary -offset 0x220000 -o "
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
config_AN521 = {"seed_params": {
                "target_platform": ["AN521"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigRegression",
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
config_AN519 = {"seed_params": {
                "target_platform": ["AN519"],
                "compiler": ["ARMCLANG", "GNUARM"],
                "proj_config": ["ConfigRegression",
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
                              "ConfigCoreIPCTfmLevel2"],
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
               "target_platform": ["AN521", "AN519", "MUSCA_A", "MUSCA_B1"],
               "compiler": ["ARMCLANG", "GNUARM"],
               "proj_config": ["ConfigRegression",
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
                           ("MUSCA_B1", "*", "*", "*", False)]
               }

config_MUSCA_A = {"seed_params": {
                  "target_platform": ["MUSCA_A"],
                  "compiler": ["ARMCLANG", "GNUARM"],
                  "proj_config": ["ConfigRegression",
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

# Configruation used in testing
config_debug = {"seed_params": {
                "target_platform": ["AN521"],
                "compiler": ["ARMCLANG"],
                "proj_config": ["ConfigDefault"],
                "cmake_build_type": ["Debug"],
                "with_mcuboot": [True],
                },
                "common_params": _common_tfm_builder_cfg,
                # invalid configuations can be added as tuples of adjustable
                # resolution "AN521" will reject all combinations for that
                # platform while ("AN521", "GNUARM") will only reject GCC ones
                "invalid": [("*", "GNUARM", "*", "*", False),
                            ("AN521", "ARMCLANG", "ConfigRegression",
                             "Release", False),
                            ]
                }

_builtin_configs = {"full": config_full,
                    "an521": config_AN521,
                    "an519": config_AN519,
                    "musca_a": config_MUSCA_A,
                    "musca_b1": config_MUSCA_B1,
                    "ipc": config_IPC,
                    "doxygen": config_doxygen,
                    "debug": config_debug}

if __name__ == '__main__':
    import os

    # Default behavior is to export refference config when called
    _dir = os.getcwd()
    from utils import save_json
    for _cname, _cfg in _builtin_configs.items():
        _fname = os.path.join(_dir, _cname + ".json")
        print("Exporting config %s" % _fname)
        save_json(_fname, _cfg)
