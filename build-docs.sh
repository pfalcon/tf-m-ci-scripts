#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2020-2022, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

#
# Used for CI to build the docs.
# Expected to have trusted-firmware-m cloned to same level as this git tree
#

set -ex

export PATH=$PATH:$GCC_10_3_PATH

mkdir -p ${WORKSPACE}/trusted-firmware-m/build/docs
cd ${WORKSPACE}/trusted-firmware-m/build/docs

cmake -S ${WORKSPACE}/trusted-firmware-m/docs -B .
cmake --build ./ -- tfm_docs_refman_html
cmake --build ./ -- tfm_docs_userguide_html
