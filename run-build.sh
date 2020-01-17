#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2020, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

#
# Builds a single configuration on Trusted Firmware M.
# Relies on environment variables pre-populated.
# These variables can be obtained using configs.py.
# Expected to have trusted-firmware-m cloned to same level as this git tree
#

set -ex
mkdir trusted-firmware-m/build
cd trusted-firmware-m/build
cmake -G "Unix Makefiles" -DPROJ_CONFIG=`readlink -f ../configs/$PROJ_CONFIG.cmake` -DTARGET_PLATFORM=$TARGET_PLATFORM -DCOMPILER=$COMPILER -DCMAKE_BUILD_TYPE=$CMAKE_BUILD_TYPE -DBL2=$BL2 ..
cmake --build ./ -- -j 2 install
if [ "$TARGET_PLATFORM" == "MUSCA_A" ] ; then
  export OFFSET1=0x200000
  export OFFSET2=0x220000
elif [ "$TARGET_PLATFORM" == "MUSCA_B1" ] ; then
  export OFFSET1=0xA000000
  export OFFSET2=0xA020000
fi
if [ ! -z "$OFFSET1" ] && [ ! -z "$OFFSET2" ] ; then
  # Cleanup offset(s)?
  srec_cat install/outputs/$TARGET_PLATFORM/mcuboot.bin -Binary -offset $OFFSET1 install/outputs/$TARGET_PLATFORM/tfm_sign.bin -Binary -offset $OFFSET2 -o install/outputs/$TARGET_PLATFORM/tfm.hex -Intel
fi
