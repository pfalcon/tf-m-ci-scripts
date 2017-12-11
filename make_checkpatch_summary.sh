#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2018-2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

##
##@file
##@brief This script is to make a summary of run-checkpatch.sh generated output
##files.
##
##The generated summary will hold the number of error and warning messages for
##each file.
##
##The first parameter of the script must be the location of input file.
##

#Check parameter
if [ -z ${1+x} ]
then
	echo "Checkpatch output file not specified!"
	exit 1
fi

infile="$1"

#Find the summary line for each file. Cut the summary line plus the file name
#the previous line.
#Concatenate the current line to the previos one,
#Print the two lines match the following regexp:
#   remember anything any number of non : characters (this is the file path)
#     followed by a :
#   match any nuber of following characters till "total:" is found
#   remember all characters after "total:" (this is the summary)
#   replace the matched string with first and and the second match concatenated
#       with new line and a tab character in between.
#   we use s: single line and m: multi line modificators for the regexp match
res=$(perl -ne '$l=$l.$_; print "$l" if $l=~s/.*?([^:]+):.*\ntotal:(.*)/$1:\n\t$2/sm;$l=$_;' "$infile")

#Print the result to standard output.
cat <<EOM
Checkpatch result summary:
$res
EOM
