#!/usr/bin/env bash
#
# Copyright (c) 2021-2023 Arm Limited. All rights reserved.
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

set -ex

. $(dirname $0)/utils/util_git.sh
. $(dirname $0)/utils/util_parse_version.sh

function clone_repo_to_share_folder() {
    REPO_URL=$1
    REPO_NAME=$2
    REPO_REFSPEC=$3

    echo "Repo: $REPO_URL $REPO_NAME $REPO_REFSPEC"

    # In case repository is not defined, just skip it
    if [ -z "${REPO_URL}" ]; then
        echo "Repo ${REPO_NAME} not needed in this job. Skip download."
        return 0
    fi

    if [ ! -d "${SHARE_FOLDER}/${REPO_NAME}" ]; then
        git_clone $REPO_URL "${SHARE_FOLDER}/${REPO_NAME}"
        git_checkout "${SHARE_FOLDER}/${REPO_NAME}" $REPO_REFSPEC
    else
        cd "${SHARE_FOLDER}/${REPO_NAME}"
        echo -e "Share Folder ${REPO_NAME} $(git rev-parse --short HEAD)\n"
        cd $OLDPWD
    fi

    # Copy repos into pwd dir (workspace in CI), so each job would work
    # on its own workspace
    cp -a -f "${SHARE_FOLDER}/${REPO_NAME}" "${WORKSPACE}/${REPO_NAME}"
}

# Take into consideration non-CI runs where SHARE_FOLDER variable
# may not be present
if [ -z "${SHARE_FOLDER}" ]; then
    # Default Jenkins values
    SHARE_VOLUME="${SHARE_VOLUME:-$PWD}"
    JOB_NAME="${JOB_NAME:-local}"
    BUILD_NUMBER="${BUILD_NUMBER:-0}"
    SHARE_FOLDER=${SHARE_VOLUME}/${JOB_NAME}/${BUILD_NUMBER}
fi

echo "Share Folder path: ${SHARE_FOLDER}"
echo

# TF-M project
if [ -n "${GERRIT_EVENT_HASH}" ]; then
    # If triggered by Gerrit, use its variables
    TFM_PROJECT="https://${GERRIT_HOST}/${GERRIT_PROJECT}"
else
    TFM_PROJECT="${CODE_REPO:?}"
fi
TFM_REFSPEC="${GERRIT_REFSPEC:?}"
TFM_NAME="trusted-firmware-m"

clone_repo_to_share_folder "${TFM_PROJECT}" "${TFM_NAME}" "${TFM_REFSPEC}"
if [ ! -d "${SHARE_FOLDER}/${TFM_NAME}" ]; then
    echo "Fatal error: ${TFM_NAME} not downloaded!"
    exit 1
fi

# Dependency projects
TFM_TESTS_PROJECT="${TFM_TESTS_URL:-}"
TFM_TESTS_REFSPEC="${TFM_TESTS_REFSPEC:-"$(parse_version lib/ext/tf-m-tests/version.txt version= = 2)"}"
TFM_TESTS_NAME="tf-m-tests"

MBEDTLS_PROJECT="${MBEDTLS_URL:-}"
MBEDTLS_REFSPEC="${MBEDTLS_VERSION:-"$(parse_version config/config_base.cmake set\(MBEDCRYPTO_VERSION \" 2)"}"
MBEDTLS_NAME="mbedtls"

MCUBOOT_PROJECT="${MCUBOOT_URL:-}"
MCUBOOT_REFSPEC="${MCUBOOT_REFSPEC:-"$(parse_version config/config_base.cmake set\(MCUBOOT_VERSION \" 2)"}"
MCUBOOT_NAME="mcuboot"

QCBOR_PROJECT="${QCBOR_URL:-}"
QCBOR_REFSPEC="${QCBOR_VERSION:-"$(parse_version lib/ext/qcbor/CMakeLists.txt set\(QCBOR_VERSION \" 2)"}"
QCBOR_NAME="qcbor"

TFM_EXTRAS_PROJECT="${TFM_EXTRAS_URL:-}"
TFM_EXTRAS_REFSPEC="${TFM_EXTRAS_REFSPEC:-"$(parse_version lib/ext/tf-m-extras/CMakeLists.txt set\(TFM_EXTRAS_REPO_VERSION \" 2)"}"
TFM_EXTRAS_NAME="tf-m-extras"

TFM_TOOLS_PROJECT="${TFM_TOOLS_URL:-}"
TFM_TOOLS_REFSPEC="${TFM_TOOLS_REFSPEC:-"$(parse_version lib/ext/tf-m-tools/CMakeLists.txt set\(TFM_TOOLS_VERSION \" 2)"}"
TFM_TOOLS_NAME="tf-m-tools"

QA_TOOLS_PROJECT="https://review.trustedfirmware.org/ci/qa-tools"
QA_TOOLS_REFSPEC="openci"
QA_TOOLS_NAME="qa-tools"

# Array containing "<repo url>;"<repo name>;<refspec>" elements
dependency_repos=(
    "${TFM_TESTS_PROJECT};${TFM_TESTS_NAME};${TFM_TESTS_REFSPEC}"
    "${MBEDTLS_PROJECT};${MBEDTLS_NAME};${MBEDTLS_REFSPEC}"
    "${MCUBOOT_PROJECT};${MCUBOOT_NAME};${MCUBOOT_REFSPEC}"
    "${QCBOR_PROJECT};${QCBOR_NAME};${QCBOR_REFSPEC}"
    "${TFM_EXTRAS_PROJECT};${TFM_EXTRAS_NAME};${TFM_EXTRAS_REFSPEC}"
    "${TFM_TOOLS_PROJECT};${TFM_TOOLS_NAME};${TFM_TOOLS_REFSPEC}"
    "${QA_TOOLS_PROJECT};${QA_TOOLS_NAME};${QA_TOOLS_REFSPEC}"
)

for repo in ${dependency_repos[@]}; do
    # Parse the repo elements
    REPO_URL="$(echo "${repo}" | awk -F ';' '{print $1}')"
    REPO_NAME="$(echo "${repo}" | awk -F ';' '{print $2}')"
    REPO_REFSPEC="$(echo "${repo}" | awk -F ';' '{print $3}')"

    clone_repo_to_share_folder "${REPO_URL}" "${REPO_NAME}" "${REPO_REFSPEC}"
done

PSA_ARCH_TESTS_PROJECT="${PSA_ARCH_TESTS_URL:-}"
PSA_ARCH_TESTS_REFSPEC="${PSA_ARCH_TESTS_VERSION:-"$(parse_version ../tf-m-tests/tests_psa_arch/fetch_repo/CMakeLists.txt set\(PSA_ARCH_TESTS_VERSION \" 2)"}"
PSA_ARCH_TESTS_NAME="psa-arch-tests"

clone_repo_to_share_folder "${PSA_ARCH_TESTS_PROJECT}" "${PSA_ARCH_TESTS_NAME}" "${PSA_ARCH_TESTS_REFSPEC}"
