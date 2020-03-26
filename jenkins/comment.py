#!/usr/bin/env python3
"""
Posts a comment to Gerrit.
"""

__copyright__ = """
/*
 * Copyright (c) 2020, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

import argparse
import json
import os
import sys
import requests


def submit_comment(base_url, auth, changeset, patchset_revision, comment):
    post_data = {"message": comment}
    comment_url = "{}/a/changes/{}/revisions/{}/review".format(
        base_url, changeset, patchset_revision
    )
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    post = None
    try:
        post = requests.post(
            comment_url, data=json.dumps(post_data), auth=auth, headers=headers,
        )
    except requests.exceptions.RequestException as exception:
        print("Error posting comment to Gerrit.")
        sys.exit(0)
    if post.status_code == 200:
        print("Posted comment to Gerrit successfully.")
    else:
        print(
            "Could not post comment to Gerrit. Error: {} {}".format(
                post.status_code, post.text
            )
        )


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Submits a comment to a Gerrit change")
    PARSER.add_argument("--host", help="Gerrit Host", default=os.getenv("GERRIT_HOST"))
    PARSER.add_argument(
        "--changeset",
        help="Changeset in Gerrit to comment on.",
        default=os.getenv("GERRIT_CHANGE_NUMBER"),
    )
    PARSER.add_argument(
        "--patchset-revision",
        help="Commit SHA of revision in Gerrit to comment on.",
        default=os.getenv("GERRIT_PATCHSET_REVISION"),
    )
    PARSER.add_argument(
        "--user", help="Username to authenticate as.", default=os.getenv("GERRIT_USER")
    )
    PARSER.add_argument(
        "--password",
        help="Password or token to authenticate as. "
        "Defaults to GERRIT_PASSWORD environment variable.",
        default=os.getenv("GERRIT_PASSWORD"),
    )
    PARSER.add_argument("--protocol", help="Protocol to use.", default="https")
    PARSER.add_argument("--port", help="Port to use.", default=None)
    PARSER.add_argument("--comment", help="Comment to send.")
    ARGS = PARSER.parse_args()
    submit_comment(
        "{}://{}{}".format(
            ARGS.protocol, ARGS.host, ":{}".format(ARGS.port) if ARGS.port else ""
        ),
        (ARGS.user, ARGS.password),
        ARGS.changeset,
        ARGS.patchset_revision,
        ARGS.comment,
    )
