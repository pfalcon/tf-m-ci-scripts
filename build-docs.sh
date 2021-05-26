#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2020-2021, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

#
# Used for CI to build the docs.
# Expected to have trusted-firmware-m cloned to same level as this git tree
#

set -ex

cd mbedtls
git apply ../trusted-firmware-m/lib/ext/mbedcrypto/*.patch

mkdir ../trusted-firmware-m/build
cd ../trusted-firmware-m/build

cmake -S .. -B . -DTFM_PLATFORM=arm/mps2/an521 \
                 -DTFM_TOOLCHAIN_FILE=../toolchain_GNUARM.cmake \
                 -DMBEDCRYPTO_PATH=../../mbedtls \
                 -DTFM_TEST_REPO_PATH=../../tf-m-tests \
                 -DMCUBOOT_PATH=../../mcuboot
cmake --build ./ -- tfm_docs_refman_html
cmake --build ./ -- tfm_docs_userguide_html
