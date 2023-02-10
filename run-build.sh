#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2020-2023, Arm Limited and Contributors. All rights reserved.
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

. $(dirname $0)/util_cmake.sh
. $(dirname $0)/util_git.sh

# For dependency that differs from platforms, the versions need to be checkded
# in each single build job.
function check_dependency_version() {
    TFM_EXTRAS_PATH="${WORKSPACE}/tf-m-extras"
    TFM_EXTRAS_REFSPEC="$(get_cmake_cache ${WORKSPACE}/trusted-firmware-m/build TFM_EXTRAS_REPO_VERSION)"

    # Array containing "<repo path>;<refspec>" elements
    dependency_repos=(
        "${TFM_EXTRAS_PATH};${TFM_EXTRAS_REFSPEC}"
    )

    for repo in ${dependency_repos[@]}; do
        # Parse the repo elements
        REPO_PATH="$(echo "${repo}" | awk -F ';' '{print $1}')"
        REPO_REFSPEC="$(echo "${repo}" | awk -F ';' '{print $2}')"

        if [ ! -z "$REPO_REFSPEC" ] ; then
            git_checkout $REPO_PATH $REPO_REFSPEC
        fi
    done
}

set -ex

if [ -z "$CONFIG_NAME" ] ; then
    echo "Set CONFIG_NAME to run a build."
    exit 1
fi

set_compiler_cmd=$(python3 tf-m-ci-scripts/configs.py -b set_compiler $CONFIG_NAME)
cmake_config_cmd=$(python3 tf-m-ci-scripts/configs.py -b cmake_config $CONFIG_NAME)
cmake_build_cmd=$(python3 tf-m-ci-scripts/configs.py -b cmake_build -j ${BUILD_JOBS:-2} $CONFIG_NAME)
post_build_cmd=$(python3 tf-m-ci-scripts/configs.py -b post_build $CONFIG_NAME)

set +e
echo "output current build environment"
cat /etc/issue
uname -a
grep -c ^processor /proc/cpuinfo
cmake --version
python --version
make --version

set -ex
eval $set_compiler_cmd

if [ -n "$BUILD_TARGET" ]; then
    cmake_build_cmd=$(echo "$cmake_build_cmd" | head -4)
    cmake_build_cmd=${cmake_build_cmd/-- install/-- $BUILD_TARGET}
fi

if [ $CODE_COVERAGE_EN = "TRUE" ] && [[ $CONFIG_NAME =~ "GCC" ]] ; then
    cmake_config_cmd=${cmake_config_cmd/toolchain_GNUARM.cmake/toolchain_GNUARM.cmake -DTFM_CODE_COVERAGE=True}
    echo "Flag: Add compiler flag for build with code coverage supported."
    echo $cmake_config_cmd
fi

if [ -z "$cmake_config_cmd" ] ; then
    echo "No CMake config command found."
    exit 1
fi

if [ -z "$cmake_build_cmd" ] ; then
    echo "No CMake build command found."
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

cd trusted-firmware-m
git apply ../tf-m-ci-scripts/build_helper/platform_settings/*.patch
cd -

rm -rf trusted-firmware-m/build
mkdir trusted-firmware-m/build
cd trusted-firmware-m/build

set +e
eval $cmake_config_cmd
cmake_cfg_error=$?
set -e

check_dependency_version

if [ $cmake_cfg_error != 0 ] ; then
    rm -rf trusted-firmware-m/build/*
    eval $cmake_config_cmd
fi

eval "$cmake_build_cmd; $post_build_cmd"
