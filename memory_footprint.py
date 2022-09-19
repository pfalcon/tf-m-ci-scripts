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

# SQAUD constant
SQUAD_TOKEN            = sys.argv[1]
SQUAD_BASE_PROJECT_URL = ("https://qa-reports.linaro.org/api/submit/tf/tf-m/")

reference_configs = [
    # build type, profile
    ["Release",    "profile_small"],
    ["Minsizerel", "profile_small"],
    ["Release",    "profile_medium"],
    ["Release",    "profile_large"],
]

# This function uses arm_non_eabi_size to get the sizes of a file
#  in the build directory of tfm
def get_file_size(filename):
    f_path = os.path.join(os.getenv('WORKSPACE'), "trusted-firmware-m", "build", "bin", filename)
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

def is_reference_config() -> bool:
    # Only push data for AN521 built with GCC
    if (os.getenv('TFM_PLATFORM') != 'arm/mps2/an521'
        or os.getenv('COMPILER') != 'GCC_10_3'
        or os.getenv('TEST_REGRESSION') == "True"):
        return False

    configs = [os.getenv('CMAKE_BUILD_TYPE'), os.getenv('PROFILE')]
    if configs in reference_configs:
        return True

    return False

def print_image_sizes(image_sizes):
    for sec, size in image_sizes.items():
        print("{:4}: {}".format(sec, size))

if __name__ == "__main__":
    # Export GCC v10.3 to ENV PATH
    os.environ["PATH"] += os.pathsep + os.getenv('GCC_10_3_PATH')
    if is_reference_config():
        print("Configuration " + os.getenv('CONFIG_NAME') + " is a reference")
        try :
            change_id = get_change_id("trusted-firmware-m")
        except :
            change_id = -1

        bl2_sizes = get_file_size("bl2.axf")
        print("------ BL2 Memory Footprint ------")
        print_image_sizes(bl2_sizes)
        tfms_sizes = get_file_size("tfm_s.axf")
        print("------ TFM Secure Memory Footprint ------")
        print_image_sizes(tfms_sizes)

        if (bl2_sizes != -1 and change_id != -1) :
            squad_config_name = os.getenv('CMAKE_BUILD_TYPE') + os.getenv('PROFILE')
            send_file_size(change_id, squad_config_name, bl2_sizes, tfms_sizes)
        else :
            #Directory or file weren't found
            if change_id == -1 :
                print("Error : trusted-firmware-m repo not found")
            else :
                print("Error : file not found")
