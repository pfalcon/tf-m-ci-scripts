#!/bin/bash
#
# Copyright (c) 2024, Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Script to configure TuxSuite tool.

mkdir -p ~/.config/tuxsuite/
cat > ~/.config/tuxsuite/config.ini <<EOF
[default]
token=$TUXSUITE_TOKEN
group=tfc
project=ci
EOF
