#!/usr/bin/env bash
#
# Copyright (c) 2023 Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Don't print mouthful "You are in 'detached HEAD' state." messages.
git config --global advice.detachedHead false

# Global defaults
GIT_CLONE_PARAMS="--no-checkout"

function git_clone() {
    # Parse the repo elements
    REPO_URL=$1
    REPO_PATH=$2

    # In case repository is not defined, just skip it
    if [ -z "${REPO_URL}" ]; then
        return
    fi

    # Clone if it does not exit
    if [ ! -d ${REPO_PATH} ]; then
        git clone --quiet ${GIT_CLONE_PARAMS} ${REPO_URL} ${REPO_PATH}
    fi
}

function git_checkout() {
    # Parse the repo elements
    REPO_PATH=$1
    REPO_REFSPEC=$2

    # Checkout if repo exits
    if [ -d ${REPO_PATH} ]; then
        cd ${REPO_PATH}

        # Fetch the corresponding refspec
        REPO_FETCH_HEAD=$(git ls-remote --quiet | grep ${REPO_REFSPEC} | awk -v d=" " '{s=(NR==1?s:s d)$1} END{print s}')

        if [ -z "${REPO_FETCH_HEAD}" ]; then
            git fetch --all
        else
            git fetch origin ${REPO_FETCH_HEAD}
        fi

        # Checkout to specified refspec
        if [[ "${REPO_REFSPEC}" =~ "refs/" ]]; then
            # Refspec in "refs/" format cannot be directly used to checkout
            git checkout ${REPO_FETCH_HEAD}
        else
            git checkout ${REPO_REFSPEC}
        fi

        echo -e "Share Folder ${REPO_PATH} $(git rev-parse --short HEAD)\n"
        cd $OLDPWD
    fi
}
