#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2018-2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

##
##@file
##@brief Execute cppcheck
##
##This bash script can be used to execute cppcheck for the tf-m project.
##It will use the CMake generated "compile_commands.json" file.
##CMake is executed to generate the build commands for the "default" build
##configuration (i.e. no build config file is specifyed on the command-line).
##
##This file shall be executed from the root directory of the tf-m working copy.
##
##In order to have all include file in place, some CMake external projects will
##be built, and thus C build tools for the default build configuration must be
##available.
##
##The script will generate two XML output files:
##file    | description
##--------|--------
##chk-config.xml | The result of cppcheck configuration verification.
##chk-src.xml. | The result of source file verification.
##
##@todo The current version of cppcheck seems to ignore command line parameters
##       when using the --project command line switch. As a result it is not
##       possible to define additional macros and include paths on the command
##       line. This results in some incorrect error and warning messages.
##@todo The file cppcheck/arm-cortex-m.cfg needs to be revised. Some settings
##      might be invalid, and also a differnet file may be needed based on
##      used compiler switches (i.e. to match witdh specification and or default
##      sign for some types).
##@todo Currently cppcheck is only executed for the default build configuration
##      "ConfigDefault.cmake"for target AN521 of the "top level" project.
##      This might need to be revied/changed in the future.
##

#Fail if any command exit with error.
set -e

#The location from where the script executes
mypath=$(dirname $0)

. "$mypath/util_cmake.sh"


#Library file for cppcheck
library_file="$(fix_win_path $(get_full_path $mypath))/cppcheck/arm-cortex-m.cfg"
suppress_file="$(fix_win_path $(get_full_path $mypath))/cppcheck/tfm-suppress-list.txt"

#Run cmake to get the compile_commands.json file
echo
echo '******* Generating compile_commandas.json ***************'
echo
generate_project $(fix_win_path $(get_full_path ./)) "./" "cppcheck" "-DCMAKE_EXPORT_COMPILE_COMMANDS=1  -DTARGET_PLATFORM=AN521 -DCOMPILER=GNUARM"
#Enter the build directory
bdir=$(make_build_dir_name "./" "cppcheck")
pushd "$bdir" >/dev/null
#Build the external projects to get all headers installed to plases from where
#tf-m code uses them
echo
echo '******* Install external projects to their final place ***************'
echo
make -j mbedtls_sst_lib_install mbedtls_mcuboot_lib_install

#Now run cppcheck.
echo
echo '******* checking cppcheck configuration ***************'
echo
cppcheck --xml -j 4 --check-config --enable=all --library="$library_file" --project=compile_commands.json --suppressions-list="$suppress_file" --inline-suppr 2>chk-config.xml

echo
echo '******* analyzing files with cppcheck ***************'
echo
cppcheck --xml -j 4 --enable=all --library="$library_file" --project=compile_commands.json --suppressions-list="$suppress_file" --inline-suppr 2>chk-src.xml
popd

echo
echo '******* Please check chk-config.xml and chk-src.xml for the results. ***************'
echo
