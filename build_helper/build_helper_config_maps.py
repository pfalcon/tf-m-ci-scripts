#!/usr/bin/env python3

""" build_helper_config_maps.py:
    Set map info of config params for build helper """

__copyright__ = """
/*
 * Copyright (c) 2022-2023, Arm Limited. All rights reserved.
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

# Map regression test parameters to short format
mapRegTest = {
    "OFF"       : "-DTEST_BL2=OFF -DTEST_S=OFF -DTEST_NS=OFF ",
    "RegBL2"    : "-DTEST_BL2=ON ",
    "RegS"      : "-DTEST_S=ON ",
    "RegNS"     : "-DTEST_NS=ON -DTEST_NS_FLIH_IRQ=OFF ",
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
    "profile_medium_arotless": "MEDIUM-AROT-LESS",
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
    # IPC
    "IPC"          : "-DCONFIG_TFM_SPM_BACKEND=IPC ",
    # CC Driver
    "CC_DRIVER_PSA": "-DCC312_LEGACY_DRIVER_API_ENABLED=OFF ",
    # ST support
    "CRYPTO_OFF"   : ("-DTEST_S_CRYPTO=OFF "
                      "-DTEST_NS_CRYPTO=OFF "),
    "CRYPTO_ON"    : ("-DTEST_S_CRYPTO=ON "
                      "-DTEST_NS_CRYPTO=ON "),
    # Corstone1000 support
    "FVP"          : "-DPLATFORM_IS_FVP=True ",
    "FPGA"         : "-DPLATFORM_IS_FVP=False -DTEST_S_PS=OFF -DTEST_S_PLATFORM=OFF ",
    "CS1K_TEST"    : ("-DTEST_S_IPC=OFF "
                      "-DEXTRA_S_TEST_SUITE_PATH=%(codebase_root_dir)s/platform/ext/target/arm/corstone1000/ci_regression_tests/ "),

    # Extra test cases
    "TEST_CBOR"    : "-DTEST_NS_QCBOR=ON ",

    # tf-m-extras example support
    "EXAMPLE_VAD"             : ("-DNS_EVALUATION_APP_PATH=%(codebase_root_dir)s/../tf-m-extras/examples/vad_an552/ns_side "
                                "-DTFM_EXTRA_PARTITION_PATHS=%(codebase_root_dir)s/../tf-m-extras/partitions/vad_an552_sp/ "
                                "-DTFM_EXTRA_MANIFEST_LIST_FILES=%(codebase_root_dir)s/../tf-m-extras/partitions/vad_an552_sp/extra_manifest_list.yaml "
                                "-DPROJECT_CONFIG_HEADER_FILE=%(codebase_root_dir)s/../tf-m-extras/examples/vad_an552/ns_side/project_config.h "
                                "-DTFM_PARTITION_FIRMWARE_UPDATE=ON -DMCUBOOT_DATA_SHARING=ON "
                                "-DMCUBOOT_UPGRADE_STRATEGY=SWAP_USING_SCRATCH "
                                "-DMCUBOOT_IMAGE_NUMBER=1 -DMCUBOOT_SIGNATURE_KEY_LEN=2048 "
                                "-DCONFIG_TFM_ENABLE_MVE=ON -DCONFIG_TFM_SPM_BACKEND=IPC "
                                "-DPLATFORM_HAS_FIRMWARE_UPDATE_SUPPORT=ON -DTFM_PARTITION_PLATFORM=ON "
                                "-DTFM_PARTITION_CRYPTO=ON -DTFM_PARTITION_INTERNAL_TRUSTED_STORAGE=ON "
                                "-DTFM_PARTITION_PROTECTED_STORAGE=ON  -DMCUBOOT_CONFIRM_IMAGE=ON "),
    "EXAMPLE_DMA350_TRIGGER"  : ("-DNS_EVALUATION_APP_PATH=%(codebase_root_dir)s/../tf-m-extras/examples/corstone310_fvp_dma/triggering_example "),
    "EXAMPLE_DMA350_CLCD"     : ("-DDEFAULT_NS_SCATTER=OFF -DPLATFORM_SVC_HANDLERS=ON "
                                "-DNS_EVALUATION_APP_PATH=%(codebase_root_dir)s/../tf-m-extras/examples/corstone310_fvp_dma/clcd_example "),
    "EXAMPLE_DMA350_S"        : "-DEXTRA_S_TEST_SUITE_PATH=%(codebase_root_dir)s/../tf-m-extras/examples/corstone310_fvp_dma/dma350_s",
    "EXAMPLE_DMA350_NS"       : "-DEXTRA_NS_TEST_SUITE_PATH=%(codebase_root_dir)s/../tf-m-extras/examples/corstone310_fvp_dma/dma350_ns"
}
