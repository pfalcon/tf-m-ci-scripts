#!/usr/bin/env bash
#
# Copyright (c) 2023 Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Parse dependency version from file
# Input parameters:
#     RELATIVE_PATH:  Relative path to the dependency version config file in TF-M
#     PATTERN:        Pattern used to search for the line containing target dependency version
#     SEPARATOR:      Separator to split the string
#     COMPONENT_NUM:  Decide which separated component is the dependency version
function parse_version() {
    RELATIVE_PATH=$1
    PATTERN=$2
    SEPARATOR=$3
    COMPONENT_NUM=$4

    ABSOLUTE_PATH="${SHARE_FOLDER}/${TFM_NAME}/${RELATIVE_PATH}"

    VERSION="$(grep "${PATTERN}" ${ABSOLUTE_PATH} | cut -d${SEPARATOR} -f${COMPONENT_NUM})"

    if [ -z "${VERSION}" ]; then
        VERSION="refs/heads/main"
    fi

    echo "${VERSION}"
}
