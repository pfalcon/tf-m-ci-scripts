#!/bin/bash
#-------------------------------------------------------------------------------
# Copyright (c) 2018-2021, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
#-------------------------------------------------------------------------------

##
##@file
##@brief Execute checkpatch
##
##This bash script can be used to execute checkpatch for the tf-m project.
##The script can be started with -h to give help on usage.
##


##@var SKIP_PATHS
##@brief Folders and files to not be analysed by checkpatch
##
##This variable specifies the list of directories which shall not be analysed
##by checkpatch.
##This is a colon (:) separated list.
##
#This is needed for Doxygen for now.
#!string SKIP_PATHS;
SKIP_PATHS='./build-\*:./platform/\*:*/tz_\*:./lib/\*:./platform/ext/\*:./bl2/ext/\*:./docs/\*:./tools/\*'

##@var TFM_DIRECTORY_NAME
##@brief Default path to tf-m source code.
##
#This is needed for Doxygen for now.
#!path TFM_DIRECTORY_NAME;
TFM_DIRECTORY_NAME="./"

##@var OUTPUT_FILE_PATH
##@brief Default path to report file.
##
##This text file will hold the output report of checkpatch.
##
#This is needed for Doxygen for now.
#!path OUTPUT_FILE_PATH;
OUTPUT_FILE_PATH="tfm_checkpatch_report.txt"

##@var CHECKPATCH_PATH_DEF
##@brief Default Path to checkpatch executable.
##
#This is needed for Doxygen for now.
#!path CHECKPATCH_PATH_DEF;
CHECKPATCH_PATH_DEF=$(readlink -f $(dirname "$0")"/checkpatch")

##@var CHECKPATCH_PATH
##@brief Path to checkpatch executable.
##
## Checkpatch path can be overriden by user argument. Initialized with Default
## value of ./checkpatch
##
#This is needed for Doxygen for now.
#!path CHECKPATCH_PATH;
CHECKPATCH_PATH=$CHECKPATCH_PATH_DEF

##@fn usage(void)
##@brief Print help text on usage.
##@returns n/a
##
#This is needed for Doxygen for now.
#!void usage(void){};
usage() {
	echo "Usage: $(basename -- "$0") [-v] [-h] [-d <TF-M dir>] [-f <output_filename>] [-u] [-p <number>]"
	echo " -v, Verbose output"
	echo " -h, Script help"
	echo " -d, <TF-M dir>, TF-M directory"
	echo " -f, <output_filename>, Output filename"
	echo " -u, Update checkpatch files using curl"
	echo " -l <number>, Check only the last <number> commits (HEAD~<number>)."
	echo " -p <path>, Provide location of directory containing checkpatch."
	echo " -r, Print raw output. Implies verbose."
	echo -e "\nNOTE: make sure checkpatch is located in '$CHECKPATCH_PATH'"
}

##@fn app_err(void)
##@brief Print error massage.
##@returns n/a
##
#This is needed for Doxygen for now.
#!void app_err(void){};
app_err() {
	echo "Error: "$1 >&2
}

##@fn download_checkpatch_file(string f_name)
##@brief Download the specified checkpatch file.
##@param[in] f_name name of file to download.
##@returns status code
##
##Download checkpatch files from raw.githubusercontent.com to the current
##directory. Target files are truncated to avoid breaking links.
##
#This is needed for Doxygen for now.
#!err download_checkpatch_file(string f_name){};
download_checkpatch_file() {
	# HTTPS address location to download checkpatch file
	if [ $VERBOSE -eq 0 ]; then
		REDIRECT=" >/dev/null"
	fi

	curl "https://raw.githubusercontent.com/torvalds/linux/v5.9/scripts/$1" --output "$1.new" &>/dev/null

	if [ $? != 0 ]; then
		app_err "curl reported error while downloading $1"
		exit 1
	else
		#Copy file and preserve links.
		cat "$1.new" > "$1"
		rm "$1.new"
	fi
}

##@fn update_checkpatch()
##@brief Download checkpatch files.
##@returns status code
##
##Download checkpatch files from raw.githubusercontent.com to \ref CHECKPATCH_PATH
##directory.
##
#This is needed for Doxygen for now.
#!void update_checkpatch(){};
update_checkpatch() {
	echo "Updating checkpatch..."
	if ! [ -x "$(command -v curl)" ]; then
		app_err "curl was not found. Please, make sure curl command is available"
		exit 1
	fi

	pushd $CHECKPATCH_PATH > /dev/null
	#Execute popd when shell exits.
	trap popd 0

	# Download checkpatch.pl
	download_checkpatch_file checkpatch.pl
	chmod 750 $CHECKPATCH_PATH/checkpatch.pl

	# Download const_structs.checkpatch
	download_checkpatch_file const_structs.checkpatch
	chmod 640 $CHECKPATCH_PATH/const_structs.checkpatch

	# Download spelling.txt
	download_checkpatch_file spelling.txt
	chmod 640 $CHECKPATCH_PATH/spelling.txt

	popd >/dev/null
	#Remove cleanup trap
	trap 0
}

