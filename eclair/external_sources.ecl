#
# Copyright (c) 202-2023, Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# External aka 3rd-party sources included in a project.
# These are intended to be filtered from MISRA reports (as we don't have
# control over them, can't easily fix issues in them, and generally that's
# normally out of scope of the project).

-file_tag+={external, "^trusted-firmware-m/platform/ext/cmsis/.*$"}
-file_tag+={external, "^trusted-firmware-m/lib/ext/mbedcrypto/.*$"}

