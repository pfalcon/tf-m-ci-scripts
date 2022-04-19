#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2022, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

set -ex

input_folder=cfgs
output_coverage_file=merge.info
output_json_file=merge.json

python3 $SHARE_FOLDER/qa-tools/coverage-tool/coverage-reporting/merge.py \
      $(find $input_folder -name "*.info" -exec echo "-a {}" \;) \
      -o $output_coverage_file \

genhtml --branch-coverage $output_coverage_file \
    --output-directory merged_report