##@fn check_tree()
##@brief Run checkpatch in directory tree checking mode
##@returns status code
##
##Execute checkpatch to check the full content of all source files under the
##directory specified in \ref TFM_DIRECTORY_NAME. Directory content specified in
##\ref SKIP_PATHS will be excluded.
##This function uses xargs to execute multiple checkpatch instances in parallel.
##
#This is needed for Doxygen for now.
#!void check_tree(){};
check_tree() {
	# Find all files to execute checkpatch on
	FIND_CMD="find $TFM_DIRECTORY_NAME -name '*.[ch]' -a -not \( -path "${SKIP_PATHS//:/ -o -path }" \)"
	echo "Scanning "$TFM_DIRECTORY_NAME" dir to find all .c and .h files to check ..."
	#Modify checkpatch command line to make checkpatch work on files.
	CHECKPATCH_CMD="$CHECKPATCH_CMD -f "
	if [ $VERBOSE -eq 1 ]; then
		eval "$FIND_CMD" | xargs -n 1 -i -P 8 $CHECKPATCH_CMD {} |tee -a "$OUTPUT_FILE_PATH"
		RETURN_CODE=${PIPESTATUS[1]}
	else
		eval "$FIND_CMD" | xargs -n 1 -i -P 8 $CHECKPATCH_CMD {} >> $OUTPUT_FILE_PATH
		RETURN_CODE=${PIPESTATUS[1]}
	fi
}

##@fn check_diff()
##@brief Run checkpatch in git diff mode.
##@returns status code
##
##Execute checkpatch to check the last N (\ref CHECK_LAST_COMMITS) commits of
##the branch checked out at directory specified in \ref TFM_DIRECTORY_NAME.
##Directory content specified in \ref SKIP_PATHS will be excluded.
##
#This is needed for Doxygen for now.
#!void check_diff(){};
check_diff() {
	BASE_COMMIT="HEAD~$CHECK_LAST_COMMITS"
	#use find to limit diff content to the same set of files as when checking
	#the whole tree.
	FIND_CMD="find ./ -name '*.[ch]' -a -not \( -path "${SKIP_PATHS//:/ -o -path }" \)"

	#enter tf-m working copy to make git commands execute fine
	pushd "$TFM_DIRECTORY_NAME" > /dev/null
	#Execute popd when shell exits
	trap popd 0

	#List of files we care about. Filter out changed files from interesting
	#list of files. This is needed to avoid GIT_CMD to break the argument
	#list length.
	CARE_LIST=$(eval $FIND_CMD | grep "$(git diff $BASE_COMMIT --name-only)" -)

	if [ ! -z "$CARE_LIST" ]; then
		# Only run checkpatch if there are files to check
		GIT_CMD="git diff $BASE_COMMIT -- $CARE_LIST"
		echo "$GIT_CMD"
		echo "Checking commits: $(git log "$BASE_COMMIT"..HEAD --format=%h | tr $"\n" " ")"

		#Modify checkpatch parameters to give more details when working on
		#diff:s
		CHECKPATCH_CMD="$CHECKPATCH_CMD --showfile -"
	fi

	if [ $VERBOSE -eq 1 ]; then
		$GIT_CMD | $CHECKPATCH_CMD | tee -a "$OUTPUT_FILE_PATH"
		RETURN_CODE=${PIPESTATUS[1]}
	else
		$GIT_CMD | $CHECKPATCH_CMD >> $OUTPUT_FILE_PATH
		RETURN_CODE=${PIPESTATUS[1]}
	fi

	popd > /dev/null
	#Remove cleanup trap.
	trap 0
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~ Entry point ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Internal variables not to be modified.
VERBOSE=0
UPDATE_CHECKPATCH_FILES=0

##@var CHECK_LAST_COMMITS
##@brief Number of commits to check.
##
##Number of commits relative to HEAD to check. When set to 0 full file content
##is checked instead of commit diffs.
##
#This is needed for Doxygen for now.
#!path CHECK_LAST_COMMITS;
CHECK_LAST_COMMITS=0

# Whether to print the output to screen.
RAW_OUTPUT=0

# Getting options and setting variables required to execute the script. This
# script starts executing from here.
while getopts "uvhd:f:l:p:r" opt
do
	case $opt in
		v) VERBOSE=1 ;;
		h) usage ; exit 0 ;;
		d) TFM_DIRECTORY_NAME="$OPTARG" ;;
		f) OUTPUT_FILE_PATH="$OPTARG" ;;
		u) UPDATE_CHECKPATCH_FILES=1 ;;
		l) CHECK_LAST_COMMITS="$OPTARG" ;;
		p) CHECKPATCH_PATH="$OPTARG" ;;
		r) RAW_OUTPUT=1
		   VERBOSE=1 ;;
		\?) usage ; exit 1 ;;
	esac
done

# Update checkpatch files
if [ $UPDATE_CHECKPATCH_FILES -eq 1 ]; then
	update_checkpatch
	echo "Checkpatch update was successful."
	exit 0
fi

#Convert checkpath override path to full path
CHECKPATCH_PATH=$(readlink -f "$CHECKPATCH_PATH")

#Convert output file name to full path
OUTPUT_FILE_PATH=$(readlink -f "$OUTPUT_FILE_PATH")

# Create checkpatch command
CHECKPATCH_APP=$CHECKPATCH_PATH"/checkpatch.pl"
CHECKPATCH_CONFG_FILENAME=$CHECKPATCH_PATH_DEF"/checkpatch.conf"
CHECKPATCH_CMD=$CHECKPATCH_APP" $(grep -o '^[^#]*' $CHECKPATCH_CONFG_FILENAME)"

# Check if checkpatch is present
if ! [ -f "$CHECKPATCH_APP" ]; then
	app_err "checkpatch.pl was not found. checkpatch.pl has to be located in $CHECKPATCH_PATH"
	exit 1
fi

#Truncate previous content
: > $OUTPUT_FILE_PATH

#Do we need to work on a git diff?
if [ $CHECK_LAST_COMMITS -eq 0 ]
then
	#Working on files
	check_tree
else
	#Working on git diff
	check_diff
fi

if [ "$RAW_OUTPUT" == "1" ] ; then
	rm $OUTPUT_FILE_PATH
	exit $RETURN_CODE
else
	echo "checkpatch report \"$OUTPUT_FILE_PATH\" is ready!"
fi
