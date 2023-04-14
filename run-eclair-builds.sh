#!/bin/bash

set -ex

. tf-m-ci-scripts/eclair/utils.sh
. tf-m-ci-scripts/eclair/utils_tfm.sh

for cfg in $(python3 ./tf-m-ci-scripts/configs.py -g "$FILTER_GROUP"); do
    echo ============== $cfg ==============
    export CONFIG_NAME=$cfg
    (cd mbedtls; git checkout .; git clean -fq)
    (cd psa-arch-tests; git checkout .; git clean -fq)
    (cd trusted-firmware-m; git checkout .; git clean -fq)
    eclair_tfm_set_toolchain_path
    detachLicense 3000
    tf-m-ci-scripts/run-build.sh
done
