#!/usr/bin/env python3
"""
Posts a verification to Gerrit verify-status plugin.
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


def check_plugins(base_url, auth):
    """
    Checks if the verify-status plugin is installed
    """
    plugin_url = "{}/a/plugins/".format(base_url)
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    try:
        request = requests.get(plugin_url, auth=auth, headers=headers)
    except requests.exceptions.RequestException as exception:
        print("Error checking plugins: {}".format(str(exception)), file=sys.stderr)
        sys.exit(0)
    if request.status_code != 200:
        print("Could not check if verify-status plugin is installed")
        return
    json_plugins = json.loads(request.text.replace(")]}'",""))
    if "verify-status" not in json_plugins:
        print("verify-status plugin not installed.")
        sys.exit(0)


def submit_verification(base_url, auth, changeset, patchset_revision, verify_details):
    """
    Handles the actual post request.
    """
    check_plugins(base_url, auth)
    post_data = {
        "verifications": {
            verify_details["verify_name"]: {
                "url": verify_details["job_url"],
                "value": verify_details["value"],
                "abstain": verify_details["abstain"],
                "reporter": verify_details["reporter"],
                "comment": verify_details["comment"],
                "category": verify_details["category"],
                "duration": verify_details["duration"],
            }
        }
    }
    submit_url = "{}/a/changes/{}/revisions/{}/verify-status~verifications".format(
        base_url, changeset, patchset_revision
    )
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    post = None
    try:
        post = requests.post(
            submit_url, data=json.dumps(post_data), auth=auth, headers=headers,
        )
    except requests.exceptions.RequestException as exception:
        print("Error posting to verify-status:", file=sys.stderr)
        print(str(exception), file=sys.stderr)
        sys.exit(0)
    if post.status_code == 204:
        print("Gerrit verify-status posted successfully.")
    else:
        print(
            "Error posting to verify-status: {}".format(post.status_code),
            file=sys.stderr,
        )
        print(post.text, file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Submits a job verification to verify-status plugin of Gerrit"
    )
    PARSER.add_argument("--host", help="Gerrit Host", default=os.getenv("GERRIT_HOST"))
    PARSER.add_argument("--job-url", help="Job URL.", default=os.getenv("BUILD_URL"))
    PARSER.add_argument("--value", help="Verification value.")
    PARSER.add_argument(
        "--changeset",
        help="Changeset in Gerrit to verify.",
        default=os.getenv("GERRIT_CHANGE_NUMBER"),
    )
    PARSER.add_argument(
        "--patchset-revision",
        help="Commit SHA of revision in Gerrit to verify.",
        default=os.getenv("GERRIT_PATCHSET_REVISION"),
    )
    PARSER.add_argument(
        "--verify-name", help="Name to give the job verifcation message."
    )
    PARSER.add_argument(
        "--user", help="Username to authenticate as.", default=os.getenv("VERIFY_USER")
    )
    PARSER.add_argument(
        "--password",
        help="Password or token to authenticate as. "
        "Defaults to VERIFY_PASSWORD environment variable.",
        default=os.getenv("VERIFY_PASSWORD"),
    )
    PARSER.add_argument(
        "--abstain",
        help="Whether this should affect the final voting value.",
        action="store_true",
    )
    PARSER.add_argument("--reporter", help="Metadata for reporter.", default="")
    PARSER.add_argument("--comment", help="Metadata for comment.", default="")
    PARSER.add_argument("--category", help="Metadata for category.", default="")
    PARSER.add_argument("--duration", help="Duration of the job.", default="")
    PARSER.add_argument("--protocol", help="Protocol to use.", default="https")
    PARSER.add_argument("--port", help="Port to use.", default=None)
    ARGS = PARSER.parse_args()
    submit_verification(
        "{}://{}{}".format(ARGS.protocol, ARGS.host, ":{}".format(ARGS.port) if ARGS.port else ""),
        (ARGS.user, ARGS.password),
        ARGS.changeset,
        ARGS.patchset_revision,
        {
            "verify_name": ARGS.verify_name,
            "job_url": ARGS.job_url,
            "value": int(ARGS.value),
            "abstain": bool(ARGS.abstain),
            "reporter": ARGS.reporter,
            "comment": ARGS.comment,
            "category": ARGS.category,
            "duration": ARGS.duration,
        },
    )
