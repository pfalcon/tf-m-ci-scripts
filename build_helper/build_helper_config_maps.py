#!/usr/bin/env python3

""" build_helper_config_maps.py:
    Set map info of config params for build helper """

__copyright__ = """
/*
 * Copyright (c) 2022, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

# Map platform names to short format
mapPlatform = {
    "arm/mps2/an519"                     : "AN519",
    "arm/mps2/an521"                     : "AN521",
    "arm/mps3/an524"                     : "AN524",
    "arm/mps3/an547"                     : "AN547",
    "arm/mps3/an552"                     : "AN552",
    "arm/musca_b1"                       : "MUSCA_B1",
    "arm/musca_s1"                       : "MUSCA_S1",
    "arm/corstone1000"                   : "corstone1000",
    "arm/mps3/corstone310/fvp"           : "corstone310",
    "arm/rss/tc"                         : "RSS",
    "cypress/psoc64"                     : "psoc64",
    "lairdconnectivity/bl5340_dvk_cpuapp": "BL5340",
    "nordic_nrf/nrf5340dk_nrf5340_cpuapp": "nrf5340dk",
    "nordic_nrf/nrf9160dk_nrf9160"       : "nrf9160dk",
    "nuvoton/m2351"                      : "M2351",
    "nuvoton/m2354"                      : "M2354",
    "nxp/lpcxpresso55s69"                : "lpcxpresso55s69",
    "stm/stm32l562e_dk"                  : "stm32l562e_dk",
    "stm/b_u585i_iot02a"                 : "b_u585i_iot02a",
    "stm/nucleo_l552ze_q"                : "nucleo_l552ze_q",
}

# Map PSA Arch Tests to short format
mapTestPsaApi = {
    "IPC"                : "FF",
    "CRYPTO"             : "CRYPTO",
    "INITIAL_ATTESTATION": "ATTEST",
    "STORAGE"            : "STORAGE",
}

# Map Profile names to short format
mapProfile = {
    "profile_small" : "SMALL",
    "profile_medium": "MEDIUM",
    "profile_large" : "LARGE",
}

# Map abbreviation of extra params to cmake build commands
mapExtraParams = {
    # Default
    ""             : "",
    "NSOFF"        : "-DNS=OFF ",
    # NSCE
    "NSCE"         : "-DTFM_NS_MANAGE_NSID=ON ",
    # MMIO
    "MMIO"         : "-DPSA_FRAMEWORK_HAS_MM_IOVEC=ON ",
    # FPU support
    "FPOFF"        : "-DCONFIG_TFM_ENABLE_FP=OFF ",
    "FPON"         : ("-DCONFIG_TFM_ENABLE_FP=ON "
                      "-DTEST_S_FPU=ON -DTEST_NS_FPU=ON "),
    "LZOFF"        : "-DCONFIG_TFM_LAZY_STACKING=OFF ",
    # Partiton
    "PSOFF"        : "-DTFM_PARTITION_PROTECTED_STORAGE=OFF ",
    # SFN
    "SFN"          : "-DCONFIG_TFM_SPM_BACKEND=SFN ",
    # CC Driver
    "CC_DRIVER_PSA": "-DCC312_LEGACY_DRIVER_API_ENABLED=OFF ",
    # ST support
    "CRYPTO_OFF"   : ("-DTEST_S_CRYPTO=OFF "
                      "-DTEST_NS_CRYPTO=OFF "),
    "CRYPTO_ON"    : ("-DTEST_S_CRYPTO=ON "
                      "-DTEST_NS_CRYPTO=ON "),
    # Corstone1000 support
    "FVP"          : "-DPLATFORM_IS_FVP=True ",
    "FPGA"         : "-DPLATFORM_IS_FVP=False ",
    "S_PS_OFF"     : "-DTEST_S_PS=OFF ",
}
