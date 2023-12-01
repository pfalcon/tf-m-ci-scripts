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

${COMP_PATH}/armlm activate --code ${ARMCLANG_UBL_CODE}
${COMP_PATH}/armlm inspect
