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

if [ -z "$CONFIG_NAME" ] ; then
	echo "Set CONFIG_NAME to run a build."
	exit 1
fi

build_commands=$(python3 tf-m-ci-scripts/configs.py -b -g all $CONFIG_NAME)

if [ -z "$build_commands" ] ; then
	echo "No build commands found."
	exit 1
fi

mkdir trusted-firmware-m/build
cd trusted-firmware-m/build

eval "set -ex ; $build_commands"
