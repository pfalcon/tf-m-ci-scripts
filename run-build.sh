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
    TFM_EXTRAS_REFSPEC="$(get_cmake_cache ${WORKSPACE}/ci_build TFM_EXTRAS_REPO_VERSION)"

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
spe_cmake_config_cmd=$(python3 tf-m-ci-scripts/configs.py -b spe_cmake_config $CONFIG_NAME)
spe_cmake_build_cmd=$(python3 tf-m-ci-scripts/configs.py -b spe_cmake_build -j ${BUILD_JOBS:-2} $CONFIG_NAME)
nspe_cmake_config_cmd=$(python3 tf-m-ci-scripts/configs.py -b nspe_cmake_config $CONFIG_NAME)
nspe_cmake_build_cmd=$(python3 tf-m-ci-scripts/configs.py -b nspe_cmake_build -j ${BUILD_JOBS:-2} $CONFIG_NAME)
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
    spe_cmake_config_cmd=${spe_cmake_config_cmd/-- install/-- $BUILD_TARGET}
    echo "Warning: BUILD_TARGET is set, will not run post_build_cmd"
    post_build_cmd=""
fi

if [ "$CODE_COVERAGE_EN" = "TRUE" ] && [[ $CONFIG_NAME =~ "GCC" ]] ; then
    spe_cmake_config_cmd=${spe_cmake_config_cmd/toolchain_GNUARM.cmake/toolchain_GNUARM.cmake -DTFM_CODE_COVERAGE=True}
    echo "Flag: Add compiler flag for build with code coverage supported."
    echo $cmake_config_cmd
fi

if [ -z "$spe_cmake_config_cmd" ] ; then
    echo "No CMake config command found."
    exit 1
fi

if [ -z "$spe_cmake_build_cmd" ] ; then
    echo "No CMake build command found."
    exit 1
fi

cnt=$(ls trusted-firmware-m/lib/ext/mbedcrypto/*.patch 2> /dev/null | wc -l)
if [ "$cnt" != "0" ] ; then
    cd mbedtls
    git apply ../trusted-firmware-m/lib/ext/mbedcrypto/*.patch
    cd -
fi

cnt=$(ls tf-m-tests/tests_psa_arch/fetch_repo/*.patch 2> /dev/null | wc -l)
if [ "$cnt" != "0" ] ; then
    cd psa-arch-tests
    git apply ../tf-m-tests/tests_psa_arch/fetch_repo/*.patch
    cd -
fi

cd trusted-firmware-m
git apply ../tf-m-ci-scripts/build_helper/platform_settings/*.patch
cd -

rm -rf ci_build
mkdir ci_build
cd ci_build

set +e
eval $spe_cmake_config_cmd
cmake_cfg_error=$?
set -e

check_dependency_version

if [ "$spe_cmake_config_cmd" != 0 ] ; then
    rm -rf ci_build/*
    eval $spe_cmake_config_cmd
fi

eval "$spe_cmake_build_cmd; $nspe_cmake_config_cmd; $nspe_cmake_build_cmd; $post_build_cmd"
