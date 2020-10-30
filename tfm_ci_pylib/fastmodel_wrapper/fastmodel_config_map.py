#!/usr/bin/env python3

""" fastmodel_config_map.py:

    Using Python clas inheritance model to generate modular and easily to scale
    configuration models for the run_fpv module. Configuration data is also
    combined with helper methods. If the file is run as a standalone file,
    it can save json configuration files to disk if requested by --export
    directive """

from __future__ import print_function
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


class FastmodelConfigMap(object):

    def __init__(self, enviroment, platform):
        pass

        self._platforms = [platform]
        self._cfg_map = self.global_import(enviroment)
        self._invalid = []

    def add_invalid(self, invalid_tuple):
        self._invalid.append(invalid_tuple)

    def get_invalid(self):
        return deepcopy(self._invalid)

    def global_import(self, enviroment, classname="TfmFastModelConfig"):
        """ Import modules with specified classname from enviroment
        provided by caller """

        # Select the imported modules with a  __name__ attribute
        ol = {nme: cfg for nme, cfg in enviroment.items()
              if hasattr(cfg, '__name__')}

        # Select those who match the classname
        fcfg = {nme: cfg_obj for nme, cfg_obj
                in ol.items() if cfg_obj .__name__ == classname}

        return {self._platforms[0]: fcfg}

    def __add__(self, obj_b):
        """ Override addition operator """

        # Create a new object of left hand operant for return
        ret_obj = deepcopy(self)

        # Get references to new class members
        map_a = ret_obj._cfg_map
        platforms_a = ret_obj._platforms
        map_b = obj_b.get_object_map()
        for platform, config in map_b.items():

            if platform in map_a.keys():
                for cfg_name, cfg_object in config.items():
                    if cfg_name in map_a[platform].keys():
                        print("Matching entrty name %s" % (cfg_name))
                        print("Left operant entry: %s "
                              "will be replaced by: %s" %
                              (map_a[platform][cfg_name], cfg_object))
                    map_a[platform][cfg_name] = cfg_object
            else:
                map_a[platform] = deepcopy(config)
                platforms_a.append(platform)

        return ret_obj

    def _cmerge(self):
        """ Join all the platform configs """

        ret = {}
        for entry in self._cfg_map.values():
            for name, cfg in entry.items():
                ret[name] = cfg
        return ret

    def get_object_map(self):
        """ Returns the config map as objects """

        return deepcopy(self._cfg_map)

    def get_config_map(self):
        """ Return a copy of the config map with the config objects rendered
        as dictionaries """

        ret_dict = deepcopy(self._cfg_map)
        for platform, config in self._cfg_map.items():
            for name, cfg_object in config.items():
                ret_dict[platform][name] = cfg_object.get_config()
        return ret_dict

    def list(self):
        """ Print a quick list of the contained platforms and
         configuration names """

        return list(self._cmerge().keys())

    def print_list(self):
        """ Print a quick list of the contained platforms and
         configuration names """

        for platform, config in self._cfg_map.items():
            print("=========== Platform: %s ===========" % platform)
            for name, cfg_object in config.items():
                print(name)

    def print(self):
        """ Print the contents of a human readable config map """

        pprint(self.get_config_map())

    def get_config_object(self, config_name, platform=None):
        try:
            cfg_dict = self._cfg_map[platform]
        except Exception as e:
            cfg_dict = self._cmerge()

        return cfg_dict[config_name]

    def get_config(self, config_name, platform=None):

        return self.get_config_object(config_name, platform).get_config()

    def patch_config(self, cfg_name, key, new_data, platform=None):
        """ Modify a configuration entry, and re-render the class """

        cfg_object = self.get_config_object(cfg_name, platform)

        # Do not
        if cfg_object.get_variant_metadata()[key] == new_data:
            return
        v_meta = cfg_object.get_variant_metadata()
        v_meta[key] = new_data
        cfg_object.set_variant_metadata(v_meta).rebuild()


def fvp_config_object_change_path(cfg_object, new_path):
    """ Change the common artifact storage path and update its
    configuration """
