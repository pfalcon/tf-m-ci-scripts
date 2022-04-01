#!/usr/bin/env python

#memory_footprint.py : Script for sending memory footprint data from the TFM CI
#to a SQUAD web interface
#
#Copyright (c) 2020-2022, Arm Limited. All rights reserved.
#
#SPDX-License-Identifier: BSD-3-Clause


import argparse
import os
import re
import sys
import json
import requests
import subprocess
import configs
from tfm_ci_pylib import utils

# Arguments/parameters given by CI
PATH_TO_TFM             = sys.argv[1]
CI_CONFIG               = sys.argv[2]
REFERENCE_CONFIGS       = sys.argv[3].split(",")
SQUAD_TOKEN             = sys.argv[4]

# local constant
SQUAD_BASE_PROJECT_URL  = ("https://qa-reports.linaro.org/api/submit/tf/tf-m/")

# This function uses arm_non_eabi_size to get the sizes of a file
#  in the build directory of tfm
def get_file_size(filename):
    f_path = os.path.join(PATH_TO_TFM, "build", "bin", filename)
    if os.path.exists(f_path) :
        file_sizes = utils.arm_non_eabi_size(f_path)[0]
        return file_sizes
    else :
        print(f_path + "Not found")
        return -1

# This function creates a json file containing all the data about
#  memory footprint and sends this data to SQUAD
def send_file_size(change_id, config_name, bl2_sizes, tfms_sizes):
    url = SQUAD_BASE_PROJECT_URL + change_id + '/' + config_name

    try:
        metrics = json.dumps({ "bl2_size"  : bl2_sizes["dec"],
                               "bl2_data"  : bl2_sizes["data"],
                               "bl2_bss"   : bl2_sizes["bss"],
                               "bl2_text"  : bl2_sizes["text"],
                               "tfms_size" : tfms_sizes["dec"],
                               "tfms_data" : tfms_sizes["data"],
                               "tfms_bss"  : tfms_sizes["bss"],
                               "tfms_text" : tfms_sizes["text"]})
    except:
        return -1

    headers = {"Auth-Token": SQUAD_TOKEN}
    data= {"metrics": metrics}

    try:
        #Sending the data to SQUAD, 40s timeout
        result = requests.post(url, headers=headers, data=data, timeout=40)
    except:
        return -1

    with open(os.path.join(PATH_TO_TFM,
                           "..",
                           "tf-m-ci-scripts",
                           "Memory_footprint",
                           "filesize.json"), "w") as F:
        #Storing the json file
        F.write(metrics)

    if not result.ok:
        print(f"Error submitting to qa-reports: {result.reason}: {result.text}")
        return -1
    else :
        print ("POST request sent to project " + config_name )
        return 0

#Function used to launch the configs.py script and get the printed output
def get_configs_by_name(config_names):
    clist = list(configs._builtin_configs.keys())
    out_cfg = {}
    for group in clist:
        build_manager = configs.get_build_manager(group)
        for _cfg_name in config_names:
            if _cfg_name in build_manager._tbm_build_cfg.keys():
                out_cfg[_cfg_name] = build_manager._tbm_build_cfg[_cfg_name]
    return out_cfg

