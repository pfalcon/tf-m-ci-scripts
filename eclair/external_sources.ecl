#
# Copyright (c) 2022-2023, Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# External aka 3rd-party sources included in a project.
# These are intended to be filtered from MISRA reports (as we don't have
# control over them, can't easily fix issues in them, and generally that's
# normally out of scope of the project).

-file_tag+={external, "^mbedtls/.*$"}
-file_tag+={external, "^mcuboot/.*$"}
-file_tag+={external, "^QCBOR/.*$"}
-file_tag+={external, "^qcbor/.*$"}
-file_tag+={external, "^trusted-firmware-m/platform/ext/cmsis/.*$"}
-file_tag+={external, "^trusted-firmware-m/lib/ext/mbedcrypto/.*$"}
-file_tag+={external, "^trusted-firmware-m/lib/ext/cryptocell-312-runtime/.*$"}
-file_tag+={external, "^trusted-firmware-m/lib/ext/t_cose/.*$"}

# Ignore any auto-generated source files in build dir.
# TODO make an exception for ci_build/spe/build-spe/generated in which source code is
# built in TF-M binaries.
-file_tag+={external, "^ci_build/.*$"}

# Ignore compiler internal headers.
-file_tag+={external, "^/.+/compiler/gcc-.*$"}

# Ignore tf-m-tests. Source code under tf-m-tests will not be included
# in production release.
-file_tag+={external, "^tf-m-tests/.*$"}

# Ignore vendor platform specific soure code
-file_tag+={external, "^trusted-firmware-m/platform/ext/target/.*$"}
