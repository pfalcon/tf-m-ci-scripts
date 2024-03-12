#!/usr/bin/env python3
#
# Copyright (c) 2019-2021, Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

import argparse
import codecs
import collections
import os
import re
import subprocess
import sys
import utils
import yaml
import logging


# File extensions to check
VALID_FILE_EXTENSIONS = (".c", ".S", ".h")


# Paths inside the tree to ignore. Hidden folders and files are always ignored.
# They mustn't end in '/'.
IGNORED_FOLDERS = (
    'platform/ext',
    'bl2/ext',
    'docs',
    'lib',
    'tools'
)

# List of ignored files in folders that aren't ignored
IGNORED_FILES = ()

INCLUDE_RE = re.compile(r"^\s*#\s*include\s\s*(?P<path>[\"<].+[\">])")
INCLUDE_RE_DIFF = re.compile(r"^\+?\s*#\s*include\s\s*(?P<path>[\"<].+[\">])")


def include_paths(lines, diff_mode=False):
    """List all include paths in a file. Ignore starting `+` in diff mode."""
    pattern = INCLUDE_RE_DIFF if diff_mode else INCLUDE_RE
    matches = (pattern.match(line) for line in lines)
    return [m.group("path") for m in matches if m]


def file_include_list(path):
    """Return a list of all include paths in a file or None on failure."""
    try:
        with codecs.open(path, encoding="utf-8") as f:
            return include_paths(f)
    except Exception:
        logging.exception(path + ":error while parsing.")
        return None


def inc_order_is_correct(inc_list, path, commit_hash=""):
    """Returns true if the provided list is in order. If not, output error
    messages to stdout."""

    # If there are less than 2 includes there's no need to check.
    if len(inc_list) < 2:
        return True

    if commit_hash != "":
        commit_hash = commit_hash + ":"

    # Get list of system includes from libc include directory.
    # No libc from TF-M secure_fw
    libc_incs = []

    # First, check if all includes are in the appropriate group.
    inc_group = "Public"
    incs = collections.defaultdict(list)
    error_msgs = []

    for inc in inc_list:
        if inc.startswith('"'):
            inc_group = "Private"
        elif inc_group == "Private":
            error_msgs.append(
                inc[1:-1] + " should be in public group, before private group"
            )
        incs[inc_group].append(inc[1:-1])

    # Then, check alphabetic order (system, project and user separately).
    if not error_msgs:
        for name, inc_list in incs.items():
            if sorted(inc_list) != inc_list:
                error_msgs.append("{} includes not in order.".format(name))

    # Output error messages.
    if error_msgs:
        print(yaml.dump({commit_hash + path: error_msgs}))
        return False
    else:
        return True


def file_is_correct(path):
    """Checks whether the order of includes in the file specified in the path
    is correct or not."""
    inc_list = file_include_list(path)
    return inc_list is not None and inc_order_is_correct(inc_list, path)


def directory_tree_is_correct():
    """Checks all tracked files in the current git repository, except the ones
       explicitly ignored by this script.
       Returns True if all files are correct."""
    (rc, stdout, stderr) = utils.shell_command(["git", "ls-files"])
    if rc != 0:
        return False
    all_files_correct = True
    for f in stdout.splitlines():
        if not utils.file_is_ignored(
            f, VALID_FILE_EXTENSIONS, IGNORED_FILES, IGNORED_FOLDERS
        ):
            all_files_correct &= file_is_correct(f)
    return all_files_correct


def group_lines(patchlines, starting_with):
    """Generator of (name, lines) almost the same as itertools.groupby

    This function's control flow is non-trivial. In particular, the clearing
    of the lines variable, marked with [1], is intentional and must come
    after the yield. That's because we must yield the (name, lines) tuple
    after we have found the name of the next section but before we assign the
    name and start collecting lines. Further, [2] is required to yeild the
    last block as there will not be a block start delimeter at the end of
    the stream.
    """
    lines = []
    name = None
    for line in patchlines:
        if line.startswith(starting_with):
            if name:
                yield name, lines
            name = line[len(starting_with) :]
            lines = []  # [1]
        else:
            lines.append(line)
    yield name, lines  # [2]


def group_files(commitlines):
    """Generator of (commit hash, lines) almost the same as itertools.groupby"""
    return group_lines(commitlines, "+++ b/")


def group_commits(commitlines):
    """Generator of (file name, lines) almost the same as itertools.groupby"""
    return group_lines(commitlines, "commit ")


def patch_is_correct(base_commit, end_commit):
    """Get the output of a git diff and analyse each modified file."""

    # Get patches of the affected commits with one line of context.
    gitlog = subprocess.run(
        [
            "git",
            "log",
            "--unified=1",
            "--pretty=commit %h",
            base_commit + ".." + end_commit,
        ],
        stdout=subprocess.PIPE,
    )

    if gitlog.returncode != 0:
        return False

    gitlines = gitlog.stdout.decode("utf-8", "replace").splitlines()
    all_files_correct = True
    for commit, comlines in group_commits(gitlines):
        for path, lines in group_files(comlines):
            all_files_correct &= inc_order_is_correct(
                include_paths(lines, diff_mode=True), path, commit
            )
    return all_files_correct


def parse_cmd_line(argv, prog_name):
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.RawTextHelpFormatter,
        description="Check alphabetical order of #includes",
        epilog="""
For each source file in the tree, checks that #include's C preprocessor
directives are ordered alphabetically (as mandated by the Trusted
Firmware coding style). System header includes must come before user
header includes.
""",
    )

    parser.add_argument(
        "--tree",
        "-t",
        help="Path to the source tree to check (default: %(default)s)",
        default=os.curdir,
    )
    parser.add_argument(
        "--patch",
        "-p",
        help="""
Patch mode.
Instead of checking all files in the source tree, the script will consider
only files that are modified by the latest patch(es).""",
        action="store_true",
    )
    parser.add_argument(
        "--from-ref",
        help="Base commit in patch mode (default: %(default)s)",
        default="origin/master",
    )
    parser.add_argument(
        "--to-ref",
        help="Final commit in patch mode (default: %(default)s)",
        default="HEAD",
    )
    args = parser.parse_args(argv)
    return args


if __name__ == "__main__":
    args = parse_cmd_line(sys.argv[1:], sys.argv[0])

    os.chdir(args.tree)

    if args.patch:
        print(
            "Checking files modified between patches "
            + args.from_ref
            + " and "
            + args.to_ref
            + "..."
        )
        if not patch_is_correct(args.from_ref, args.to_ref):
            sys.exit(1)
    else:
        print("Checking all files in directory '%s'..." % os.path.abspath(args.tree))
        if not directory_tree_is_correct():
            sys.exit(1)

    # All source code files are correct.
    sys.exit(0)
