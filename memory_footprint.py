#!/usr/bin/env python

#memory_footprint.py : Script for sending memory footprint data from the TFM CI
#to a SQUAD web interface
#
#Copyright (c) 2020-2022, Arm Limited. All rights reserved.
#
#SPDX-License-Identifier: BSD-3-Clause


import os
import re
import sys
import json
import requests
import subprocess
from tfm_ci_pylib import utils

# SQAUD constant
SQUAD_TOKEN            = sys.argv[1]
SQUAD_BASE_PROJECT_URL = ("https://qa-reports.linaro.org/api/submit/tf/tf-m/")

reference_configs = [
    'AN521_ARMCLANG_1_Minsizerel_BL2',
    'AN521_ARMCLANG_1_Minsizerel_BL2_SMALL_PSOFF',
    'AN521_ARMCLANG_2_Minsizerel_BL2_MEDIUM_PSOFF',
    'AN521_ARMCLANG_3_Minsizerel_BL2_LARGE_PSOFF'
]

# This function uses arm_non_eabi_size to get the sizes of a file
#  in the build directory of tfm
def get_file_size(filename):
    f_path = os.path.join(os.getenv('WORKSPACE'), "trusted-firmware-m", "build", "bin", filename)
    if os.path.exists(f_path) :
        data_fromelf = utils.fromelf(f_path)
        print(data_fromelf[1])  # Output of fromelf
        return data_fromelf[0]  # Data parsed from output of fromelf
    else :
        print(f_path + "Not found")
        return -1

# This function creates a json file containing all the data about
#  memory footprint and sends this data to SQUAD
def send_file_size(change_id, config_name, bl2_sizes, tfms_sizes):
    url = SQUAD_BASE_PROJECT_URL + change_id + '/' + config_name

    try:
        metrics = json.dumps({ "bl2_code_size"    : bl2_sizes["Code"],
                               "bl2_inline_data"  : bl2_sizes["Inline Data"],
                               "bl2_ro_data"      : bl2_sizes["RO Data"],
                               "bl2_rw_data"      : bl2_sizes["RW Data"],
                               "bl2_zi_data"      : bl2_sizes["ZI Data"],
                               "tfms_code_size"   : tfms_sizes["Code"],
                               "tfms_inline_data" : tfms_sizes["Inline Data"],
                               "tfms_ro_data"     : tfms_sizes["RO Data"],
                               "tfms_rw_data"     : tfms_sizes["RW Data"],
                               "tfms_zi_data"     : tfms_sizes["ZI Data"]})
    except:
        return -1

    headers = {"Auth-Token": SQUAD_TOKEN}
    data= {"metrics": metrics}

    try:
        #Sending the data to SQUAD, 40s timeout
        result = requests.post(url, headers=headers, data=data, timeout=40)
    except:
        return -1

    with open(os.path.join(os.getenv('WORKSPACE'),
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

# Function based on get_local_git_info() from utils, getting change id for the tfm repo
def get_change_id(repo='trusted-firmware-m'):
    directory = os.path.join(os.getenv('WORKSPACE'), repo)
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

def print_image_sizes(image_sizes):
    for sec, size in image_sizes.items():
        print("{:4}: {}".format(sec, size))

if __name__ == "__main__":
    # Export ARMClang v6.13 to ENV PATH
    os.environ["PATH"] += os.pathsep + os.getenv('ARMCLANG_6_13_PATH')
    if os.getenv('CONFIG_NAME') in reference_configs:
        print("Configuration " + os.getenv('CONFIG_NAME') + " is a reference")
        try :
            change_id = get_change_id("trusted-firmware-m")
        except :
            change_id = -1

        print("------ BL2 Memory Footprint ------")
        bl2_sizes = get_file_size("bl2.axf")
        print("\n\n------ TFM Secure Memory Footprint ------")
        tfms_sizes = get_file_size("tfm_s.axf")

        if (bl2_sizes != -1 and change_id != -1) :
            squad_config_name = os.getenv('CONFIG_NAME')
            send_file_size(change_id, squad_config_name, bl2_sizes, tfms_sizes)
        else :
            #Directory or file weren't found
            if change_id == -1 :
                print("Error : trusted-firmware-m repo not found")
            else :
                print("Error : file not found")
