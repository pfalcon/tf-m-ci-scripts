#!/usr/bin/env bash
#
# Copyright (c) 2021 Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Clones and checkout TF-M related repositories in case these are not present
# under SHARE_FOLDER, otherwise copy the share repositories into current folder
# (workspace)

#
# The way it works is simple: the top level job sets the SHARE_FOLDER
# parameter based on its name and number on top of the share
# volume (/srv/shared/<job name>/<job number>) then it calls the clone
# script (clone.sh), which in turn it fetches the repositories mentioned
# above. Jobs triggered on behalf of the latter, share the same
# SHARE_FOLDER value, and these in turn also call the clone script, but
# in this case, the script detects that the folder is already populated so
# its role is to simply copy the repositories into the job's
# workspace. As seen, all jobs work with repositories on their own
# workspace, which are just copies of the share folder, so there is no
# change of a race condition, i.e every job works with its own copy. The
# worst case scenario is where the down-level job,
# i.e. tf-m-build-config, uses its default SHARE_FOLDER value, in this
# case, it would simply clone its own repositories without reusing any
# file however the current approach prevents the latter unless the job
# is triggered manually from the buider job itself.
#

# Global defaults
GIT_CLONE_PARAMS="--no-checkout"

# Must projects
TFM_PROJECT="${CODE_REPO:?}"
TFM_REFSPEC="${GERRIT_REFSPEC:?}"
TFM_NAME="trusted-firmware-m"

SCRIPTS_PROJECT="${CI_SCRIPTS_REPO:?}"
SCRIPTS_REFSPEC="${CI_SCRIPTS_BRANCH:?}"
SCRIPTS_NAME="tf-m-ci-scripts"

# Optional projects
TFM_TESTS_PROJECT="${TFM_TESTS_URL:-}"
TFM_TESTS_REFSPEC="${TFM_TESTS_REFSPEC:-}"
TFM_TESTS_NAME="tf-m-tests"

MBEDTLS_PROJECT="${MBEDTLS_URL:-}"
MBEDTLS_REFSPEC="${MBEDTLS_VERSION:-}"
MBEDTLS_NAME="mbedtls"

MCUBOOT_PROJECT="${MCUBOOT_URL:-}"
MCUBOOT_REFSPEC="${MCUBOOT_REFSPEC:-}"
MCUBOOT_NAME="mcuboot"

PSA_ARCH_TESTS_PROJECT="${PSA_ARCH_TESTS_URL:-}"
PSA_ARCH_TESTS_REFSPEC="${PSA_ARCH_TESTS_VERSION:-}"
PSA_ARCH_TESTS_NAME="psa-arch-tests"

# Array containing "<repo url>;"<repo name>;<refspec>" elements
repos=(
    "${TFM_PROJECT};${TFM_NAME};${TFM_REFSPEC}"
    "${TFM_TESTS_PROJECT};${TFM_TESTS_NAME};${TFM_TESTS_REFSPEC}"
    "${SCRIPTS_PROJECT};${SCRIPTS_NAME};${SCRIPTS_REFSPEC}"
    "${MBEDTLS_PROJECT};${MBEDTLS_NAME};${MBEDTLS_REFSPEC}"
    "${MCUBOOT_PROJECT};${MCUBOOT_NAME};${MCUBOOT_REFSPEC}"
    "${PSA_ARCH_TESTS_PROJECT};${PSA_ARCH_TESTS_NAME};${PSA_ARCH_TESTS_REFSPEC}"
)

# Take into consideration non-CI runs where SHARE_FOLDER variable
# may not be present
if [ -z "${SHARE_FOLDER}" ]; then
    # Default Jenkins values
    SHARE_VOLUME="${SHARE_VOLUME:-$PWD}"
    JOB_NAME="${JOB_NAME:-local}"
    BUILD_NUMBER="${BUILD_NUMBER:-0}"
    SHARE_FOLDER=${SHARE_VOLUME}/${JOB_NAME}/${BUILD_NUMBER}
fi

echo "Share Folder ${SHARE_FOLDER}"

# clone git repos
for repo in ${repos[@]}; do

    # parse the repo elements
    REPO_URL="$(echo "${repo}" | awk -F ';' '{print $1}')"
    REPO_NAME="$(echo "${repo}" | awk -F ';' '{print $2}')"
    REPO_REFSPEC="$(echo "${repo}" | awk -F ';' '{print $3}')"

    # in case repository is not define, just skip it
    if [ -z "${REPO_URL}" ]; then
        continue
    fi

    # clone and checkout in case it does not exit
    if [ ! -d ${SHARE_FOLDER}/${REPO_NAME} ]; then
        git clone --quiet ${GIT_CLONE_PARAMS} ${REPO_URL} ${SHARE_FOLDER}/${REPO_NAME}

        # fetch and checkout the corresponding refspec
        cd ${SHARE_FOLDER}/${REPO_NAME}

        git fetch ${REPO_URL} ${REPO_REFSPEC} && git checkout FETCH_HEAD
        echo -e "\n\nShare Folder ${SHARE_FOLDER}/${REPO_NAME} $(git rev-parse --short HEAD)\n\n"
        cd $OLDPWD

    else
        # otherwise just show the head's log
        cd ${SHARE_FOLDER}/${REPO_NAME}
        echo -e "\n\nShare Folder ${SHARE_FOLDER}/${REPO_NAME} $(git rev-parse --short HEAD)\n\n"
        cd $OLDPWD
    fi

    # copy repository into pwd dir (workspace in CI), so each job would work
    # on its own workspace
    cp -a -f ${SHARE_FOLDER}/${REPO_NAME} ${WORKSPACE}/${REPO_NAME}

done