# This funcion manipulates the format of the config given
#  as entry to extract the name of the configuration used
def identify_config():
    name_config = "Unknown"

    try :
        cfg = get_configs_by_name([CI_CONFIG])[CI_CONFIG]
        if (not cfg.lib_model and cfg.isolation_level == "1" and
            not cfg.test_regression and cfg.test_psa_api == "OFF" and
            cfg.cmake_build_type == "Release" and cfg.with_otp == "off" and
            cfg.with_bl2 and cfg.with_ns and
            cfg.profile == "" and cfg.partition_ps == "ON"):
                name_config = "CoreIPC"
        elif (cfg.lib_model and cfg.isolation_level == "1" and
            not cfg.test_regression and cfg.test_psa_api == "OFF"      and
            cfg.cmake_build_type == "Release" and cfg.with_otp == "off"  and
            cfg.with_bl2 and cfg.with_ns and
            cfg.profile == "" and cfg.partition_ps == "ON"):
                name_config = "Default"
        elif (not cfg.lib_model and cfg.isolation_level == "2"    and
            not cfg.test_regression and cfg.test_psa_api == "OFF"     and
            cfg.cmake_build_type == "Release" and cfg.with_otp == "off" and
            cfg.with_bl2 and cfg.with_ns and
            cfg.profile == "" and cfg.partition_ps == "ON"):
                name_config = "CoreIPCTfmLevel2"
        elif (cfg.lib_model and cfg.isolation_level == "1" and
            not cfg.test_regression and cfg.test_psa_api == "OFF"      and
            cfg.cmake_build_type == "Release" and cfg.with_otp == "off"  and
            cfg.with_bl2 and cfg.with_ns and
            cfg.profile == "profile_small" and cfg.partition_ps == "OFF"):
                name_config = "DefaultProfileS"
        elif (cfg.lib_model and cfg.isolation_level == "1" and
            not cfg.test_regression and cfg.test_psa_api == "OFF"      and
            cfg.cmake_build_type == "Minsizerel" and cfg.with_otp == "off"  and
            cfg.with_bl2 and cfg.with_ns and
            cfg.profile == "profile_small" and cfg.partition_ps == "OFF"):
                name_config = "MinSizeProfileS"
        elif (not cfg.lib_model and cfg.isolation_level == "2" and
            not cfg.test_regression and cfg.test_psa_api == "OFF"     and
            cfg.cmake_build_type == "Release" and cfg.with_otp == "off"  and
            cfg.with_bl2 and cfg.with_ns and
            cfg.profile == "profile_medium" and cfg.partition_ps == "ON"):
                name_config = "DefaultProfileM"
        elif (not cfg.lib_model and cfg.isolation_level == "3" and
            not cfg.test_regression and cfg.test_psa_api == "OFF"     and
            cfg.cmake_build_type == "Release" and cfg.with_otp == "off"  and
            cfg.with_bl2 and cfg.with_ns and
            cfg.profile == "profile_large" and cfg.partition_ps == "ON"):
                name_config = "DefaultProfileL"
        ret = [cfg.tfm_platform,cfg.compiler, name_config]
    except:
        ret = ["Unknown", "Unknown", "Unknown"]
    return ret

# Function based on get_local_git_info() from utils, getting change id for the tfm repo
def get_change_id(directory):
    directory = os.path.abspath(directory)
    cur_dir = os.path.abspath(os.getcwd())
    cmd = "git log HEAD -n 1  --pretty=format:'%b'"

    os.chdir(directory) # Going to the repo's directory

    git_info_rex = re.compile(r'(?P<body>^[\s\S]*?)((?:Change-Id:\s)'
                              r'(?P<change_id>.*)\n?)', re.MULTILINE)

    r, e = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE).communicate()

    if e:
        print("Error", e)
        return -1
    else:
        try:
            txt_body = r.decode('ascii')
        except UnicodeDecodeError as E:
            txt_body = r.decode('utf-8')
        result = txt_body.rstrip()

    try:
        change_id = git_info_rex.search(result).groupdict()["change_id"].strip()
    except:
        return -1

    os.chdir(cur_dir) #Going back to the initial directory
    return change_id

if __name__ == "__main__":
    # Export GCC v7.3.1 to ENV PATH
    os.environ["PATH"] += os.pathsep + os.getenv('GCC_7_3_1_PATH')
    for i in range(len(REFERENCE_CONFIGS)):
        REFERENCE_CONFIGS[i] = REFERENCE_CONFIGS[i].strip().lower()
    config = identify_config()
    if (config[2].lower() in REFERENCE_CONFIGS
        and config[0] == "arm/mps2/an521"
        and config[1] == "toolchain_GNUARM.cmake"):
        # Pushing data for AN521 and GNUARM
        print("Configuration " + config[2] + " is a reference")
        try :
            change_id = get_change_id(PATH_TO_TFM)
        except :
            change_id = -1
        bl2_sizes = get_file_size("bl2.axf")
        tfms_sizes = get_file_size("tfm_s.axf")
        if (bl2_sizes != -1 and change_id != -1) :
            send_file_size(change_id, config[2], bl2_sizes, tfms_sizes)
        else :
            #Directory or file weren't found
            if change_id == -1 :
                print("Error : trusted-firmware-m repo not found")
            else :
                print("Error : file not found")
