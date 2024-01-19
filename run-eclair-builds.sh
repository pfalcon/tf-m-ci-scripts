#!/bin/bash

set -ex

LICENSE_LEASE=5400

. tf-ci-scripts/eclair/utils.sh
. tf-m-ci-scripts/eclair/utils_tfm.sh

num_configs=$(python3 ./tf-m-ci-scripts/configs.py -g "$FILTER_GROUP" | wc -l)

echo "Number of configs to build: $num_configs"

cnt=1

for cfg in $(python3 ./tf-m-ci-scripts/configs.py -g "$FILTER_GROUP"); do
    echo "============== $cfg ($cnt/$num_configs) =============="
    export CONFIG_NAME=$cfg
    (cd mbedtls; git checkout .; git clean -fq)
    (cd psa-arch-tests; git checkout .; git clean -fq)
    (cd trusted-firmware-m; git checkout .; git clean -fq)
    eclair_tfm_set_toolchain_path
    detachLicense $LICENSE_LEASE
    tf-m-ci-scripts/run-build.sh
    cnt=$((cnt + 1))
done

# Extend license lease one final time for further processing after the builds
# (creation of project database and rendering reports, etc.).
detachLicense $LICENSE_LEASE

echo "Built $num_configs configs"
