#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2020, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

#
# Used for CI to build the docs.
# Expected to have trusted-firmware-m cloned to same level as this git tree
#

set -ex
mkdir trusted-firmware-m/build
cd trusted-firmware-m/build
cmake ../ -G"Unix Makefiles" -DTARGET_PLATFORM=AN521 -DCOMPILER=GNUARM
cmake --build ./ -- install_doc
cmake --build ./ -- install_userguide
