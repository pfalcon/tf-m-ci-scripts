#!/usr/bin/env python

#memory_footprint.py : Script for sending memory footprint data from the TFM CI
#to a SQUAD web interface
#
#Copyright (c) 2020-2021, Arm Limited. All rights reserved.
#
#SPDX-License-Identifier: BSD-3-Clause


import argparse
import os
import re
import sys
import json
import requests
import subprocess
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
        bl2_sizes = utils.arm_non_eabi_size(f_path)[0]
        return bl2_sizes
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
                               "tfms_size" : tfms_sizes["dec"],
                               "tfms_data" : tfms_sizes["data"],
                               "tfms_bss"  : tfms_sizes["bss"]})
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
def get_config(config_string):
    script_directory = os.path.join(PATH_TO_TFM, "..", "tf-m-ci-scripts")
    directory = os.path.abspath(script_directory)
    cur_dir = os.path.abspath(os.getcwd())
    os.chdir(directory) # Going to the repo's directory

    cmd = "python3 configs.py " + config_string

    rex = re.compile(r'(?P<config>^[\s\S]*?)((?:TFM_PLATFORM=)'
                     r'(?P<platform>.*)\n)((?:TOOLCHAIN_FILE=)'
                     r'(?P<toolchain>.*)\n)((?:PSA_API=)'
                     r'(?P<psa>.*)\n)((?:ISOLATION_LEVEL=)'
                     r'(?P<isolation_level>.*)\n)((?:TEST_REGRESSION=)'
                     r'(?P<regression>.*)\n)((?:TEST_PSA_API=)'
                     r'(?P<psa_test>.*)\n)((?:CMAKE_BUILD_TYPE=)'
                     r'(?P<build_type>.*)\n)((?:OTP=)'
                     r'(?P<otp>.*)\n)((?:BL2=)'
                     r'(?P<bl2>.*)\n)((?:NS=)'
                     r'(?P<ns>.*)\n)((?:PROFILE=)'
                     r'(?P<profile>.*)\n)((?:PARTITION_PS=)'
                     r'(?P<partition_ps>.*)?)', re.MULTILINE)

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

    m = rex.search(txt_body)
    match_dict = m.groupdict()

    match_dict = {k: simple_filter(v) for k, v in match_dict.items()}

    os.chdir(cur_dir)

    return match_dict

def simple_filter(A):
    try:
        a = A.lower()
        if a in ["true", "on"]:
            return True
        elif a in ["false", "off"]:
            return False
        else:
            return A
    except Exception:
        return A

# This funcion manipulates the format of the config given
#  as entry to extract the name of the configuration used
def identify_config(ci_config):
    arguments = get_config(CI_CONFIG)
    name_config = "Unknown"
    try :
        if (arguments["psa"] and arguments["isolation_level"] == "1"      and
            not arguments["regression"] and not arguments["psa_test"]     and
            arguments["build_type"] == "Release" and not arguments["otp"] and
            arguments["bl2"] and arguments["ns"] and
            arguments["profile"] == "N.A" and arguments["partition_ps"]):
                name_config = "CoreIPC"
        elif (not arguments["psa"] and arguments["isolation_level"] == "1" and
            not arguments["regression"] and not arguments["psa_test"]      and
            arguments["build_type"] == "Release" and not arguments["otp"]  and
            arguments["bl2"] and arguments["ns"] and
            arguments["profile"] == "N.A" and arguments["partition_ps"]):
                name_config = "Default"
        elif (arguments["psa"] and arguments["isolation_level"] == "2"    and
            not arguments["regression"] and not arguments["psa_test"]     and
            arguments["build_type"] == "Release" and not arguments["otp"] and
            arguments["bl2"] and arguments["ns"] and
            arguments["profile"] == "N.A" and arguments["partition_ps"]):
                name_config = "CoreIPCTfmLevel2"
        elif (not arguments["psa"] and arguments["isolation_level"] == "1" and
            not arguments["regression"] and not arguments["psa_test"]      and
            arguments["build_type"] == "Release" and not arguments["otp"]  and
            arguments["bl2"] and arguments["ns"] and
            arguments["profile"] == "SMALL" and arguments["partition_ps"]):
                name_config = "DefaultProfileS"
        elif (not arguments["psa"] and arguments["isolation_level"] == "2" and
            not arguments["regression"] and not arguments["psa_test"]      and
            arguments["build_type"] == "Release" and not arguments["otp"]  and
            arguments["bl2"] and arguments["ns"] and
            arguments["profile"] == "MEDIUM" and arguments["partition_ps"]):
                name_config = "DefaultProfileM"
        ret = [arguments["platform"],arguments["toolchain"], name_config]
    except:
        ret = ["Unknown", "Unknown", "Unknown"]
    return ret

# Function based on get_local_git_info() from utils, getting change id for the tfm repo
def get_change_id(directory):
    directory = os.path.abspath(directory)
    cur_dir = os.path.abspath(os.getcwd())
    os.chdir(directory) # Going to the repo's directory
    cmd = "git log HEAD -n 1  --pretty=format:'%b'"

    git_info_rex = re.compile(r'(?P<body>^[\s\S]*?)((?:Change-Id:\s)'
                              r'(?P<change_id>.*)\n?)', re.MULTILINE)

    r, e = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE).communicate()
    if e:
        print("Error", e)
        return
    else:
        try:
            txt_body = r.decode('ascii')
        except UnicodeDecodeError as E:
            txt_body = r.decode('utf-8')
        result = txt_body.rstrip()

    change_id = git_info_rex.search(result).groupdict()["change_id"].strip()
    os.chdir(cur_dir) #Going back to the initial directory
    return change_id

if __name__ == "__main__":
    for i in range(len(REFERENCE_CONFIGS)):
        REFERENCE_CONFIGS[i] = REFERENCE_CONFIGS[i].strip().lower()
    config = identify_config(CI_CONFIG)
    if (config[2].lower() in REFERENCE_CONFIGS
        and config[0] == "mps2/an521"
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
