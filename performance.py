#!/usr/bin/env python3

__copyright__ = '''
/*
 * Copyright (c) 2020-2023, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 '''

import argparse
import os
import json
import logging
import re
import requests
from tfm_ci_pylib import utils

mem_configs = {
    'AN521_ARMCLANG_1_Minsizerel_BL2':              'MEMORY-AN521-ARMCC-Default-Minsizerel',
    'AN521_ARMCLANG_1_Minsizerel_BL2_SMALL_PSOFF':  'MEMORY-AN521-ARMCC-Small-Minsizerel',
    'AN521_ARMCLANG_2_Minsizerel_BL2_MEDIUM_PSOFF': 'MEMORY-AN521-ARMCC-Medium-Minsizerel',
    'AN521_ARMCLANG_3_Minsizerel_BL2_LARGE_PSOFF':  'MEMORY-AN521-ARMCC-Large-Minsizerel'
}

profiling_configs = {
    'AN521_GCC_1_Release_BL2_PROF':     'PERF-AN521-GCC-Level1-SFN-Release',
    'AN521_GCC_1_Release_BL2_IPC_PROF': 'PERF-AN521-GCC-Level1-IPC-Release',
    'AN521_GCC_2_Release_BL2_PROF':     'PERF-AN521-GCC-Level2-IPC-Release',
    'AN521_GCC_3_Release_BL2_PROF':     'PERF-AN521-GCC-Level3-IPC-Release'
}

def get_git_commit_hash(repo='trusted-firmware-m'):
    cur_dir = os.path.abspath(os.getcwd())

    os.chdir(os.path.join(os.getenv('WORKSPACE'), repo)) # Going to the repo's directory
    git_commit = os.popen('git rev-parse --short HEAD').read()[:-1]
    os.chdir(cur_dir) # Going back to the initial directory

    return git_commit

def get_file_size(filename):
    '''
    This function uses fromelf of ARMCLANG to get the sizes of a file in the build binary directory of TF-M
    '''
    f_path = os.path.join(os.getenv('WORKSPACE'), 'trusted-firmware-m', 'build', 'bin', filename)
    if os.path.exists(f_path) :
        data_fromelf = utils.fromelf(f_path)
        print(data_fromelf[1])  # Output of fromelf
        return data_fromelf[0]  # Data parsed from output of fromelf
    else :
        print(f_path + 'Not found')
        return -1

def save_mem_to_json(config_name, bl2_sizes, tfm_s_sizes):
    '''
    This function creates a json file containing all the data about memory footprint in share folder.
    '''
    try:
        metrics = json.dumps({ 'bl2_code_size'    : bl2_sizes['Code'],
                               'bl2_inline_data'  : bl2_sizes['Inline Data'],
                               'bl2_ro_data'      : bl2_sizes['RO Data'],
                               'bl2_rw_data'      : bl2_sizes['RW Data'],
                               'bl2_zi_data'      : bl2_sizes['ZI Data'],
                               'spe_code_size'    : tfm_s_sizes['Code'],
                               'spe_inline_data'  : tfm_s_sizes['Inline Data'],
                               'spe_ro_data'      : tfm_s_sizes['RO Data'],
                               'spe_rw_data'      : tfm_s_sizes['RW Data'],
                               'spe_zi_data'      : tfm_s_sizes['ZI Data']})
    except:
        return -1

    with open(os.path.join(os.getenv('SHARE_FOLDER'),
                           'Memory_footprint',
                           '{}_filesize.json'.format(config_name)), 'w') as F:
        #Storing the json file
        F.write(metrics)
    return 0

def get_prof_psa_client_api_data(f_log_path):
    '''
    Get PSA Client API profiling data report from target log.
    '''

    prof_data = {}
    with open(f_log_path,'r') as f_log:
        tfm_log = f_log.read()

        # Extract TF-M PSA Client API profiling data
        pattern = r'(secure|non-secure) ([^\n]+) average is (\d+) CPU cycles'
        matches = re.findall(pattern, tfm_log)
        for match in matches:
            type, api, cpu_cycles = match
            prof_data[('s_' if type == 'secure' else 'ns_') + api.replace(' ', '_')] = cpu_cycles

    return prof_data


def send_squad(user_args, job_dir, config_name):
    '''
    Send performance data to SQUAD dashboard.
    '''
    prof_data, mem_data = {}, {}

    # Generate Profiling data from target log
    if config_name in profiling_configs.keys():
        target_log = os.path.join(job_dir, 'target_log.txt')
        prof_data = get_prof_psa_client_api_data(target_log)
        config_name = profiling_configs[config_name]

    # Load Memory Footprint data from share folder json files.
    if config_name in mem_configs.keys():
        mem_json_path = os.path.join(os.getenv('SHARE_FOLDER'), 'Memory_footprint', '{}_filesize.json'.format(config_name))
        with open(mem_json_path, 'r') as f:
            mem_data = json.load(f)
        config_name = mem_configs[config_name]

    # Write result to JSON file
    metrics = json.dumps({**prof_data, **mem_data})
    with open(os.path.join(job_dir, 'performance.json'), 'w') as f_json:
        f_json.write(metrics)

    # SQAUD constant
    SQUAD_TOKEN = user_args.squad_token
    SQUAD_BASE_PROJECT_URL = ('https://qa-reports.linaro.org/api/submit/tf/tf-m/')
    url = SQUAD_BASE_PROJECT_URL + get_git_commit_hash('trusted-firmware-m') + '/' + config_name
    headers = {'Auth-Token': SQUAD_TOKEN}
    data= {'metrics': metrics}

    # Sending the data to SQUAD, 40s timeout
    try:
        result = requests.post(url, headers=headers, data=data, timeout=40)
    except:
        return -1

    if not result.ok:
        print(f'Error submitting to qa-reports: {result.reason}: {result.text}')
        return -1
    else :
        print ('POST request sent to project ' + config_name)
        return 0

def main(user_args):
    if user_args.generate_memory:
        # Export ARMClang v6.13 to ENV PATH
        os.environ['PATH'] += os.pathsep + os.getenv('ARMCLANG_6_13_PATH')
        if os.getenv('CONFIG_NAME') in mem_configs.keys():
            print('Configuration ' + os.getenv('CONFIG_NAME') + ' is a reference')

            print('---------- BL2 Memory Footprint ----------')
            bl2_sizes = get_file_size('bl2.axf')

            print('------ TF-M Secure Memory Footprint ------')
            tfm_s_sizes = get_file_size('tfm_s.axf')

            if save_mem_to_json(os.getenv('CONFIG_NAME'), bl2_sizes, tfm_s_sizes) == -1:
                print('Memory footprint generate failed.')

    if user_args.send_squad:
        with open(os.path.join(os.getenv('SHARE_FOLDER'), 'performance_config.txt'), 'r') as f:
            for line in f:
                config_name, job_dir = line.split()[0], line.split()[1]
                send_squad(user_args, job_dir, config_name)

def get_cmd_args():
    parser = argparse.ArgumentParser(description='Performance')
    cmdargs = parser.add_argument_group('Performance')

    # Configuration control
    cmdargs.add_argument(
        '--generate-memory', dest='generate_memory', action='store_true', default=False, help='Generate memory footprint data'
    )
    cmdargs.add_argument(
        '--send-squad', dest='send_squad', action='store_true', default=False, help='Send data to SQUAD'
    )
    cmdargs.add_argument(
        '--squad-token', dest='squad_token', action='store', help='SQUAD BOARD TOKEN'
    )

    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(get_cmd_args())
