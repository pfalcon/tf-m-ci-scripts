#!/bin/bash
#
# Copyright (c) 2019-2021, Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# unittest-include-order.sh <path-to-root-folder> [patch]

set -o pipefail

LOG_FILE=$(mktemp -t include-order-check.XXXX)

if [[ "$2" == "patch" ]]; then
  echo "# Check order of includes on the last patch"
  TEST_CASE="Order of includes on the last patch(es)"
  "$CI_ROOT/script/static-checks/check-include-order.py" --tree "$1" \
      --patch --from-ref origin/master \
      | tee "$LOG_FILE"
else
  echo "# Check order of includes of the entire source tree"
  TEST_CASE="Order of includes of the entire source tree"
  "$CI_ROOT/script/static-checks/check-include-order.py" --tree "$1" \
      | tee "$LOG_FILE"
fi

EXIT_VALUE=$?

echo >> "$LOG_TEST_FILENAME"
echo "****** $TEST_CASE ******" >> "$LOG_TEST_FILENAME"
echo >> "$LOG_TEST_FILENAME"
if [[ "$EXIT_VALUE" == 0 ]]; then
  echo "Result : SUCCESS" >> "$LOG_TEST_FILENAME"
else
  echo "Result : FAILURE" >> "$LOG_TEST_FILENAME"
  echo >> "$LOG_TEST_FILENAME"
  cat "$LOG_FILE" >> "$LOG_TEST_FILENAME"
fi
echo >> "$LOG_TEST_FILENAME"

rm -f "$LOG_FILE"

exit "$EXIT_VALUE"
