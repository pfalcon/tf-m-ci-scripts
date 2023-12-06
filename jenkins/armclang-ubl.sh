#!/bin/bash
#
# Copyright (c) 2019, Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Script to activate ArmClang UBL license.

set -ex

varname=${COMPILER}_PATH
eval COMP_PATH=\$$varname

success=0
delay=5
for i in $(seq 1 3); do
    if ${COMP_PATH}/armlm activate --code ${ARMCLANG_UBL_CODE}; then
        success=1
        break
    fi
    sleep ${delay}
    delay=$((${delay} * 2))
done

if [ ${success} -eq 0 ]; then
    ls -l ~/.armlm/logs/*.log
    cat ~/.armlm/logs/*.log
    exit 1
fi

${COMP_PATH}/armlm inspect
