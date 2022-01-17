#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2020-2022, Arm Limited and Contributors. All rights reserved.
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

set +e
echo "output current build environment"
cat /etc/issue
uname -a
grep -c ^processor /proc/cpuinfo
cmake --version
python --version
make --version

# Export specific compiler path to env PATH
compiler_path="${COMPILER_VERSION}_PATH"
export PATH=$PATH:"${!compiler_path}"
# Show compiler version
if [[ $COMPILER_VERSION =~ "ARMCLANG" ]] ; then
    armclang --version
else
    arm-none-eabi-gcc --version
fi

set -ex
build_commands=$(python3 tf-m-ci-scripts/configs.py -b -g all $CONFIG_NAME)

if [ $CODE_COVERAGE_EN = "TRUE" ] && [[ $CONFIG_NAME =~ "GNUARM" ]] ; then
    build_commands=${build_commands/toolchain_GNUARM.cmake/toolchain_GNUARM.cmake -DTFM_CODE_COVERAGE=True}
    echo "Flag: Add compiler flag for build with code coverage supported."
    echo $build_commands
fi

if [ -z "$build_commands" ] ; then
	echo "No build commands found."
	exit 1
fi

cnt=$(ls trusted-firmware-m/lib/ext/mbedcrypto/*.patch 2> /dev/null | wc -l)
if [ "$cnt" != "0" ] ; then
	cd mbedtls
	git apply ../trusted-firmware-m/lib/ext/mbedcrypto/*.patch
	cd -
fi

cnt=$(ls trusted-firmware-m/lib/ext/psa_arch_tests/*.patch 2> /dev/null | wc -l)
if [ "$cnt" != "0" ] ; then
	cd psa-arch-tests
	git apply ../trusted-firmware-m/lib/ext/psa_arch_tests/*.patch
	cd -
fi

psa_qcbor_link="https://github.com/laurencelundblade/QCBOR.git"
psa_qcbor_path="$(pwd)/psa_qcbor"
psa_qcbor_cfg_cmake="psa-arch-tests/api-tests/tools/cmake/common/CMakeExternal.cmake"
sed -i "s#$psa_qcbor_link#$psa_qcbor_path#g" $psa_qcbor_cfg_cmake

rm -rf trusted-firmware-m/build
mkdir trusted-firmware-m/build
cd trusted-firmware-m/build

eval "set -ex ; $build_commands"
