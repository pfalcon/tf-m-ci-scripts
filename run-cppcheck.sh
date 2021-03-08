#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2018-2020, Arm Limited and Contributors. All rights reserved.
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
##configuration (i.e. no build config file is specified on the command-line).
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
##      might be invalid, and also a different file may be needed based on
##      used compiler switches (i.e. to match width specification and or default
##      sign for some types).
##@todo Currently cppcheck is only executed for the default build configuration
##      "ConfigDefault.cmake"for target AN521 of the "top level" project.
##      This might need to be revised/changed in the future.
##

#Fail if any command exit with error.
set -e

RAW_OUTPUT=0

while getopts "hr" opt ; do
  case "$opt" in
    h)
      echo "Usage: $(basename -- "$0") [-h] [-r] [git_hash]"
      echo " -r, Raw output. (Default is to create xml reports)."
      echo " -h, Script help"
      exit 0
      ;;
    r)
      RAW_OUTPUT=1
      ;;
  esac
done

shift $((OPTIND-1))

#The location from where the script executes
mypath=$(dirname $0)

#The cmake_exported project file in json format
cmake_commands=compile_commands.json

. "$mypath/util_cmake.sh"

#Library file for cppcheck
library_file="$(fix_win_path $(get_full_path $mypath))/cppcheck/arm-cortex-m.cfg"
suppress_file="$(fix_win_path $(get_full_path $mypath))/cppcheck/tfm-suppress-list.txt"
toolchain_file="$(fix_win_path $(get_full_path ./))/toolchain_GNUARM.cmake"

#Enable all additional checks by default
additional_checklist="all"

#Run cmake to get the compile_commands.json file
echo
echo '******* Generating compile_commands.json ***************'
echo
generate_project $(fix_win_path $(get_full_path ./)) "./" "cppcheck" "-DCMAKE_EXPORT_COMPILE_COMMANDS=1 -DTFM_PLATFORM=mps2/an521 -DTFM_TOOLCHAIN_FILE=$toolchain_file"
#Enter the build directory
bdir=$(make_build_dir_name "./" "cppcheck")
pushd "$bdir" >/dev/null

#The following snippet allows cppcheck to be run differentially against a
#commit hash passed as first argument $1. It does not
#affect the legacy functionality of the script, checking the whole codebase,
#when called without an argument
if [[ ! -z "$1" ]]
  then
    echo "Enabled git-diff mode against hash:  $1"

    # Do not execute unused function check and information check when running in diff-mode
    additional_checklist="style,performance,portability,missingInclude"
    # Grep will set exit status to 1 if a commit does not contain c/cpp.. files
    set +e
    filtered_cmd_f=compile_commands_filtered.json
    # Get a list of files modified by the commits between the reference and HEAD
    flist=$(git diff-tree --no-commit-id --name-only -r $1 | grep -E '\S*\.(c|cpp|cc|cxx|inc|h)$')
    flist=$(echo $flist | xargs)
    echo -e "[" > $filtered_cmd_f
    IFS=$' ' read -ra git_flist <<< "${flist}"

    for fl in "${git_flist[@]}"; do
        echo "Looking for reference of file: $fl"

        # dry run the command to see if there any output
        JSON_CMD=$(grep -B 3 "\"file\": \".*$fl\"" $cmake_commands)

        if [ -n "${JSON_CMD}" ]; then
            command_matched=1
            grep -B 3 "\"file\": \".*$fl\"" $cmake_commands >> $filtered_cmd_f
            echo -e "}," >> $filtered_cmd_f
        fi
    done
    set -e

    # Only continue if files in the patch are included in the build commands
    if [ -n "${command_matched}" ]; then
        sed -i '$ d' $filtered_cmd_f
        echo -e "}\n]" >> $filtered_cmd_f

        cat $filtered_cmd_f > $cmake_commands
    else
        echo "CppCheck: Ignoring files not contained in the build config"
        if [ "$RAW_OUTPUT" == "0" ] ; then
          # Always generate an empty file for other stages of ci expecting one
        echo "Files Ignored: $flist"
				cat <<-EOF > chk-config.xml
				<?xml version="1.0" encoding="UTF-8"?>
				<results version="2">
				    <cppcheck version="$(cppcheck --version)"/>
				    <errors>
				    </errors>
				</results>
				EOF
        cp chk-config.xml chk-src.xml
        fi
        exit 0
    fi
fi

function cppcheck_failed {
  # echo "cppcheck failed."
  # echo "Check log for errors."
  echo "CppCheck needs to be updated. Current Version would fail with no error."
  echo "Skip voting for the time being."
  exit 1
}

EXTRA_ARGS="--error-exitcode=1"
if [ "$RAW_OUTPUT" != "1" ] ; then
  # If not in raw output mode, use xml output.
  EXTRA_ARGS="--xml"
else
  trap cppcheck_failed ERR
fi
CPPCHECK_ARGS="$EXTRA_ARGS --enable="$additional_checklist" --library="$library_file" --project=$cmake_commands --suppressions-list="$suppress_file" --inline-suppr"

#Now run cppcheck.
echo
echo '******* checking cppcheck configuration ***************'
echo

if [ "$RAW_OUTPUT" == "1" ] ; then
  cppcheck $CPPCHECK_ARGS --check-config > /dev/null
else
  cppcheck $CPPCHECK_ARGS --check-config 2>chk-config.xml
fi

echo
echo '******* analyzing files with cppcheck ***************'
echo
if [ "$RAW_OUTPUT" == "1" ] ; then
  cppcheck $CPPCHECK_ARGS > /dev/null
  echo '******* cppcheck complete ***************'
else
  cppcheck $CPPCHECK_ARGS 2>chk-src.xml
  echo
  echo '******* Please check chk-config.xml and chk-src.xml for the results. ***************'
  echo
fi
popd
