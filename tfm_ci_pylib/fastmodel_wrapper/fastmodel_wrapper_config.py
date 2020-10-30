#!/usr/bin/env python3

""" fastmodel_wrapper_config.py:

    Using Python clas inheritance model to generate modular and easily to scale
    configuration models for the run_fpv module. Configuration data is also
    combined with helper methods. If the file is run as a standalone file,
    it can save json configuration files to disk if requested by --export
    directive """

from __future__ import print_function
from collections import OrderedDict
from copy import deepcopy
from pprint import pprint

__copyright__ = """
/*
 * Copyright (c) 2018-2020, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

__author__ = "tf-m@lists.trustedfirmware.org"
__project__ = "Trusted Firmware-M Open CI"
__version__ = "1.2.0"


try:
    from tfm_ci_pylib.utils import save_dict_json
except ImportError:
    import os
    import sys
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "../"))
    from tfm_ci_pylib.utils import save_dict_json


# Used in fixed sorting of configuration before generating a json file
# WARNING modification of this file will fundamentaly change behavior
config_sort_order = [
    "directory",
    "terminal_log",
    "bin",
    "error_on_failed",
    "test_rex", "test_cases",
    "test_end_string",
    "application",
    "data",
    "simlimit",
    "parameters"
]


class fpv_wrapper_config(object):
    """ Controlling Class that wraps around an ARM Fastmodel and controls
    execution, adding regex flow controls, and headless testing """

    # Ensure the dictionary entries are sorted
    _cfg = OrderedDict.fromkeys(config_sort_order)
    _name = "run_fpv"

    def __init__(self,
                 fvp_dir,
                 terminal_file,
                 fvp_binary,
                 eof,
                 test_rex,
                 test_cases,
                 test_end_string,
                 fvp_app,
                 fvp_boot,
                 fvp_sim_limit,
                 params):

        self._cfg["directory"] = fvp_dir
        self._cfg["terminal_log"] = terminal_file
        self._cfg["bin"] = fvp_binary
        self._cfg["error_on_failed"] = eof
        self._cfg["test_rex"] = test_rex
        self._cfg["test_cases"] = test_cases
        self._cfg["test_end_string"] = test_end_string
        self._cfg["application"] = fvp_app
        self._cfg["data"] = fvp_boot
        self._cfg["simlimit"] = fvp_sim_limit
        self._cfg["parameters"] = params

    @classmethod
    def get_config(self):
        """ Return a copy of the fastmodel configuration dictionary """
        return dict(deepcopy(self._cfg))

    @classmethod
    def get_variant_metadata(self):
        """ Return a copy of the class generator variant dictionary """
        return deepcopy(self._vdict)

    @classmethod
    def set_variant_metadata(self, vdict):
        """ Replace the metadata dictionary with user provided one """

        self._vdict = deepcopy(vdict)

        return self

    @classmethod
    def querry_variant_metadata(self, key, value):
        """ Verify that metadata dictionary contains value for key entry """

        return self._vdict[key] == value

    @classmethod
    def rebuild(self):
        """ Recreate the configuration of a class after metadata has been
        modified """

        # Reset the configuration entries to the stock ones
        self._cfg = deepcopy(self._tpl_cfg)

        # recreate a temporary class with proper configuration
        @config_variant(**self._vdict)
        class tmp_class(self):
            pass

        # Copy over the new configuguration from temporary class
        self._cfg = deepcopy(tmp_class._cfg)

    @classmethod
    def print(self):
        """ Print the configuration dictionary in a human readable format """
        pprint(dict(self._cfg))

    @classmethod
    def json_to_file(self, outfile=None):
        """ Create a JSON file with the configration """

        if not outfile:
            outfile = self.get_name() + ".json"
        save_dict_json(outfile, self.get_config(), config_sort_order)
        print("Configuration exported to %s" % outfile)

    @classmethod
    def get_name(self):
        """ Return the name of the configuration """

        return self._name.lower()

    def get_sort_order(self):
        """ Return an ordered list of entries in the configuration """

        return self._cfg.keys()


def config_variant(**override_params):
    """ Class decorator that enables dynamic subclass creation for different
    configuration combinatins. Override params can be any keyword based
    argument of template_cfg._vict """

    def class_rebuilder(cls):
        class TfmFastModelConfig(cls):
            override = False
            _cfg = deepcopy(cls._cfg)
            _tpl_cfg = deepcopy(cls._cfg)
            _vdict = deepcopy(cls._vdict)
            for param, value in override_params.items():
                if param in _vdict.keys():
                    _vdict[param] = value
                    override = True

            if override:
                _vdict["variant_name_tpl"] = _vdict["variant_name_tpl"] \
                    % _vdict

                # Update the configuration dependant enties
                _cfg["terminal_log"] = _cfg["terminal_log"] % _vdict

                # Adjust the binaries based on bootloader presense
                if _vdict["bootloader"] == "BL2":
                    _vdict["app_bin"] = override_params["app_bin"] if \
                        "app_bin" in override_params else "mcuboot.axf"
                    _vdict["data_bin"] = override_params["data_bin"] if \
                        "data_bin" in override_params \
                        else "tfm_s_ns_signed.bin"
                    _vdict["data_bin_offset"] = "0x10080000"
                else:
                    _vdict["app_bin"] = override_params["app_bin"] if \
                        "app_bin" in override_params else "tfm_s.axf"
                    _vdict["data_bin"] = override_params["data_bin"] if \
                        "data_bin" in override_params else "tfm_ns.bin"
                    _vdict["data_bin_offset"] = "0x00100000"

                # Switching from AN519 requires changing the parameter
                # cpu0.baseline=0 -> 1
                if _vdict["platform"] == "AN519":
                    idx = _cfg["parameters"].index("cpu0.baseline=0")
                    cpu_param = _cfg["parameters"].pop(idx).replace("=0", "=1")
                    _cfg["parameters"].append(cpu_param)
                _cfg["application"] = _cfg["application"] % _vdict
                _cfg["data"] = _cfg["data"] % _vdict

                if _vdict["psa_suite"] == "FF":
                    print("TfmFastModelConfig override:")
                    _cfg["parameters"] = [
                        "fvp_mps2.platform_type=2",
                        "cpu0.baseline=0",
                        "cpu0.INITVTOR_S=0x10080400",
                        "cpu0.semihosting-enable=0",
                        "fvp_mps2.DISABLE_GATING=0",
                        "fvp_mps2.telnetterminal0.start_telnet=0",
                        "fvp_mps2.telnetterminal1.start_telnet=0",
                        "fvp_mps2.telnetterminal2.start_telnet=0",
                        "fvp_mps2.telnetterminal0.quiet=1",
                        "fvp_mps2.telnetterminal1.quiet=1",
                        "fvp_mps2.telnetterminal2.quiet=1",
                        "fvp_mps2.UART2.out_file=$TERM_FILE",
                        "fvp_mps2.UART2.unbuffered_output=1",
                        "fvp_mps2.UART0.shutdown_on_eot=1",
                        "fvp_mps2.mps2_visualisation.disable-visualisation=1"]

                _name = cls._name % _vdict

        return TfmFastModelConfig

    return class_rebuilder


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
    _cfg["directory"] = "FVP_MPS2_11.3"
    _cfg["terminal_log"] = "terminal_%(variant_name_tpl)s.log"
    _cfg["bin"] = "FVP_MPS2_AEMv8M"
    _cfg["error_on_failed"] = False
    _cfg["application"] = (
        "cpu0=%(build_path)s/%(variant_name_tpl)s/" +
        "%(app_bin_path)s/%(app_bin)s")
    _cfg["data"] = (
        "cpu0=%(build_path)s/%(variant_name_tpl)s/%(data_bin_path)s/" +
        "%(data_bin)s@%(data_bin_offset)s")
    _cfg["simlimit"] = "60"
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


if __name__ == "__main__":
    # Create Json configuration files on user request
    pass
