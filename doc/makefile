# -----------------------------------------------------------------------------\
# Copyright (c) 2017-2019, Arm Limited and Contributors. All rights reserved.       \
#                                                                              \
# SPDX-License-Identifier: BSD-3-Clause                                        \
#                                                                              \
------------------------------------------------------------------------------*/

.PHONY: all

COMPR=7z

ifeq ($(OS),Windows_NT)
COMPR=7z.exe
endif

COMPR_FLAGS=a -tzip

git_hash:=$(shell git log --format="%cd_%h" --date=short -n 1)

archive_name=html_${git_hash}.zip

.PHONY: all
all: html zip

html:
	doxygen Doxyfile

zip: ${archive_name}

${archive_name}: html
	"${COMPR}" ${COMPR_FLAGS} $@ $?

.PHONY: clean
clean:
	-rm html_*.zip
	-rm -rf html
