#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2018-2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

#Fail if any executed command fails.
set -e

##
##@file
##@brief This script is to make a summary of cppcheck XML output files.
##
##The generated summary will hold the number of messages of each severity type.
##
##The first parameter of the script must be the location of the XML file.
##
##The script uses regual expressions to identify and count messages.
##
##Usage:
##  command | result
##  --------|-------
##  make_cppcheck_summary.sh foo/bar/build.xml | Summary text.
##

#Check parameter
if [ -z ${1+x} ]
then
	echo "Cppcheck output file not specified!"
	exit 1
fi

xml_file="$1"

#List of error types cmake reports.
severity_list=( "none" "error" "warning" "style" "performance" "portability"
				"information" "debug")

#Count each severity type and build result message.
for severity in "${severity_list[@]}"
do
	#Count lines with this severity type.
	n=$(grep -c "severity=\"$severity\"" "$xml_file" || true)
	#Start of report line
	line=$'\n\tIssues with severity '"\"$severity\":"
	#Indentatin to character position 46.
	indent=$(eval "printf ' %.0s' {1..$(( 46-${#line} ))}")
	#Add identation and number
	line="$line$indent$n"
	#Extend issue list
	issue_list="$issue_list$line"
done
msg="Cppcheck results: $issue_list"

echo "$msg"
